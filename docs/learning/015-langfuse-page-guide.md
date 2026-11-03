# 15：读懂Langfuse的整张记录详情页

2026-11-03。依据：学习者提供的Langfuse US v4.73.0截图、课程trace_demo.py实际代码、服务器submission收据与官方文档。截图确认首条导入trace、步骤树、输入输出已显示；输出字典含依据一致性1、回答完整性0，顶部另可见回答完整性0的评分徽标。两个正式Score对象的全部详情仍需在Scores标签核对。未将含个人信息的原始截图上传学习仓库；讲义已准备不等于学习者已独立掌握。

## 这页正在展示什么

当前选择的是一条“导入已有评测”的记录，不是一次新的模型回答。脚本读取第13节保存的DeepEval判分，整理展示材料，把已有分数发送到Langfuse；本次没有调用DeepSeek，也没有运行Agent Desk的真实聊天、检索或工具任务。

因此页面能回答的是：这次导入记录叫什么、分了哪些步骤、登记了什么问题和答案、关联了哪些评分。它暂时不能回答之前DeepSeek实际推理耗时、实际检索是否命中、Agent有没有改对文件；这些需要在真实执行路径中加埋点。

## 顶部栏与记录编号

- Organization：组织，容纳项目及成员。
- My Project：当前项目的数据空间。看记录时要选对项目，不能把不同项目默认视为同一份数据。
- Hobby：当前套餐名称，不是模型名称。
- Traces：所在功能区域是过程记录。
- 页面顶部长串字符：Trace ID，即这条记录的唯一标识，不是API密钥。
- 日期时间：这条记录的时间；当前显示的是导入操作时间。
- 0.00s：本次导入span的短耗时被显示精度四舍五入，不表示原DeepSeek请求瞬间完成。

## 中间的树：每行是一个被记录的步骤

```text
learning-saved-evaluation-import  导入已有评测（根步骤）
├─ prepare-case-display           整理要展示的问题、资料和答案
└─ attach-existing-scores         关联已经存在的两项评分
```

点击不同节点，右侧显示那个节点的数据，不一定始终显示整条记录。当前根步骤的Input只有问题；资料和候选答案的整理结果可以去prepare-case-display节点看。attach-existing-scores记录关联了哪些评分名，以及本次新模型调用为0。

Trace是一组共享trace ID的工作记录；span/observation是其中一段工作，generation则可专门表示模型调用。本例只有普通span，没有假造历史generation。

Tree显示父子层级；Timeline按时间排列各步骤，适合看耗时和重叠；Graph显示关系图。三个是同一份记录的不同视图，不是三个模型；图也不能替代未采集的执行证据。

## 右侧：先读Preview，再读Scores

| 标签或字段 | 中文意思 | 这页应怎么看 |
|---|---|---|
| Preview | 概览 | 看当前节点的输入和输出 |
| Input | 输入 | 当前根步骤记录了用户问题：如何隔离不同项目的依赖？不是完整模型请求体 |
| Output | 输出 | 根步骤记录了旧候选答案和保存的分数字典；不是本轮新生成的答案 |
| answer | 回答正文 | 缺少相关资料，无法根据资料回答 |
| saved_scores | 输出中的一个数据字段 | 里面写着依据一致性1、回答完整性0；字段存在不等于两个Score对象都已核验 |
| Attributes | 属性 | 元数据，例如来源文件、来源哈希、记录类型和计时范围 |
| Scores | 正式评分记录 | 核对已关联的评分名称、分值和理由；与Preview里的普通输出字段分开看 |
| Log View | 日志式视图 | 用另一种呈现方式查看记录内容，初学可先使用Preview |
| Formatted | 格式化显示 | 把数据排成容易阅读的样子 |
| Raw | 原始数据 | 查看原始结构，排查字段时再用 |

绿色文字是显示高亮，不等于PASS。点击saved_scores左边的小箭头可展开其字段；这只是展开数据，不会重新评分。点击Scores标签读取已有分数也不等于运行模型裁判。

本节两个分数的意思：依据一致性1，答案没有编造；回答完整性0，没有提供用户要的方法。1/0由本节严格二值标准定义，不是概率，也不说明所有功能的好坏。分数来源是先前DeepSeek作为裁判的判分，Langfuse本次负责接收和展示。

## 左侧菜单完整中文对照

| 菜单 | 中文与用途 |
|---|---|
| Home | 总览，查看项目的记录数、分数等概况 |
| Dashboards | 自定义看板，把关心的数据做成汇总图 |
| Tracing | 执行记录，查某一次操作的步骤、输入输出和耗时；当前所在入口 |
| Sessions | 会话分组，把属于同一段对话或流程的多条trace串起来，需要程序关联会话ID |
| Users | 应用终端用户维度，按程序记录的user ID分析；不是管理Langfuse网站登录账号的页面 |
| Alerts | 告警，配置要关注的条件与通知；不是安装后自动知道所有问题 |
| Skills（Beta） | 管理Agent任务指引及相关文件的版本；Beta表示试验功能，不会自动同步Agent Desk本地技能 |
| Prompts | 存储、版本管理提示词；应用需实际读取或关联这些版本 |
| Playground | 交互式试验Prompt和模型；实际模型运行需要连接配置 |
| Scores | 查看已产生的评价结果，包括程序、人工或模型给出的分数 |
| Evaluators | 定义怎样评分以及何时执行；规则和评分结果是两类东西 |
| Human Annotation | 人工标注、复核，组织人来评答案 |
| Datasets | 测试题集，保存可重复测试的案例；不同于RAG检索资料库 |
| Experiments | 在固定数据集上运行应用或Prompt版本并比较结果；本例导入trace还不是数据集实验 |
| Upgrade Plan | 套餐升级入口 |
| Settings | 项目设置，包括项目API密钥等配置；登录密码不是项目API密钥 |
| Book a call | 预约官方咨询 |
| Support | 官方帮助与支持 |

Observability、Prompt Management、Evaluation是菜单分组标题，分别对应过程观测、提示/技能管理、评测。本课程先使用Tracing和Scores，再学习Datasets和Experiments，不要求一次学完所有入口。

## 实际怎样用：今天按这个顺序看

1. 点击根步骤learning-saved-evaluation-import，在Preview里把问题与答案对照看。
2. 点击prepare-case-display，找reference_documents，确认当前资料是“（无资料）”。这是固定样例的资料，不是实际检索日志。
3. 点击attach-existing-scores，看是否记录了两个评分名称，以及new_model_calls为0。
4. 回到根步骤点Scores，分别找到依据一致性、回答完整性和具体理由，核对正式评分记录。若只显示一项，检查筛选、层级和后台入库状态，不能把缺失当0分。
5. 需要换一条记录时，从左侧Tracing返回列表并按时间、名称等查找；重复查看不会重新发起DeepSeek请求，无须再执行--send。

将来给真实Agent Desk接入后，也按同样思路看：问题是什么、哪一步读取资料、传给模型什么、模型如何回应、工具有没有执行、最后结果是否满足要求。界面只展示程序记录到的信息，不能把模型说“已完成”当作文件已经改变。

## 右上角Chrome空间提示

这不是Langfuse评分结果。它提示本机存储不足，可能影响浏览器及扩展运行；先前本机磁盘检查也证实C盘空间不足。提示右上角×只关闭通知；大按钮进入网站数据清理流程，不是刷新评测或修复回答的按钮。网站数据清理和学习记录查看应分开处理。

## 接下来学习怎样串起来

一条失败记录 → 人工分析原因 → 加入测试集 → 修改应用或Prompt → 在相同测试集上跑新实验 → 对比结果。这才是Datasets和Experiments接下来要解决的问题；导入一条旧成绩只是第一步。

官方依据：[Trace/observation/session概念](https://langfuse.com/docs/observability/data-model)、[评分与数据集实验](https://langfuse.com/docs/evaluation/core-concepts)、[提示词和技能版本管理](https://langfuse.com/docs/prompt-and-skill-management/overview)。
