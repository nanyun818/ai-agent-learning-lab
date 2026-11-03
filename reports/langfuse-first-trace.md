# Langfuse首条记录的网页核验

核验日期：2026-11-03。依据学习者提供的US区域Langfuse v4.73.0截图和服务器发送收据。未重新运行--send，未新发模型请求。

截图可见：

- 一条learning-saved-evaluation-import记录及其唯一标识。
- 根步骤与prepare-case-display、attach-existing-scores两个子步骤。
- 输入问题、旧候选答案及输出字典saved_scores。
- saved_scores中依据一致性1、回答完整性0；顶部另可见回答完整性0的评分徽标。

据此确认首条trace与输入输出已到达Cloud。不能仅凭输出字典断言两个正式Score对象的详情都已核验；需在根步骤Scores标签进一步查看评分名称、值与理由。原始截图含账号与项目标识，不上传公共学习仓库。

本次记录为导入已保存合成评测，非实时评分或Agent Desk真实任务。显示0.00s只对应导入处理，不代表先前DeepSeek响应速度。后续验证真实应用链路时须在执行时采集步骤、输入输出和实际证据。

当前教学：[第15节页面中文指南](../docs/learning/015-langfuse-page-guide.md)。
