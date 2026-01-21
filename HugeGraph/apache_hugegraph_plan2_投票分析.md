---
name: Apache HugeGraph 项目 - Plan 2: 投票分析功能实现
overview: 实现投票数据提取、统计分析和报告生成功能。
todos:
  - id: implement_apache_api_client
    content: 实现 Apache Pony Mail API 客户端（用于提取投票数据）
    status: pending
  - id: implement_vote_analyzer
    content: 实现投票分析器（数据提取、清洗、分组统计）
    status: pending
  - id: create_vote_prompts
    content: 创建投票提取相关的 prompt 模板
    status: pending
  - id: generate_vote_statistics
    content: 生成投票统计报告（Markdown 格式）
    status: pending
---

# Plan 2: 投票分析功能实现

## 目标

实现投票数据的提取、分析和统计报告生成：
- Apache Pony Mail API 客户端
- 投票数据提取和清洗
- 分组统计（Binding/Non-Binding × +1/+0/-1）
- 统计报告生成

## 任务列表

### 1. 实现 Apache API 客户端 (`src/utils/apache_api.py`)

**功能要求**：
- 调用 Apache Pony Mail JSON API
- 获取邮件线程数据
- 递归遍历邮件 children 数组
- 提取单封邮件详情

**API 端点**：
- 线程信息：`https://lists.apache.org/api/thread.lua?id={thread_id}`
- 单封邮件：`https://lists.apache.org/api/email.lua?id={email_id}`

### 2. 实现投票分析器 (`src/tasks/vote_analyzer.py`)

**功能要求**：
- 从邮件 body 提取投票信息（正则表达式 + LLM 辅助）
- 提取投票值（+1, -1, +0）
- 提取绑定类型（binding/non-binding）
- 提取投票人信息
- 数据清洗和去重
- 按分组维度统计

**数据提取策略**：
- 正则表达式匹配投票格式
- LLM 辅助解析复杂格式（当正则失败时）
- 数据验证和清洗

### 3. 创建投票提取 Prompt (`config/prompts/vote_extraction.md`)

**Prompt 设计**：
- System Role: Data extraction expert
- 提取规则说明
- JSON schema 输出格式

### 4. 生成统计报告

**输出内容**：
- 分组统计表格
- 投票人列表
- 时间分布统计
- 保存为 Markdown 和 JSON 格式

**输出文件**：
- `outputs/statistics/vote_statistics.md`
- `outputs/data/vote_data.json`

## 数据源

- 投票线程链接：https://lists.apache.org/thread/djkxttgpj08v74r8rqdv3np856g3krlr
- 已有统计数据：`/Users/wy770/Apache/vote_statistics_summary.md`（可作为参考和验证）

## 成功标准

1. ✅ 成功从 Apache API 提取投票数据
2. ✅ 准确识别投票值和绑定类型
3. ✅ 正确分组统计（Binding/Non-Binding × +1/+0/-1）
4. ✅ 生成完整的统计报告
