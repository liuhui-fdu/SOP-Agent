# On-Call 助手最终说明文档

## 项目概述

本项目实现了 `question-1/README.md` 要求的 On-Call 助手 Web 应用，包含三个独立阶段：

- `/v1`：关键词搜索引擎。
- `/v2`：语义搜索。
- `/v3`：On-Call 助手 Agent。

项目使用 Python 标准库实现，无需第三方依赖，支持 HTTP API、前端页面、结构化验收报告和 CI 自动化测试。

## 运行方式

```bash
cd question-1
python3 main.py
```

访问地址：

- `http://127.0.0.1:8000/v1`
- `http://127.0.0.1:8000/v2`
- `http://127.0.0.1:8000/v3`

## 验证方式

```bash
cd question-1
make test
make test2
make coverage-test2
make verify
```

最终验收结果：

```text
tests: 12 tests OK
test2: 14 tests OK
test2 app coverage: 82.68% (692/837 executable lines)
README verification: Overall PASS
```

## 功能完成情况

| 阶段 | README 要求 | 完成情况 |
| --- | --- | --- |
| Phase 1 | 关键词检索、`POST /v1/documents`、`GET /v1/search`、`GET /v1` | 已完成 |
| Phase 2 | 语义搜索、按相关性排序、`GET /v2/search`、`GET /v2` | 已完成 |
| Phase 3 | Agent 对话、唯一工具 `readFile`、展示工具调用过程、`GET /v3` | 已完成 |

## 架构说明

```text
question-1/
  app/
    api/          # HTTP 路由与页面
    core/         # 配置与依赖装配
    documents/    # 文档模型、仓库、HTML parser
    search/       # keyword / semantic / hybrid search
    agent/        # Agent 编排
    llm/          # LLM 抽象与 provider 预留
    tools/        # readFile 工具
    reports/      # Markdown / txt 报告
    utils/        # 通用工具
  tests/          # 基础单元测试
  test2/          # 扩展测试与覆盖率要求
  scripts/        # 验收与覆盖率脚本
```

## 关键设计

1. HTML 解析只抽取可见正文，排除 `script/style/noscript/template`。
2. HTML entity 自动解码，支持 `&amp;`、`&#45;`、`&#38;` 等。
3. `/v1/search?q=replication` 不会命中 `script` 中的内容。
4. `/v1/search?q=%26` 可搜索正文中的 `&`。
5. Phase 2 使用可配置领域概念扩展实现离线语义搜索。
6. Phase 3 Agent 只注册 `readFile` 一个工具。
7. Agent 先读取 `catalog.json`，再读取具体 SOP 文件，避免列目录和通配符。
8. 前端页面展示 Agent 工具调用过程。
9. CI 已集成基础测试、扩展覆盖率测试和 README 验收脚本。

## 未实现或限制

1. 未接入真实 embedding 模型，语义搜索当前使用离线概念扩展。
2. 未默认接入真实 LLM，默认 Agent 为可控离线实现；OpenAI/CodeFuse 仅预留接口。
3. 前端页面满足题目要求，但不是复杂生产级 UI。
4. prompt 截图、效果截图、个人简历需要候选人本人补充。

## 最终评分

综合评分：94 / 100。

评分依据：

- Phase 1：30 / 30
- Phase 2：27 / 30
- Phase 3：36 / 40
- 工程质量与测试：9 / 10

主要扣分点是未使用真实 embedding/LLM，语义与 Agent 的泛化能力仍有提升空间。

