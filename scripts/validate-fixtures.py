#!/usr/bin/env python3
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]; S=ROOT/'schemas/v0.1'; F=ROOT/'fixtures/v0.1'
ALGORITHM_ID='refetch.rank.baseline.v0.1'
Q=Decimal('0.000001')

def load(p):
    with open(p, encoding='utf-8') as f: return json.load(f)
schemas={p.name:load(p) for p in S.glob('*.schema.json')}
registry=Registry()
for p in S.glob('*.schema.json'):
    schema=load(p); res=Resource.from_contents(schema)
    registry=registry.with_resource(schema['$id'], res).with_resource(p.name, res)
validators={name:Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()) for name,schema in schemas.items()}

def assert_precision(x, label):
    if -num(x).as_tuple().exponent > 6:
        raise ValueError(f'{label}Precision')

def rounded(x):
    d=Decimal(str(x)).quantize(Q, rounding=ROUND_HALF_UP)
    return Decimal('0') if d == 0 else d

def num(x): return Decimal(str(x))

def schema_check(name,obj):
    errs=list(validators[name].iter_errors(obj))
    if errs: raise AssertionError('; '.join(e.message for e in errs[:3]))

def names_unique(items, err):
    names=[s['name'] for s in items]
    if len(names)!=len(set(names)): raise ValueError(err)

def evidence_ids(req, cid):
    ids=set()
    for c in req['candidates']:
        if c['id']==cid: ids.update(e['id'] for e in c['evidence'])
    for a in req['analysis']:
        if a['candidateId']==cid: ids.update(e['id'] for e in a['evidence'])
    return ids

def semantic(req):
    schema_check('rank-request.schema.json',req)
    cids=[c['id'] for c in req['candidates']]
    if len(cids)!=len(set(cids)): raise ValueError('duplicateCandidateId')
    aids=[a['id'] for a in req['analysis']]
    if len(aids)!=len(set(aids)): raise ValueError('duplicateAnalysisId')
    seen_ev=[]
    for c in req['candidates']:
        names_unique(c['signals'],'duplicateCandidateSignalName')
        for s in c['signals']: assert_precision(s['value'], 'signalValue')
        if any(not s['name'].startswith('source.') for s in c['signals']): raise ValueError('invalidCandidateSignalNamespace')
        seen_ev += [e['id'] for e in c['evidence']]
    for a in req['analysis']:
        names_unique(a['signals'],'duplicateAnalysisSignalName')
        for s in a['signals']: assert_precision(s['value'], 'signalValue')
        if any(not s['name'].startswith('analysis.') for s in a['signals']): raise ValueError('invalidAnalysisSignalNamespace')
        seen_ev += [e['id'] for e in a['evidence']]
    for w in req['lens']['weights'].values(): assert_precision(w, 'weight')
    if len(seen_ev)!=len(set(seen_ev)): raise ValueError('duplicateEvidenceId')
    ac=[a['candidateId'] for a in req['analysis']]
    if set(ac)!=set(cids): raise ValueError('analysisCandidateMissing')
    if len(ac)!=len(set(ac)): raise ValueError('duplicateAnalysisForCandidate')
    for c in req['candidates']:
        ev=evidence_ids(req,c['id'])
        for s in c['signals']:
            if not set(s['evidenceRefs']) <= ev: raise ValueError('danglingEvidenceRef')
    for a in req['analysis']:
        ev=evidence_ids(req,a['candidateId'])
        for s in a['signals']:
            if not set(s['evidenceRefs']) <= ev: raise ValueError('danglingEvidenceRef')
        cl=a.get('clusterAssignment')
        if cl and not set(cl['evidenceRefs']) <= ev: raise ValueError('danglingEvidenceRef')

def expected_slate(req):
    semantic(req)
    weights=req['lens']['weights']; allowed=set(req['lens'].get('allowedSourceTypes',[]))
    max_items=req['lens']['policy']['maxItems']; max_pc=req['lens']['policy']['maxPerCluster']
    amap={a['candidateId']:a for a in req['analysis']}; rows=[]
    for c in req['candidates']:
        if allowed and c['source']['type'] not in allowed: continue
        a=amap[c['id']]; reasons=[]; total=Decimal('0')
        for s in c['signals'] + a['signals']:
            if s['name'] not in weights: continue
            contribution=rounded(num(s['value']) * num(weights[s['name']]))
            if contribution != 0:
                reasons.append({'signal':s['name'],'value':s['value'],'weight':weights[s['name']],'contribution':float(contribution),'evidenceRefs':s['evidenceRefs']})
                total += contribution
        cl=a.get('clusterAssignment'); key=f"{cl['namespace']}:{cl['id']}" if cl else None
        rows.append((c, float(rounded(total)), reasons, key))
    rows.sort(key=lambda r:(-r[1], r[0]['id']))
    items=[]; cluster_counts={}; suppressed=0
    for c,score,reasons,key in rows:
        if key and cluster_counts.get(key,0) >= max_pc:
            suppressed += 1; continue
        if key: cluster_counts[key]=cluster_counts.get(key,0)+1
        items.append({'candidateId':c['id'],'decision':{'rank':len(items)+1,'score':score,'reasons':reasons}})
        if len(items) >= max_items: break
    by_id={c['id']:c for c in req['candidates']}; cov={}; clusters={}; un=0
    for it in items:
        c=by_id[it['candidateId']]; cov[c['source']['type']]=cov.get(c['source']['type'],0)+1
        cl=amap[c['id']].get('clusterAssignment')
        if cl:
            k=f"{cl['namespace']}:{cl['id']}"; clusters[k]=clusters.get(k,0)+1
        else: un += 1
    return {'specVersion':'v0.1','requestId':req['id'],'lensId':req['lens']['id'],'generatedAt':req['context']['generatedAt'],'algorithmId':ALGORITHM_ID,'items':items,'coverage':{'bySourceType':cov},'diversity':{'clustersSelected':clusters,'unclusteredSelected':un,'suppressedByClusterLimit':suppressed}}

def validate_expected(req, slate):
    schema_check('feed-slate.schema.json',slate)
    if slate != expected_slate(req):
        exp=expected_slate(req)
        if slate.get('coverage') != exp.get('coverage'): raise AssertionError('coverageMismatch')
        if slate.get('diversity') != exp.get('diversity'): raise AssertionError('diversityMismatch')
        if [i.get('candidateId') for i in slate.get('items',[])] != [i['candidateId'] for i in exp['items']]: raise AssertionError('candidateOrderingMismatch')
        raise AssertionError('expectedScoreMismatch')

def pool_signature(req):
    clone={k:req[k] for k in ['candidates','analysis']}
    return json.dumps(clone, sort_keys=True)

def main():
    for name in schemas: Draft202012Validator.check_schema(schemas[name])
    orders=[]; sig=None
    for p in sorted((F/'valid').glob('*.rank-request.json')):
        req=load(p); semantic(req)
        ps=pool_signature(req)
        if sig is None: sig=ps
        elif sig != ps: raise AssertionError('valid fixtures must share candidate and analysis pool')
        exp=F/'expected'/p.name.replace('.rank-request.json','.feed-slate.json')
        if not exp.exists(): raise AssertionError(f'missing expected {exp}')
        slate=load(exp); validate_expected(req, slate)
        orders.append(tuple(i['candidateId'] for i in slate['items']))
    if len(set(orders)) < 3: raise AssertionError('three Lens outputs must differ')
    for p in sorted((F/'invalid').glob('*.json')):
        wrapper=load(p); expected=wrapper['expectedError']; req=wrapper['request']; slate=wrapper.get('slate')
        try:
            if slate is None: semantic(req)
            else: validate_expected(req, slate)
        except Exception as e:
            if expected!='schema' and expected not in str(e): raise AssertionError(f'{p}: expected {expected}, got {e}')
        else:
            raise AssertionError(f'{p}: unexpectedly valid')
    print('validated schemas, semantic fixtures, recomputed expected outputs, references, metrics, and lens differences')
if __name__=='__main__': main()
