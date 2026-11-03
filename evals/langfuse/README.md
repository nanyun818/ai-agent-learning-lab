# Langfuse第一步：导入已有评分

2026-11-03状态：SDK安装、真实SDK内存导出与4项离线检查通过；学习者尚需注册Cloud、创建项目并在自己的服务器终端输入项目密钥。尚未核验云端接入。

服务器Python3.10，固定langfuse==4.7.0并按已安装包核对接口。当前最新Python SDK5.1.0要求Python>=3.11，因此本节没有直接升级原Python。依赖装在本目录独立.venv内；完整Langfuse平台没有部署在现有服务器。

首次在新环境安装：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

课程服务器已经装好，直接：

```bash
source .venv/bin/activate
python trace_demo.py --preview
```

预览只读取兄弟目录deepeval/results的最新dimensions-*.json与promptfoo/judge-cases.json，提取j05两个有效判分。它不调用模型、不读取生产对话、不上传。

注册并创建Cloud项目后，执行：

```bash
python trace_demo.py --send
```

在SSH交互终端中，程序会询问区域地址（默认EU）和两个项目密钥，密钥隐藏输入且不写入文件。也支持预设LANGFUSE_PUBLIC_KEY、LANGFUSE_SECRET_KEY、LANGFUSE_BASE_URL环境变量；非交互模式不会询问缺失值。

--send才连接Cloud，发起鉴权检查，创建一次“导入已有评测”的trace与两个score，并flush。没有DeepSeek请求。网页出现记录和分数后才算云端接入已核验；SDK调用返回和本地submission收据仅说明已尝试发送。

创建的都是普通span，没有伪造历史generation、模型耗时或token统计。span耗时仅表示导入工作，评分理由来自此前真实DeepEval结果；再次--send会新增另一条导入记录。

离线开发验证：

```bash
python -m unittest -v test_trace_demo
```

真实Langfuse SDK用InMemorySpanExporter输出到内存，create_score在测试中替换成记录调用的mock，因此不使用Cloud凭据、不连接外网。检查3个span同属一条trace、两项分数引用同一trace ID、无效/错误评分被拒绝，以及缺少凭据在本地报错。

详细注册、隐藏输入、网页读法见[第14节](../../docs/learning/014-langfuse-first-trace.md)。
