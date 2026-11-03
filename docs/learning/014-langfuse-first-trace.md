# 14：Langfuse把一次过程和分数联系起来

2026-11-03。状态：SDK与导入脚本已准备；真实SDK的内存导出、4项离线检查通过；学习者需要先注册Langfuse Cloud、创建项目和配置项目凭据，云端实际可见性待验证。本节没有新调用模型，也未改动Agent Desk源码。

## 上一节真实结果

已只读核验dimensions-20261101T060402Z-2646f0c4.json。j05依据一致性1分、回答完整性0分，有效维度判分2/2、与助教建议2/2一致、原始请求尝试2次。理由分别是诚实说明资料不足，以及没有给出隔离项目依赖的方法。见[脱敏报告](../../reports/deepeval-two-metrics.json)。标签仍是助教建议，不是独立专家标注。

## 为什么现在学Langfuse

之前得到的结果是“通过或不通过”。要定位真实应用问题，还需要知道资料检索、模型调用、工具调用等各步发生了什么。Langfuse通过埋点收集程序实际记录的数据，再将过程、输入输出和评分关联展示；没有埋点的内部步骤不会自动被看见。

| 名词 | 中文理解 | 本节 |
|---|---|---|
| Trace | 一次工作过程的记录 | 本次导入已有评测 |
| Span / observation | 过程中的一段工作 | 整理展示材料、附加分数 |
| Score | 对这次过程或某一步的评价 | 从旧报告读到的依据1、完整性0 |

Langfuse也有评测功能，本节先练记录与关联，不把它仅理解为画图工具。DeepEval产生的成绩需要程序显式传给Langfuse，不会因为同时安装就自动同步。promptfoo网页仍独立存在。

## 第一个实验的边界

今天先将既有公开合成案例的两个分数送到Cloud，不重复批改：

```text
learning-saved-evaluation-import（导入已有评测）
├─ prepare-case-display（整理展示材料）
└─ attach-existing-scores（附加已有分数）
   ├─ 依据一致性：1
   └─ 回答完整性：0
```

前三项是span，两个分数是关联到根trace的score，不是额外两个span。SDK真实记录的是这次导入操作，不能据其毫秒耗时说之前DeepSeek很快；没有创建伪造的generation或补填旧模型时间。本例不是实时观测原始评分，更不是已完成Agent Desk全链路接入。下一阶段才把埋点放到真实请求周围，记录模型输入、输出、用量、失败和执行耗时。

## 注册和创建项目

1. 打开[Langfuse Cloud](https://cloud.langfuse.com/)注册并登录。本课程示例使用EU站点，地址为https://cloud.langfuse.com；如果选择其他区域，BASE_URL必须与该区域一致。
2. 按界面创建Organization（组织）和Project（项目），项目可命名agent-desk-learning。
3. 进入项目的Settings → API Keys，创建项目密钥对。Public Key是项目公钥，Secret Key用于鉴权。这两项属于Langfuse，和DeepSeek模型密钥不同；本次无需把DeepSeek密钥配置到Langfuse。
4. 选择并使用项目级密钥，不使用组织级密钥；本脚本auth_check会读取当前项目信息，初学例子可使用新学习项目的默认权限。凭据只在自己的终端输入，不作为课程文件发布。

## 准备服务器环境

使用私人启动指南SSH连接服务器，再执行：

```bash
cd /home/ubuntu/ai-learning-lab/evals/langfuse
source .venv/bin/activate
python trace_demo.py --preview
```

服务器已经安装SDK，不需要重装。preview读取旧报告并显示两个实测分数，不上传。

推荐初学方式：直接执行`python trace_demo.py --send`。在SSH交互终端中，如果尚未设置环境变量，程序会依次询问区域根地址、Public Key、Secret Key；EU区域地址直接回车即可。密钥输入不显示、不写文件，仅用于本次进程。它们是Langfuse项目密钥，不是DeepSeek密钥。

也可选择下面的环境变量方式。每条read命令分别执行；粘贴相应值并回车后，才执行下一段命令，避免后面的命令被当作输入内容。

```bash
read -rsp '输入 Langfuse Public Key 后回车：' LANGFUSE_PUBLIC_KEY
```

```bash
export LANGFUSE_PUBLIC_KEY
```

```bash
read -rsp '输入 Langfuse Secret Key 后回车：' LANGFUSE_SECRET_KEY
```

```bash
export LANGFUSE_SECRET_KEY
export LANGFUSE_BASE_URL='https://cloud.langfuse.com'
python trace_demo.py --send
```

如果注册的是US或Japan区域，应使用该项目设置中显示的区域根地址，本例允许官方Cloud区域，不连接任意第三方端点。查看网页需要浏览器登录正确组织和项目，不需要15500端口或SSH网页隧道；SSH在这里用于运行服务器上的脚本。

## 网页怎样看

程序会打印Trace ID和可用时的查看链接。到项目的Tracing/Traces记录列表，找learning-saved-evaluation-import；若名称或布局有调整，用Trace ID定位。

点开后先看问题、答案和两项中文score，再展开两个子步骤。本例预期显示依据一致性1、回答完整性0；这些来自旧报告，不是Langfuse再次评分。发送是异步的，flush不等于网页已经可见；必须看到trace及两个score后才确认接入。SDK返回的链接只是定位信息，不是入库成功证明。暂未出现时先检查区域、项目、鉴权、导出日志与队列，不要重跑付费评分。

## 版本和资源选择

2026-11-03检查服务器总内存约3.7GB、可用约1.2GB，未发现Docker；官方自托管VM建议至少4核16GiB内存。本节使用Cloud，不在既有服务器运行整套多容器平台。

当前PyPI最新Python SDK5.1.0要求Python>=3.11，而课程服务器是Python3.10。本例固定langfuse==4.7.0（要求>=3.10），按其已安装的start_as_current_observation、create_score、flush和auth_check接口验证，没有直接套用新SDK的所有低层API。安装在evals/langfuse/.venv，不改变DeepEval独立环境。

## 验收与留痕

已完成：真实SDK的3个span在内存中形成父子关系、两次score调用引用同一trace ID；无效结果被阻止；非交互环境缺密钥在本地报错；交互隐藏输入的模拟值不写入环境或文件。共4项离线检查通过，没有使用Cloud凭据、没有外部上传。待完成：学习者注册、项目配置、真实--send、网页可见性与自己的解释。原始数据库、生产聊天、服务凭据不发布。

代码：[trace_demo.py](../../evals/langfuse/trace_demo.py)、[离线SDK验证](../../evals/langfuse/test_trace_demo.py)。

官方依据：[Tracing入门](https://langfuse.com/docs/observability/get-started)、[API keys位置](https://langfuse.com/faq/all/where-are-langfuse-api-keys)、[分数关联API/SDK](https://langfuse.com/docs/evaluation/evaluation-methods/scores-via-sdk)、[自托管VM建议](https://langfuse.com/self-hosting/deployment/docker-compose)、[SDK版本与兼容](https://langfuse.com/docs/observability/sdk/overview)。
