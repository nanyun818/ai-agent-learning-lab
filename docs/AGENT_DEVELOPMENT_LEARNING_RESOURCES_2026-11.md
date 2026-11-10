# GitHub Agent开发学习路线精选（2026-11-10）

目标：用课程补齐原理，以已有本地Agent Desk作为实践主线。本页为官方仓库、README和GitHub API核对后的资源选择，不表示课程已完成或代码已安装运行。stars为查询当日快照，仅作关注度参考。

## 六个经过核对的课程仓库

| 仓库 | 内容与定位 | 语言/运行取向 | 关注度快照 |
|---|---|---|---|
| [Datawhale Hello-Agents](https://github.com/datawhalechina/hello-agents) | 系统教程：经典Agent范式、自建框架、记忆与检索、上下文工程、协议、评测和综合项目 | 中文讲解，Python实践；优先主教材 | 86,598 stars |
| [Hugging Face Agents Course](https://github.com/huggingface/agents-course) | Agent基础、smolagents/LangGraph/LlamaIndex等框架、应用和最终benchmark作业 | 官方课程主体英文，Python；用作第二视角和作业参考 | 34,687 stars |
| [Microsoft AI Agents for Beginners](https://github.com/microsoft/ai-agents-for-beginners) | 分课讲解工具使用、Agentic RAG、规划、多Agent、部署等；当前仓库标示18课 | 有简体中文翻译；运行示例偏Microsoft Agent Framework/Foundry，部分需要Azure配置 | 79,341 stars |
| [LangChain Academy](https://github.com/langchain-ai/langchain-academy) | LangGraph循序渐进的Notebook模块，逐步学习Agent工作流并进入部署 | 英文，Python；工程化进阶 | 3,006 stars |
| [Agents From Scratch](https://github.com/langchain-ai/agents-from-scratch) | 以邮件助手逐步串起Agent基础、评测、人工介入和记忆，有notebooks、源码和tests | 英文，Python；完整小项目结构参考；默认服务配置需适配，不能承诺DeepSeek直接替换全部示例 | 2,443 stars |
| [Datawhale All-in-RAG](https://github.com/datawhalechina/all-in-rag) | 文档处理与分块、向量和索引、混合检索、查询优化、生成与评估 | 中文，Python；RAG专项，不是完整Agent通识课程 | 13,022 stars |

六个仓库查询时均未归档；推送日期不等同于课程质量或接口兼容保证。没有克隆大仓库、安装依赖、申请新服务或产生模型调用。

## 给当前学习者的选择

主教材选Hello-Agents，遇到检索问题查All-in-RAG，工作流进阶时选LangChain Academy。其余作为参考，不要求六套同时学完。

Hello-Agents可针对当前项目选择：

- 第4章“智能体经典范式构建”：理解ReAct、Plan-and-Solve、Reflection，以及模型、工具、反馈之间的循环。
- 第7章“构建你的Agent框架”：按需补充应用各层如何组织，不要求重写整个Agent Desk。
- 第8章“记忆与检索”与第9章“上下文工程”：对应项目检索漏召回、手工记忆和会话历史如何进入模型请求。
- 第12章“智能体性能评估”：对应固定业务任务、程序规则、模型裁判、人工复核和改动前后对照。
- 第10章“智能体通信协议”：对应项目MCP接入及工具调用；区分协议连接、权限审批和模型自主工具循环。

建议实践对应：

| 知识块 | Agent Desk中的学习证据 |
|---|---|
| Agent循环与工具 | 解释普通聊天和任务执行模式的边界，记录一次真实工具调用及反馈 |
| 检索与上下文 | 解释ad02为何漏掉pnpm资料，提出候选改进并在固定任务上复测 |
| 评测 | 继续将真实应用接入promptfoo，用Langfuse记录实际运行链路；不以读课程代替项目实验 |
| 记忆与持久化 | 区分单会话历史、手工记忆和自动记忆系统，分别验证新会话与重启行为 |
| 人工审批与工程化 | 分析需要审批的动作，在可检查的任务中核对实际产物和执行结果 |

这些课程多数用Python，而Agent Desk是Node/JavaScript应用。先学可迁移机制，再映射到自己的源码；不要求为了跟课更换应用技术栈。课程示例的模型、SDK、账户和版本需要逐个核对，不能认为任何OpenAI兼容接口都可覆盖所有功能。

每个知识块继续保留：自己的解释、对应源码位置、可复现的合成实验、结果与失败分析，以及GitHub提交。当前已验证的8任务基线见[Agent Desk首轮报告](../reports/agentdesk-first-baseline.md)。

官方课程入口：[Hello-Agents在线教材](https://datawhalechina.github.io/hello-agents/)、[Hugging Face课程](https://huggingface.co/learn/agents-course/)、[LangChain Academy](https://academy.langchain.com/)。以上仓库名称和课程概况直接取自各项目官方README；推荐顺序是结合当前学习进度作出的判断。
