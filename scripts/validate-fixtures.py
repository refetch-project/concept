#!/usr/bin/env python3
import json, sys
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource
ROOT=Path(__file__).resolve().parents[1]; S=ROOT/'schemas/v0.1'; F=ROOT/'fixtures/v0.1'

def load(p):
    with open(p, encoding='utf-8') as f: return json.load(f)
schemas={p.name:load(p) for p in S.glob('*.schema.json')}
registry=Registry()
for p in S.glob('*.schema.json'):
    schema=load(p); res=Resource.from_contents(schema)
    registry=registry.with_resource(schema['$id'], res).with_resource(p.name, res)
validators={name:Draft202012Validator(schema, registry=registry, format_checker=FormatChecker()) for name,schema in schemas.items()}

def schema_check(name,obj):
    errs=list(validators[name].iter_errors(obj))
    if errs: raise AssertionError('; '.join(e.message for e in errs[:3]))

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
    for c in req['candidates']: seen_ev += [e['id'] for e in c['evidence']]
    for a in req['analysis']: seen_ev += [e['id'] for e in a['evidence']]
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
        for cl in a.get('clusterAssignments',[]):
            if not set(cl['evidenceRefs']) <= ev: raise ValueError('danglingEvidenceRef')

def main():
    for name in schemas: Draft202012Validator.check_schema(schemas[name])
    orders=[]
    for p in sorted((F/'valid').glob('*.rank-request.json')):
        req=load(p); semantic(req)
        exp=F/'expected'/p.name.replace('.rank-request.json','.feed-slate.json')
        if not exp.exists(): raise AssertionError(f'missing expected {exp}')
        slate=load(exp); schema_check('feed-slate.schema.json',slate)
        if slate['generatedAt'] != req['context']['generatedAt']: raise AssertionError(f'{exp}: generatedAt mismatch')
        orders.append(tuple(i['candidateId'] for i in slate['items']))
    if len(set(orders)) < 3: raise AssertionError('three Lens outputs must differ')
    for p in sorted((F/'invalid').glob('*.json')):
        wrapper=load(p); expected=wrapper['expectedError']; req=wrapper['request']
        try:
            semantic(req)
        except Exception as e:
            if expected!='schema' and expected not in str(e): raise AssertionError(f'{p}: expected {expected}, got {e}')
        else:
            raise AssertionError(f'{p}: unexpectedly valid')
    print('validated schemas, fixtures, references, expected outputs, and lens differences')
if __name__=='__main__': main()
