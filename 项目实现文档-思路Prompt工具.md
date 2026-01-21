# Apache HugeGraph 项目实现文档
## 思路 + Prompt + 工具

---

## 一、实现思路

### 1. 整体架构设计

本项目采用模块化、工作流驱动的设计模式，确保代码结构清晰、易于维护和扩展。

#### 1.1 模块化设计

- **核心模块**：LLM 客户端、文件管理工具
- **任务模块**：文章生成、投票分析、数据可视化
- **工具模块**：Apache API 客户端、图片生成工具、飞书文档客户端
- **工作流模块**：整合所有功能，分阶段执行

#### 1.2 工作流设计

采用分阶段执行模式，每个阶段有明确的输入输出和错误处理机制。

**主工作流（GraduationWorkflow）：**

```
初始化阶段
  ├─ 初始化 FileManager（文件管理）
  ├─ 初始化 ArticleGenerator（文章生成器）
  ├─ 初始化 DataVisualizer（数据可视化）
  ├─ 初始化 LinkCollector（链接收集器）
  └─ 初始化 ImageGenerator（图片生成器，可选）
  ↓
执行阶段（run 方法）
  ├─ 步骤1: 封面图生成（可选）
  │   ├─ 调用通义万相 API 生成封面图
  │   └─ 失败时继续执行（不中断流程）
  │
  ├─ 步骤2: 文章内容生成
  │   ├─ 加载项目信息（hugegraph_需求分析报告.md）
  │   ├─ 加载投票统计（vote_statistics_summary.md 或 vote_data.json）
  │   ├─ 生成文章大纲（LLM + outline_generation.md）
  │   ├─ 生成文章正文（LLM + article_generation.md）
  │   ├─ 提取引用金句（LLM + quote_extraction.md）
  │   └─ 组装最终内容（整合正文、引用、占位符）
  │
  ├─ 步骤3: 占位符替换
  │   ├─ 生成数据可视化图表（matplotlib）
  │   │   ├─ 社区贡献趋势图（community_trend.png）
  │   │   ├─ 版本发布时间线（release_timeline.png）
  │   │   └─ 投票分布图（vote_distribution.png）
  │   ├─ 替换图表占位符（[COMMUNITY_TREND_CHART] 等）
  │   ├─ 替换封面图占位符（[封面图占位符]）
  │   └─ 替换链接集合占位符（[链接集合占位符]）
  │
  └─ 步骤4: 保存输出文件
      ├─ 保存文章（outputs/articles/hugegraph_graduation_article.md）
      └─ 保存大纲（outputs/data/article_outline.json）
```

**投票分析工作流（独立流程）：**

```
输入：投票线程 URL
  ↓
步骤1: 数据获取
  ├─ 调用 Apache Pony Mail API
  ├─ 提取线程 ID
  └─ 递归遍历邮件数据
  ↓
步骤2: 投票信息提取
  ├─ 优先使用正则表达式解析
  │   ├─ 投票值（+1, -1, +0）
  │   └─ 绑定类型（binding/non-binding）
  └─ LLM 辅助解析（当正则失败时）
  ↓
步骤3: 数据统计
  ├─ 分组统计（binding/non-binding, +1/+0/-1）
  ├─ 计算百分比和总数
  └─ 格式化统计摘要（VoteStatisticsFormatter）
  ↓
步骤4: 输出生成
  ├─ 保存统计报告（outputs/statistics/vote_statistics.md）
  ├─ 保存原始数据（outputs/data/vote_data.json）
  └─ 生成可视化图表（matplotlib，可选）
```

**工作流特点：**

1. **容错设计**：每个步骤都有独立的异常处理，失败时不会中断整个流程
2. **模块化执行**：每个任务模块（文章生成、投票分析、可视化）可独立运行
3. **占位符机制**：使用占位符标记需要替换的内容，最后统一替换
4. **数据驱动**：优先使用已有数据文件，避免重复计算

### 2. LLM 调用设计

设计统一的 LLM 调用接口，提供一致的调用体验：

- **统一函数签名**：`craft_ai(task_category, task_vibe, task_summary, task_instruction, output_schema, ...)`
- **支持 JSON Schema 输出**：结构化数据提取，确保输出格式规范
- **温度控制**：根据任务类型调整 creativity_level，平衡创造性和准确性
- **错误处理**：完善的异常处理和重试机制，提高系统稳定性

### 3. 数据流设计

**输入数据源**：
- **本地文件**：
  - `hugegraph_需求分析报告.md` - 项目信息
  - `vote_statistics_summary.md` - 投票统计摘要（备用）
  - `outputs/data/vote_data.json` - 投票原始数据（优先使用）
  - `config/links.json` - 项目相关链接配置

- **外部 API**：
  - Apache Pony Mail API - 投票邮件数据（投票分析阶段）

**数据处理流程**：
1. **数据加载**：FileManager 读取本地文件
2. **数据提取**：VoteAnalyzer 从 API 或文件提取投票信息
3. **数据格式化**：VoteStatisticsFormatter 格式化统计摘要
4. **LLM 生成**：ArticleGenerator 使用 LLM 生成文章内容
5. **数据可视化**：DataVisualizer 使用 matplotlib 生成图表
6. **内容整合**：GraduationWorkflow 替换占位符，组装最终内容

**输出数据**：
- **Markdown 文件**：
  - `outputs/articles/hugegraph_graduation_article.md` - 完整文章
  - `outputs/statistics/vote_statistics.md` - 投票统计报告

- **JSON 数据**：
  - `outputs/data/article_outline.json` - 文章大纲
  - `outputs/data/vote_data.json` - 投票原始数据

- **图片文件**：
  - `outputs/images/hugegraph_cover_image.png` - 封面图
  - `outputs/images/community_trend.png` - 社区趋势图
  - `outputs/images/release_timeline.png` - 版本时间线
  - `outputs/images/vote_distribution.png` - 投票分布图

---

## 二、Prompt 设计

### 1. 文章生成 Prompt

完整 Prompt 内容：

```markdown
# 毕业文章生成 Prompt

你是技术社区的资深编辑，要写一篇公众号风格的毕业文章。

## 关键规则（CRITICAL RULES）

### NO LINKS
- **绝对禁止**：不要添加任何链接（后续统一插入）
- 避免链接打断阅读流

### NO FLUFF
- **直接进入主题**：避免 "In this article we will discuss..." 等空话
- 每句话都要有价值
- 不要使用 "Let's dive in" 或 "Without further ado" 等填充句

### NO HALLUCINATIONS
- **严禁编造事实或数据**：只使用提供的数据
- 不编造统计数据、日期、名称等信息
- 不确定的信息明确标注为 "[数据待确认]"
- 如果数据不可用，使用占位符 "[数据不可用]"

### STRICT WORD LIMIT
- **目标字数**：2000-3000 字
- **硬性上限**：绝对不超过 3000 字
- **更短更好**：如果能在更少字数内表达清楚，优先选择更短的版本
- **无情删减**：删除所有冗余描述和填充内容

## 文章主题
Apache HugeGraph 从 Apache 孵化器毕业成为顶级项目（TLP）。

## 写作风格要求

### 段落格式
- **段落简短**：每段 2-3 句，最多不超过 4 句
- **避免大段文字**：大段文字会让读者感到压力

### 列表使用规则
- **尽量避免使用列表**：除非是简短的关键信息（3-5 项）
- **优先使用流畅的散文**：用自然语言描述，而不是 bullet points
- **例外情况**：仅在以下情况使用列表：
  - 简短的功能列表（3-5 项）
  - 价格层级
  - 功能规格对比

### 比较和对比
- **使用表格而非列表**：当需要比较多个项目时，使用 Markdown 表格
- **突出关键信息**：在表格中使用 **粗体** 标记重要信息
- **添加快速结论**：在比较后添加 "> **结论**：..." 格式的总结

### 反 AI 检测
**避免使用以下 AI 检测短语**：
- "In today's world" / "在当今世界"
- "delve into" / "深入探讨"
- "comprehensive guide" / "全面指南"
- "game-changer" / "游戏改变者"
- "unleash" / "释放"
- "elevate" / "提升"
- "streamline" / "简化"
- "leverage" / "利用"
- "robust" / "强大的"
- "cutting-edge" / "前沿的"
- "landscape" / "格局"
- "It is important to note" / "值得注意的是"

**使用自然过渡**：
- "Here's the thing" / "关键点是"
- "But wait" / "但是"
- "The catch?" / "问题在于"

### 语言风格
- **主动语态**：优先使用主动语态
- **专业但易读**：语气专业但保持可读性
- **具体例子**：使用具体、具体的例子，避免抽象概括
- **对话式过渡**：使用自然的对话式过渡

## 内容结构（必须遵循）
1. 标题与引言（包含封面图占位符）
2. 项目简介（HugeGraph 是什么）
3. 孵化历程回顾（2022-2026）
4. 关键成就亮点
   - 社区成长
   - 版本发布
   - 生产应用
   - 生态系统
5. 投票结果总结（含统计表与引用金句）
6. 链接集合占位符
7. 致谢与展望

## 图表占位符
在合适位置插入：
- [COMMUNITY_TREND_CHART]
- [RELEASE_TIMELINE_CHART]
- [VOTE_DISTRIBUTION_CHART]

## 引用金句
从投票邮件中提取正面评价并以引用格式呈现。

## 输出格式
返回 JSON：
{
  "title": "...",
  "meta_description": "...",
  "content": "# 标题\n正文..."
}
```

---

### 2. 大纲生成 Prompt

完整 Prompt 内容：

```markdown
# 大纲生成 Prompt

请生成文章大纲，只包含标题，不要写正文。

## 输出格式（JSON）
{
  "headline_suggestions": ["标题1", "标题2", "标题3"],
  "sections": [
    {"heading": "H2 标题", "notes": "简短说明"},
    {"heading": "H3 标题", "notes": "简短说明"}
  ],
  "keyword_placement": "关键词布局建议"
}
```

---

### 3. 引用提取 Prompt

完整 Prompt 内容：

```markdown
# 引用金句提取 Prompt

从投票邮件正文中提取正面评价、祝贺语或支持性陈述。

## 规则
- 优先选择 IPMC 成员（binding votes）的邮件
- 查找以下类型的表达：
  - 明确祝贺（"Congratulations", "Congrats", "Well done"）
  - 正面评价（"Great work", "Excellent", "Impressive"）
  - 支持性陈述（"I support", "I'm happy to see", "This is great news"）
  - 对项目的积极评价（"Strong community", "Mature project"）
- 如果正文很长，提取最相关的 1-2 句话
- 保持原文，不要改写或总结
- 如果没有合适引用，返回空字符串（不要输出解释或道歉）

## 输出格式
每条引用使用 Markdown blockquote：
> 引用内容 — 姓名
```

---

### 4. 投票提取 Prompt（LLM 辅助）

完整 Prompt 内容：

```text
从以下邮件正文中提取投票信息：

邮件正文：
{body[:1000]}  # 限制长度避免 token 过多

请提取以下信息：
1. 投票值：查找 "+1"、"-1"、"+0"（通常位于正文开头）
2. 绑定类型：查找 "binding" 或 "non-binding"（大小写不敏感）
3. 原始文本：包含投票值的一行

如果找不到投票信息，返回 null。

返回 JSON 格式：
{
  "vote_value": "+1" | "-1" | "+0" | null,
  "binding_type": "binding" | "non-binding" | null,
  "raw_text": "原始投票文本"
}
```

**说明**：此 Prompt 在代码中动态构建，`{body[:1000]}` 会被实际邮件正文内容替换。

---

### 5. 封面图生成 Prompt

完整 Prompt 内容：

```text
Create a formal and authoritative celebration image for Apache HugeGraph's graduation from Apache Incubator to Top-Level Project status. 

The composition should feature:
- Central placement of the Apache feather logo (classic red Apache brand color #D22128) on the left side
- HugeGraph project logo positioned next to the Apache logo, maintaining brand consistency
- Large, bold headline text in elegant sans-serif font: "Apache HugeGraph Graduates to Top-Level Project" in white or dark text
- Subtitle text below: "2022-2026 | Successfully Incubated" in smaller, refined typography
- Professional color scheme: Apache red (#D22128), deep blue/dark navy for HugeGraph brand colors, clean white backgrounds
- Subtle gradient background transitioning from dark to lighter tones
- Celebration elements: subtle sparkles or light rays suggesting achievement and success
- Corporate, professional aesthetic suitable for official announcements
- Clean, spacious layout with excellent readability
- Dimensions: 1200x630px (16:9 aspect ratio), optimized for social media sharing
- High resolution, print-quality digital art style
- Modern minimalist design with formal presentation suitable for technical community and enterprise audience
```

**说明**：此 Prompt 硬编码在 `src/utils/image_generator.py` 的 `_COVER_IMAGE_PROMPT` 类变量中，用于通义万相 API 生成封面图。

---

## 三、工具和技术栈

### 1. LLM 服务

**ChatAI API**
- **Base URL**: `https://www.chataiapi.com/v1`
- **默认模型**: `gemini-2.5-pro`
- **支持模型**: 仅支持 Gemini 系列模型
- **功能**: 文本生成、结构化数据提取（JSON Schema）

**调用方式**
- 使用 OpenAI 兼容接口
- 支持 `temperature`、`max_tokens` 等参数
- 支持 JSON Schema 输出

---

### 2. 图片生成服务

**通义万相 API（DashScope）**
- **模型**: `wan2.6-t2i`（推荐）
- **API Key**: 通过环境变量 `DASHSCOPE_API_KEY` 配置
- **地域**: 北京（`cn-beijing`）
- **Base URL**: `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- **调用方式**: HTTP 同步调用

**功能特性**
- 支持提示词智能改写（`prompt_extend: true`）
- 支持反向提示词（`negative_prompt`）
- 生成的图片 URL 有效期为 24 小时，自动下载并保存到本地
- 支持自定义尺寸（总像素在 [1280*1280, 1440*1440] 之间，宽高比 [1:4, 4:1]）

**默认参数**
- 尺寸：`1696*960`（16:9 比例，适合封面图）
- 数量：`n=1`（按张计费，测试建议设为 1）
- 水印：`watermark=false`（不添加水印）
- 反向提示词：`"低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。"`

---

### 3. 数据可视化工具

**matplotlib**
- 用于生成统计图表
- 输出格式：PNG
- 图表类型：
  - 社区贡献趋势图（折线图）
  - 版本发布时间线（时间轴图）
  - 投票分布图（饼图/柱状图）

---

### 4. 数据源

**Apache Pony Mail API**
- **用途**: 获取投票邮件数据
- **API 端点**: `https://lists.apache.org/api/ponymail.lists.apache.org/thread`
- **数据格式**: JSON
- **处理方式**: 递归遍历 `children` 字段，提取邮件正文

---

### 5. 文件管理

**本地文件系统**
- 输入文件：Markdown 文档（投票统计、需求分析报告）
- 输出文件：
  - `outputs/articles/hugegraph_graduation_article.md` - 完整文章
  - `outputs/data/article_outline.json` - 文章大纲
  - `outputs/data/vote_data.json` - 投票数据
  - `outputs/statistics/vote_statistics.md` - 统计报告
  - `outputs/images/*.png` - 图表和封面图

---

### 6. 飞书云文档集成

**飞书开放平台 API**
- **用途**: 将思路和 Prompt 文档上传到飞书云文档
- **认证方式**: App ID + App Secret → tenant_access_token
- **API 端点**: 
  - 创建文档: `POST /open-apis/docx/v1/documents`
  - 写入内容: `POST /open-apis/docx/v1/documents/{document_id}/blocks/{page_block_id}/children`
- **权限要求**: 云文档读写权限

**功能**
- 自动创建飞书云文档
- 将 Markdown 内容转换为飞书 blocks 格式
- 支持指定文件夹（folder_token）

---

## 四、工作流程总结

### 完整执行流程

#### 阶段一：投票分析（独立执行）

**执行脚本**：`scripts/analyze_votes.py`

**流程步骤**：

1. **数据获取**
   - 从 Apache Pony Mail API 获取投票线程数据
   - 递归遍历邮件树结构，提取所有邮件

2. **投票提取**
   - **优先策略**：使用正则表达式提取投票值（+1, -1, +0）和绑定类型
   - **降级策略**：当正则失败时，调用 LLM 辅助解析
   - 提取发件人信息（姓名、邮箱）

3. **数据统计**
   - 按绑定类型分组（binding vs non-binding）
   - 按投票值分组（+1, +0, -1）
   - 计算总数、百分比等统计指标

4. **格式化输出**
   - 使用 `VoteStatisticsFormatter` 生成格式化的统计摘要
   - 生成 Markdown 格式的统计报告
   - 保存 JSON 格式的原始数据（包含 votes 列表）

5. **数据可视化**（可选）
   - 生成投票分布图（饼图/柱状图）
   - 保存到 `outputs/images/vote_distribution.png`

**输出文件**：
- `outputs/statistics/vote_statistics.md` - 统计报告
- `outputs/data/vote_data.json` - 原始投票数据（包含 votes 列表和 summary_counts）

---

#### 阶段二：文章生成（主工作流）

**执行脚本**：`scripts/generate_article.py`

**流程步骤**：

1. **初始化工作流**
   - 初始化所有任务模块（ArticleGenerator, DataVisualizer, LinkCollector, ImageGenerator）
   - 检查通义万相 API 配置（可选）

2. **封面图生成**（可选，默认启用）
   - 调用通义万相 API 生成封面图（如果配置了 DASHSCOPE_API_KEY）
   - 失败时打印警告，继续执行（不中断流程）
   - 保存到 `outputs/images/hugegraph_cover_image.png`

3. **文章内容生成**（ArticleGenerator.generate）
   
   **3.1 数据加载**
   - 加载项目信息：`hugegraph_需求分析报告.md`
   - 加载投票统计：`vote_statistics_summary.md` 或 `outputs/data/vote_data.json`
   - 使用 `VoteStatisticsFormatter` 格式化投票统计摘要
   - 加载原始投票数据（用于引用提取）

   **3.2 大纲生成**
   - 调用 LLM，使用 `config/prompts/outline_generation.md`
   - 输出 JSON 格式的大纲结构
   - 保存到 `outputs/data/article_outline.json`

   **3.3 正文生成**
   - 调用 LLM，使用 `config/prompts/article_generation.md`
   - 输入：主题、项目信息、投票统计摘要
   - 输出 JSON：`{title, meta_description, content}`
   - 内容包含占位符：`[COMMUNITY_TREND_CHART]`, `[RELEASE_TIMELINE_CHART]`, `[VOTE_DISTRIBUTION_CHART]`, `[封面图占位符]`, `[链接集合占位符]`

   **3.4 引用提取**
   - 从原始投票数据中提取引用金句
   - 调用 LLM，使用 `config/prompts/quote_extraction.md`
   - 输入：投票邮件的原始文本（raw_text）
   - 降级策略：如果 LLM 失败，使用正则表达式提取正面评价
   - 输出：Markdown blockquote 格式的引用列表

   **3.5 内容组装**
   - 将正文、引用金句整合
   - 在合适位置插入引用金句和链接集合占位符

4. **占位符替换**（_replace_placeholders）

   **4.1 数据可视化**
   - 生成社区贡献趋势图：`outputs/images/community_trend.png`
   - 生成版本发布时间线：`outputs/images/release_timeline.png`
   - 生成投票分布图：`outputs/images/vote_distribution.png`

   **4.2 占位符替换**
   - 替换图表占位符：`[COMMUNITY_TREND_CHART]` → `![Community Trend](../images/community_trend.png)`
   - 替换封面图占位符：`[封面图占位符]` → `![Cover Image](../images/hugegraph_cover_image.png)`
   - 替换链接集合占位符：`[链接集合占位符]` → 从 `config/links.json` 生成的链接列表

5. **保存输出**
   - 保存最终文章：`outputs/articles/hugegraph_graduation_article.md`
   - 保存文章大纲：`outputs/data/article_outline.json`

**错误处理**：
- 每个步骤都有独立的 try-except 块
- 封面图生成失败不影响文章生成
- 占位符替换失败时保存原始内容
- 详细的错误日志输出

---

#### 阶段三：文档上传（可选）

**执行脚本**：`upload_feishu_simple.py`

**流程步骤**：

1. **认证**
   - 使用 App ID 和 App Secret 获取 tenant_access_token

2. **文档创建**
   - 查找用户个人文件夹（"明天不下雨"）
   - 创建飞书云文档

3. **内容转换**
   - 将 Markdown 转换为飞书 blocks 格式
   - 支持标题、列表、代码块、段落等格式

4. **内容写入**
   - 使用 blocks API 批量写入内容（每批最多 50 个 blocks）
   - 写入到文档的页面块中

---

### 工作流执行顺序

**推荐执行顺序**：

```bash
# 1. 投票分析（如果还没有数据）
python scripts/analyze_votes.py --use-summary  # 使用已有摘要
# 或
python scripts/analyze_votes.py  # 从 API 获取新数据

# 2. 文章生成（包含封面图生成）
python scripts/generate_article.py

# 3. 文档上传（可选）
python upload_feishu_simple.py
```

**一键执行**：

```bash
python scripts/run_all.py  # 执行所有任务
```

---

## 五、关键设计原则

### 1. 工作流驱动设计

- **分阶段执行**: 每个阶段有明确输入输出，便于调试和优化
  - 投票分析阶段独立执行，可重复运行
  - 文章生成阶段依赖投票分析结果，但可独立运行（使用已有数据）
  - 封面图生成可选，失败不影响主流程

- **容错机制**: 完善的异常处理，确保流程健壮性
  - 每个步骤都有独立的 try-except 块
  - 关键步骤失败时打印警告但继续执行
  - 非关键步骤（如封面图生成）失败不影响整体流程

- **占位符机制**: 使用占位符标记需要动态替换的内容
  - 图表占位符：`[COMMUNITY_TREND_CHART]`, `[RELEASE_TIMELINE_CHART]`, `[VOTE_DISTRIBUTION_CHART]`
  - 封面图占位符：`[封面图占位符]`, `[COVER_IMAGE_PLACEHOLDER]`
  - 链接集合占位符：`[链接集合占位符]`
  - 最后统一替换，确保路径正确

- **LLM 接口统一**: 统一的 `craft_ai` 函数签名，简化调用逻辑
  - 统一的参数结构：`task_category`, `task_vibe`, `task_summary`, `task_instruction`
  - 支持 JSON Schema 输出，确保结构化数据提取
  - 温度控制：根据任务类型调整 `creativity_level`

- **Prompt 结构化**: 采用结构化的 Prompt 设计，确保输出质量
  - 集中管理：所有 Prompt 文件存放在 `config/prompts/` 目录
  - 封面图 Prompt 硬编码在代码中（`ImageGenerator._COVER_IMAGE_PROMPT`）
  - 清晰的规则说明和输出格式要求

- **内容规则严格**: NO LINKS, NO FLUFF, NO HALLUCINATIONS，保证内容质量
  - 文章生成时禁止添加链接（后续统一插入）
  - 禁止空话和填充句
  - 严禁编造事实或数据

### 2. 模块化设计

- 核心功能独立，易于测试和扩展
- Prompt 模板化，集中管理
- 工具类封装，便于复用

### 3. 错误处理

- 正则表达式优先，LLM 辅助解析
- 完善的异常处理和降级方案
- 详细的日志输出

### 4. 数据驱动

- 使用已有数据文件，避免重复工作
- 结构化数据输出（JSON）
- 可视化数据展示

---

## 六、输出文件说明

### 文章相关
- `outputs/articles/hugegraph_graduation_article.md` - 完整文章（包含图表占位符）
- `outputs/data/article_outline.json` - 文章大纲数据

### 投票统计
- `outputs/statistics/vote_statistics.md` - 统计报告
- `outputs/data/vote_data.json` - 原始投票数据

### 数据可视化
- `outputs/images/community_trend.png` - 社区贡献趋势图
- `outputs/images/release_timeline.png` - 版本发布时间线
- `outputs/images/vote_distribution.png` - 投票分布图

### 封面图
- `outputs/images/hugegraph_cover_image.png` - 封面图（如果使用 API 生成）

---

## 七、环境配置

### 必需的环境变量

```bash
# LLM 服务
CHATAI_API_KEY=your_chatai_api_key
CHATAI_BASE_URL=https://www.chataiapi.com/v1
DEFAULT_LLM_MODEL=gemini-2.5-pro

# 图片生成服务（可选）
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_REGION=cn-beijing

# 飞书云文档（可选）
FEISHU_APP_ID=your_feishu_app_id
FEISHU_APP_SECRET=your_feishu_app_secret
```

---

## 八、使用说明

### 生成投票统计
```bash
python scripts/analyze_votes.py --use-summary
```

### 生成文章
```bash
python scripts/generate_article.py
```

### 生成封面图
```bash
python scripts/generate_cover_image.py
```

如果配置了 `DASHSCOPE_API_KEY`，将自动使用通义万相 API 生成封面图；否则会生成提示词文件供手动使用。

### 上传到飞书
```bash
python scripts/upload_to_feishu.py --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET
```

### 执行所有任务
```bash
python scripts/run_all.py
```

---

## 九、实现亮点

1. **工作流驱动设计**：分阶段执行，每个阶段职责明确，便于调试和优化
2. **统一 LLM 接口**：设计统一的 `craft_ai` 函数签名，简化调用逻辑
3. **模块化架构**：核心功能独立，易于测试和扩展
4. **Prompt 模板化**：集中管理所有 Prompt，便于维护和优化
5. **智能错误处理**：正则表达式优先，LLM 辅助解析，提高数据提取准确率
6. **全流程自动化**：从数据获取到文章生成全流程自动化，减少人工干预
7. **多工具集成**：LLM、图片生成、数据可视化、文档管理一体化，提供完整解决方案
8. **结构化输出**：支持 JSON Schema 输出，确保数据格式规范
9. **内容质量保证**：严格的内容规则（NO LINKS, NO FLUFF, NO HALLUCINATIONS），确保输出质量

---

**文档生成时间**: 2025年1月
