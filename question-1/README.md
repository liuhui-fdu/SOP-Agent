# 编程面试：On-Call 助手

## 概述

构建一个 On-Call 助手 Web 应用。`data/` 目录下有 100 份部门 On-Call SOP 的 HTML 文档（demo 提供 10 份）。

- 编程语言不限
- 可以使用任何 AI 工具辅助
- 需要实现 HTTP API + 前端页面
- 本题分为三个阶段，每阶段实现为独立的路由前缀（`/v1`、`/v2`、`/v3`）
- 建议按顺序完成，每阶段只有完整实现才得分

| 阶段                       | 分值 |
| -------------------------- | ---- |
| Phase 1：搜索引擎          | 30   |
| Phase 2：语义搜索          | 30   |
| Phase 3：On-Call 助手 Agent | 40   |

---

## 测试数据

| 文件           | 部门       | 关键内容                                     |
| -------------- | ---------- | -------------------------------------------- |
| `sop-001.html` | 后端服务   | OOM 排查、服务超时、降级策略、故障分级       |
| `sop-002.html` | 数据库 DBA | 主从延迟、慢查询、连接池满、数据恢复         |
| `sop-003.html` | 前端       | 页面白屏、CDN 资源加载失败、兼容性、性能劣化 |
| `sop-004.html` | SRE        | K8s 集群问题、监控告警、容量规划、故障响应   |
| `sop-005.html` | 安全团队   | 安全事件分级、入侵检测、漏洞响应             |
| `sop-006.html` | 数据平台   | 数据管道故障、ETL 失败、Spark 集群           |
| `sop-007.html` | 移动端     | App 崩溃率、热修复、推送服务                 |
| `sop-008.html` | AI & 算法  | 模型推理延迟、推荐质量下降、GPU 集群         |
| `sop-009.html` | QA         | 测试环境故障、自动化测试、发版卡点           |
| `sop-010.html` | 网络 & CDN | CDN 节点故障、DNS 异常、DDoS 防护            |

---

## Phase 1：搜索引擎

### API

```text
POST /v1/documents
{ "id": "sop-001", "html": "<html>...</html>" }
→ 201 { "id": "sop-001", "title": "后端服务 On-Call SOP" }

GET /v1/search?q={query}
→ 200 { "query": "...", "results": [{ "id": "...", "title": "...", "snippet": "...", "score": 1.0 }] }

GET /v1
→ 搜索页面（输入框 + 结果列表，前端不做要求）
```

### 要求

1. 实现基于关键词的文档检索

### 验证

| 查询                          | 期望结果                                |
| ----------------------------- | --------------------------------------- |
| `GET /v1/search?q=OOM`        | 返回 sop-001                            |
| `GET /v1/search?q=故障`       | 返回多个文档（大部分 SOP 都包含"故障"） |
| `GET /v1/search?q=replication` | 返回空（该词仅出现在 script 标签内）    |
| `GET /v1/search?q=CDN`        | 返回 sop-003, sop-010                   |
| `GET /v1/search?q=&`          | 返回正文中包含 & 字符的文档             |

---

## Phase 2：语义搜索

### API

```text
GET /v2/search?q={query}
→ 200 { "query": "...", "results": [{ "id": "...", "title": "...", "snippet": "...", "score": 0.87 }] }

GET /v2
→ 搜索页面（前端不做要求）
```

### 要求

1. 实现语义搜索，查询词不需要在文档中精确出现
2. 结果按相关性排序

### 验证

| 查询                            | 期望结果                              |
| ------------------------------- | ------------------------------------- |
| `GET /v2/search?q=服务器挂了`   | sop-001（后端）和 sop-004（SRE）靠前 |
| `GET /v2/search?q=黑客攻击`     | sop-005（安全团队）靠前              |
| `GET /v2/search?q=机器学习模型出问题` | sop-008（AI 算法）靠前              |

---

## Phase 3：On-Call 助手 Agent

### API

```text
GET /v3
→ 对话界面（消息输入 + 对话历史，前端不做要求）

API 设计不做限定，自行定义。
```

### 要求

1. 实现一个 Agent，通过对话回答用户的 On-Call 问题
2. Agent 只有一个工具：`readFile(fname: string) -> string`，可读取 `data/` 目录下的任意文件，也可以往 `data/` 目录添加任意文件
3. Agent 不能列目录、不能使用通配符，只能按文件名读取
4. 对话过程展示 Agent 的工具调用过程

### 验证

| 用户提问                           | 期望行为                                                   |
| ---------------------------------- | ---------------------------------------------------------- |
| "数据库主从延迟超过30秒怎么处理？" | Agent 定位并读取 sop-002.html，给出处理步骤                |
| "服务 OOM 了怎么办？"             | Agent 找到 sop-001.html，给出排查和处理建议                |
| "P0 故障的响应流程是什么？"       | Agent 综合多个 SOP 给出完整回答                            |
| "怀疑有人入侵了系统"             | Agent 找到 sop-005.html，给出安全事件响应流程              |
| "推荐结果质量下降了"             | Agent 找到 sop-008.html，给出排查方向                      |

---

## 实现说明

本目录包含一个可直接运行的参考实现，优先满足 README 中 `/v1`、`/v2`、`/v3` 的验收要求，同时保持模块解耦和可扩展设计。

### 运行方式

```bash
cd question-1
python3 main.py
```

启动后访问：

- `http://127.0.0.1:8000/v1`：关键词搜索页面
- `http://127.0.0.1:8000/v2`：语义搜索页面
- `http://127.0.0.1:8000/v3`：Agent 对话页面

项目使用 Python 标准库实现，无需安装第三方依赖。Python 3.9+ 可运行。

### 验证方式

```bash
cd question-1
make test
make test2
make coverage-test2
make verify
```

`make verify` 会按 README 的关键验收案例运行检查，并生成：

- `reports/verification.md`
- `reports/verification.txt`

`make coverage-test2` 会运行 `test2/` 扩展测试，并使用 Python 标准库 `trace` 统计 `app/` 业务代码覆盖率，要求不低于 80%。

### 架构划分

```text
app/
  api/              # /v1 /v2 /v3 HTTP 协议适配和页面
  core/             # 配置、依赖装配
  documents/        # SOP 文档模型、仓库、HTML parser 插件
  search/           # keyword / semantic / hybrid 搜索插件
  agent/            # On-Call Agent 编排
  llm/              # 通用 LLMClient 抽象与 provider 预留
  tools/            # Agent 工具插件，当前只注册 readFile
  reports/          # Markdown / txt 结构化报告
  utils/            # 文本、HTML 等基础工具
```

### 设计约束

- Phase 1 搜索只索引 HTML 可见正文，`script/style` 不会进入检索内容。
- HTML entity 会被解码，因此搜索 `&` 时推荐使用标准 URL：`/v1/search?q=%26`。
- Phase 2 使用可配置的领域概念扩展进行离线语义检索，不硬编码单个验收 query。
- Phase 3 Agent 严格只暴露 `readFile(fname)` 一个工具；Agent 通过读取 `catalog.json` 定位 SOP，再读取具体 SOP 文件。
- LLM 层预留 `mock`、`openai`、`codefuse` provider，但默认实现不依赖外部服务，保证离线验收稳定。
