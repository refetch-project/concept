# Refetch Concept

Refetch Concept 是 Refetch 的语言无关规范源。它定义术语、RFC、JSON Schema 和一致性 fixtures，帮助不同实现生成可解释的 `FeedSlate`。

Rust 参考实现位于 [`refetch-project/core-rust`](https://github.com/refetch-project/core-rust)。Rust struct 是本仓库 Schema 与 fixtures 的 binding，不是反向定义规范的来源。

> **项目阶段：** Foundation v0.1.1。v0.1 契约是一个草案状态的、可执行的确定性 feed 排序与列表选择规范。

## Refetch 能带来什么

Refetch 让同一批信息可以根据用户当前主动选择的 **Lens** 重新组织。

| Lens | 优先呈现的内容 |
| --- | --- |
| 生产可用 | 稳定发布、迁移说明、运行风险、兼容性 |
| 前沿观察 | 新技术、不寻常实验、早期研究信号 |
| 维护分诊 | 回归、安全修复、依赖变化、高影响 issue |

例如，同一条 GitHub Release 和一篇 RSS 文章都可以表示为 `FeedCandidate`。在“生产可用”Lens 下，Release 可能因为稳定采用和迁移证据排在前面；在“前沿观察”Lens 下，RSS 文章可能因为新颖性和技术讨论信号排在前面。来源材料保持一致，改变的是当前任务视角和解释方式。

## 仓库边界

本仓库包含：

- 共享术语：[`docs/terminology.md`](docs/terminology.md)。
- 语义信息流草案规则：[`rfcs/0001-semantic-feed.md`](rfcs/0001-semantic-feed.md)。
- 版本化 JSON Schema：[`schemas/v0.1/`](schemas/v0.1/)。
- 一致性 fixtures：[`fixtures/v0.1/`](fixtures/v0.1/)。
- 机械验证脚本：[`scripts/validate-fixtures.py`](scripts/validate-fixtures.py)。
- 维护者记录：[`docs/maintainers/`](docs/maintainers/)。

[`core-rust`](https://github.com/refetch-project/core-rust) 包含确定性的 Rust 参考实现、CLI 和 Rust 契约 binding。其他实现应绑定本仓库 Schema 并通过这里的 fixtures，而不是复制 Rust 专属假设。

## 契约形态

```text
FeedSlate = Select(Rank(Candidates, LensProfile, Policy, Context))
```

v0.1 流程保持小而可测：

```text
validate
→ eligibility/filtering
→ feature contributions
→ deterministic ordering
→ cluster-constrained selection
→ typed slate metrics
```

所有影响分数的 `Signal` 都必须携带显式 `evidenceRefs`。每个非零贡献都会生成结构化 `RankingReason`。`FeedSlate.generatedAt` 来自 `RankRequest.context.generatedAt`，因此实现排序时不得读取系统时钟。

## 验证可执行规范

安装 Python 依赖并运行 fixture 检查：

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validate-fixtures.py
```

验证脚本会检查 Schema、本地 `$ref` 解析、valid 与 invalid fixtures、引用关系、expected `FeedSlate` 输出，以及三个 Lens 示例之间是否存在可观察差异。

## 参与方式

适合的贡献包括：

- 带候选数据、证据和期望解释的真实信息流场景。
- 对 RFC、Schema 和 fixture 语义的评审。
- 能暴露契约歧义的新一致性 fixtures。
- 来自 Rust、TypeScript、Dart 或其他 binding 的实现反馈。

请将产品限制、失败分析和内部维护讨论放在 RFC 或 maintainer 文档中，而不是堆积在 README 主叙事里。
