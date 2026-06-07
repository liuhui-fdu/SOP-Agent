1. Phase 1 关键词搜索截图
建议用浏览器或 curl 截图这几个：
/v1/search?q=OOM
预期：返回 sop-001
/v1/search?q=故障
预期：返回多个 SOP
/v1/search?q=replication
预期：返回空
/v1/search?q=CDN
预期：返回 sop-003、sop-010
/v1/search?q=%26
预期：返回正文包含 & 的文档
另外可以补一张：
/v1/search?q=&
说明兼容 README 非标准写法。
2. Phase 2 语义搜索截图
浏览器打开或在 /v2 页面搜索：
服务器挂了
预期：sop-001、sop-004 靠前
黑客攻击
预期：sop-005 靠前
机器学习模型出问题
预期：sop-008 靠前
这三张很重要，直接对应 Phase 2 验收。
3. Phase 3 Agent 对话截图
在 /v3 页面依次问：
数据库主从延迟超过30秒怎么处理？
截图要看到：调用 readFile(sop-002.html)，并回答处理步骤。
服务 OOM 了怎么办？
截图要看到：调用 readFile(sop-001.html)。
P0 故障的响应流程是什么？
截图要看到：调用多个 SOP，或至少展示多个 readFile(...) 工具调用。
怀疑有人入侵了系统
截图要看到：调用 readFile(sop-005.html)。
推荐结果质量下降了
截图要看到：调用 readFile(sop-008.html)。
4. 自动化验证截图
最后截终端：
make verify
最好能看到：
PASS
reports/verification.md
reports/verification.txt
再截：
make coverage-test2
要看到覆盖率：
coverage >= 80%