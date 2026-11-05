# Agent Desk 本地项目评测

这轮评测的对象是电脑上的 Agent Desk 源码后端，不要求先把应用上传 GitHub。学习仓库只保存评测程序、虚构资料、结果和讲义。不要复制实际用户数据库或服务商配置。

## 实际测到的链路

HTTP创建资料/会话 → Agent Desk自身FTS检索和手工记忆 → 拼接上下文 → 真实DeepSeek生成 → SSE返回 → SQLite保存。

应用的 `createApp`、`createStore` 都从 `--source` 指向的本地目录直接导入。应用已有 `node_modules` 和 Node >=24 是前提；评测脚本没有额外npm依赖，不重建Electron，不修改应用源码。

独立临时数据库只包含 cases.json 中的虚构项目。模型请求经过本机临时网关，以便记录实际messages并将输出上限设为512、thinking设为disabled、temperature设为0；这是评测配置覆盖，不是桌面版原样默认配置。网关只转发至官方DeepSeek地址，不生成模拟答案，不重试，正常全量8任务9次请求。没有模型裁判调用。临时应用/网关在结束时关闭，脚本只清理自己创建且路径经验证的临时数据库。

## 运行

PowerShell中把环境变量设为实际源码位置（占位路径需要替换）：

```powershell
$env:AGENT_DESK_SOURCE = '你的Agent Desk源码目录'
node run.mjs
node run.mjs --check
node --test test_grading.mjs
```

默认仅预览题目，`--check`使用真实后端做检索和授权预检，两者均不请求模型。预检PASS只指检索/隔离规则，不表示回答、历史或记忆已通过生成测试。

在当前终端已有 `DEEPSEEK_API_KEY` 时：

```powershell
node run.mjs --run
node run.mjs --run --case ad02
```

全量正常9次生成；单独ad02正常1次；ad06两轮正常2次；单独ad07会先跑ad06以建立另一会话，正常3次。错误停止后续任务，不将API错误当成回答质量0分。不调用CLI引擎，不读取其他应用凭据，密钥只从当前进程环境读取并保留在内存。

`review.mjs result.json`只在已有答案上重新计算引用标识检查，不请求模型。它会更新该结果文件，并记录离线复评说明。需要保留原版时先复制。

## 怎么解释结果

- `rule_pass`：当前任务的明确检查是否全部通过，属于规则初筛。
- `reference_documents`：通过真实应用检索/记忆接口得到的资料。
- `requests.messages`：真实传给生成模型的消息，不含鉴权头。
- `usage`：该任务最后一轮的服务商用量；多轮任务不是整个任务的累计用量，不可直接相加当作批次总费用。
- 引用检查能发现编造ID，不证明资料语义上支持每句话；拒答正则也不能替代人工或校准后的模型裁判。
- 没有新建Langfuse trace，没有自动写入promptfoo历史；JSON/中文报告是本轮结果入口。

首轮：[实测报告](../../reports/agentdesk-first-baseline.md)、[原始合成实验结果](../../reports/agentdesk-first-baseline.json)、[第16节原理](../../docs/learning/016-agentdesk-project-evaluation.md)。

## 范围与可复现限制

测试的是本地修改后的源码快照。报告记录Git提交、dirty状态及5个关键源文件SHA256；未提交的其他依赖源码也会影响结果，这些哈希不是完整源代码归档。另一个人只克隆公开Agent Desk旧提交，未必能得到相同结果。不是已安装Electron包或桌面点击流程的验收，不含任务执行、MCP工具完成率或安全认证。

8道题是AI协助编写的小型开发集，已经用来发现问题，不是独立测试集或行业基准。学习者人工复核尚待完成。下一步围绕ad02提出检索修改，在固定题目上复测，再增加未参与改动的新问法。
