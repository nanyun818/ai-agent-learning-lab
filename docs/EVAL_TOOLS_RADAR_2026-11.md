# 开源评测工具选型记录（2026-11-05）

这是官方仓库与文档核对后的选型笔记，不代表已经安装、接入或完成这些项目。GitHub stars只反映关注度的一部分，不等于质量或企业采用率。

| 项目 | 本次GitHub API快照 | 定位 | 对Agent Desk的应用建议 |
|---|---|---|---|
| [Opik](https://github.com/comet-ml/opik) | 23,181 stars；最近推送2026-11-05；Apache-2.0 | tracing、数据集、自动评测及仪表板 | 可作为Langfuse同类方案比较；当前已有Langfuse账号，暂不换平台 |
| [OpenJudge](https://github.com/agentscope-ai/OpenJudge) | 1,052 stars；最近推送2026-11-03；Apache-2.0 | 可定制评分器、场景评分标准生成，覆盖工具、记忆和轨迹 | 适合在已有实际输出上比较评分器，特别关注编造引用和任务完整性；生成的标准仍需人工复核 |
| [AgentEvals（LangChain团队）](https://github.com/langchain-ai/agentevals) | 757 stars；最近推送2026-07-14；MIT | Agent中间轨迹的规则匹配和模型评分；Python/TypeScript | 适合Node/JS应用，将真实工具调用序列接入，检查工具选择、顺序及多余步骤；社区规模较小，不能称为当前最热门 |
| [Harbor](https://github.com/harbor-framework/harbor) | 6,793 stars；最近推送2026-11-05；Apache-2.0 | Terminal-Bench团队的沙箱Agent任务运行与评测框架 | 更适合后续评测任务执行模式：完成文件任务、运行测试、检查实际产物；需要环境和Agent适配 |
| [EvalScope](https://github.com/modelscope/evalscope) | 3,650 stars；最近推送2026-11-05；Apache-2.0 | ModelScope模型评测、性能基准与Agent评测 | 中文文档适合扩展学习；用于模型选型、标准任务与性能测试，不替代应用业务任务集 |

## 如何加入当前学习

继续原主线：promptfoo直接运行本地Agent Desk固定任务集 → Langfuse记录真实检索/生成与评分 → 修改检索并做相同题目对照。框架与平台都需要适配真实应用的数据，不会自动知道软件的所有功能。

新增候选：进入任务执行评测时，用AgentEvals检查轨迹；有沙箱任务需求时，考虑Harbor。OpenJudge可以与DeepEval在同一批答案上做小规模评分器比较。Opik先作为平台选型对照，EvalScope作为模型/基准拓展，不把五个都塞进两周必修。

## 三种不同对象

1. 平台：保存、查看、组织实验，如Langfuse和Opik。
2. 评分框架/评分器库：按规则或模型判断结果与轨迹，如DeepEval、OpenJudge、AgentEvals。
3. 任务运行环境与任务集：让Agent在可检查的环境里做事，如Harbor；具体benchmark的任务、环境、评分标准仍需核对。

这些能力会重叠，不是互斥分类。

官方依据：[Opik README](https://github.com/comet-ml/opik)、[OpenJudge README与Agent评分器](https://github.com/agentscope-ai/OpenJudge)、[AgentEvals规则/模型轨迹评分](https://github.com/langchain-ai/agentevals)、[Harbor项目与文档入口](https://www.harborframework.com/)、[EvalScope Agent参数](https://github.com/modelscope/evalscope/blob/main/docs/en/get_started/parameters.md)。元数据来源为各仓库GitHub REST API，查询日期2026-11-05；后续会变化。
