---
name: Apache HugeGraph 项目 - Plan 3: 文章生成功能实现
overview: 实现毕业文章生成、数据可视化、封面图生成和完整工作流。
todos:
  - id: create_prompt_templates
    content: 创建所有 prompt 模板（文章生成、大纲生成、引用提取、封面图）
    status: pending
  - id: implement_article_generator
    content: 实现文章生成器（工作流各阶段）
    status: pending
  - id: implement_data_visualizer
    content: 实现数据可视化工具（生成图表）
    status: pending
  - id: implement_workflow
    content: 实现完整的工作流（整合所有功能）
    status: pending
  - id: create_main_scripts
    content: 创建主执行脚本
    status: pending
  - id: generate_final_outputs
    content: 生成最终输出文件（文章、图表、文档）
    status: pending
---

# Plan 3: 文章生成功能实现

## 目标

实现完整的文章生成功能：
- Prompt 模板创建
- 文章生成器（工作流各阶段）
- 数据可视化图表生成
- 完整工作流整合
- 主执行脚本

## 任务列表

### 1. 创建 Prompt 模板

**需要创建的 Prompt 文件**：
- `config/prompts/article_generation.md` - 文章生成 prompt
- `config/prompts/outline_generation.md` - 大纲生成 prompt
- `config/prompts/quote_extraction.md` - 引用提取 prompt
- `config/prompts/cover_image.md` - 封面图生成 prompt（使用已有的 `cover_image_prompts.md`）

**Prompt 设计要点**：
- 采用结构化的 prompt 设计和规则
- 关键规则：NO LINKS, NO FLUFF, NO HALLUCINATIONS, STRICT WORD LIMIT
- 格式化规则：短段落、避免 bullet points、主动语态
- JSON schema 输出格式

### 2. 实现文章生成器 (`src/tasks/article_generator.py`)

**工作流阶段**：
- Phase 0: 信息收集（从已有数据文件读取）
- Phase 1: 大纲生成（使用 LLM + outline prompt）
- Phase 2: 正文撰写（使用完整的 content writing prompt）
- Phase 3: 引用金句提取（从投票邮件）
- Phase 4: 数据可视化（生成图表）
- Phase 5: 内容整合（Markdown 格式化）

**功能要求**：
- 集成 LLM 客户端调用
- 分阶段执行工作流
- 内容格式化
- 图表占位符替换

### 3. 实现数据可视化工具 (`src/tasks/data_visualizer.py`)

**需要生成的图表**：
- 社区贡献趋势图（折线图）
- 版本发布时间线图（时间线图）
- 投票分布图（饼图/柱状图）

**技术要求**：
- 使用 matplotlib 生成图表
- 保存为 PNG 文件
- 嵌入到文章中的占位符位置

### 4. 实现完整工作流 (`src/workflows/graduation_workflow.py`)

**工作流整合**：
- 整合文章生成器
- 整合数据可视化
- 整合文件管理
- 完整的执行流程

### 5. 创建主执行脚本

**脚本文件**：
- `scripts/generate_article.py` - 执行文章生成
- `scripts/analyze_votes.py` - 执行投票分析
- `scripts/run_all.py` - 执行所有任务

### 6. 生成最终输出

**输出文件**：
- `outputs/articles/hugegraph_graduation_article.md` - 完整文章
- `outputs/images/cover_image.png` - 封面图
- `outputs/images/community_trend.png` - 社区趋势图
- `outputs/images/release_timeline.png` - 版本时间线
- `outputs/images/vote_distribution.png` - 投票分布图

## 数据源

- 投票统计数据：`/Users/wy770/Apache/vote_statistics_summary.md`
- 需求分析报告：`/Users/wy770/Apache/hugegraph_需求分析报告.md`
- 封面图提示词：`/Users/wy770/Apache/cover_image_prompts.md`

## 依赖包

```
matplotlib>=3.7.0
```

## 成功标准

1. ✅ 所有 prompt 模板创建完成
2. ✅ 文章生成器可以生成完整文章
3. ✅ 数据可视化图表生成成功
4. ✅ 工作流可以完整执行
5. ✅ 所有输出文件生成完成
