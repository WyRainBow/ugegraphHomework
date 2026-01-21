# 实现思路和 Prompt 说明

## 一、实现思路

### 1. 架构设计思路

本项目采用模块化、工作流驱动的设计模式，采用了以下设计思路：

#### 1.1 模块化设计
- **核心模块**（`src/core/`）：LLM 客户端、文件管理工具
- **任务模块**（`src/tasks/`）：文章生成、投票分析、数据可视化
- **工具模块**（`src/utils/`）：Apache API 客户端、图片生成工具
- **工作流模块**（`src/workflows/`）：整合所有功能

#### 1.2 工作流设计
采用分阶段执行模式：
- 每个阶段有明确的输入输出
- 支持阶段间的数据传递
- 便于调试和优化

#### 1.3 LLM 调用接口
设计统一的 LLM 调用接口：
- 统一的函数签名
- 支持 JSON schema 输出
- 温度控制和错误处理

### 2. 数据流设计

#### 2.1 文章生成流程
```
已有数据文件（vote_statistics_summary.md, hugegraph_需求分析报告.md）
  ↓
信息收集（FileManager 读取）
  ↓
大纲生成（LLM + outline prompt）
  ↓
正文撰写（LLM + content prompt）
  ↓
引用提取（LLM + quote prompt）
  ↓
数据可视化（matplotlib 生成图表）
  ↓
内容整合（替换占位符）
  ↓
输出 Markdown 文件
```

#### 2.2 投票分析流程
```
Apache Pony Mail API
  ↓
邮件数据提取（递归遍历 children）
  ↓
正则表达式解析（+1, -1, +0, binding/non-binding）
  ↓
LLM 辅助解析（当正则失败时）
  ↓
数据清洗和分组统计
  ↓
生成统计报告（Markdown + JSON）
```

### 3. 封面图生成思路

封面图生成设计：

1. **Prompt 提取**：从 `cover_image_prompts.md` 提取详细提示词
2. **Prompt 增强**：添加视觉风格要求
3. **生成方式**：
   - **优先使用通义万相API**：如果配置了 `DASHSCOPE_API_KEY`，将自动调用通义万相文生图API（wan2.6-t2i模型）生成封面图
   - **降级方案**：如果未配置API Key，则生成详细的 prompt 文档供手动使用（Google Nanobraow 或其他工具）

#### 3.1 通义万相API集成

- **模型**：wan2.6-t2i（推荐）
- **API端点**：北京地域 `https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation`
- **调用方式**：HTTP同步调用（wan2.6支持）
- **图片尺寸**：默认 1696*960（16:9比例，适合封面图）
- **特性**：
  - 支持提示词智能改写（prompt_extend）
  - 支持反向提示词（negative_prompt）
  - 生成的图片URL有效期为24小时，自动下载并保存到本地

## 二、Prompt 设计

### 1. 文章生成 Prompt

#### 1.1 设计思路
采用结构化的 Prompt 设计，确保输出质量

#### 1.2 核心结构
```
System Role: Expert subject matter authority writing premium article

Critical Rules:
- NO LINKS: 不添加任何链接（后续统一插入）
- NO FLUFF: 直接进入主题，避免空话
- NO HALLUCINATIONS: 不编造事实或数据
- STRICT WORD LIMIT: 严格字数限制（2000-3000 words）

Topic & Context:
- 主题：Apache HugeGraph 毕业公告
- 文章类型：公众号风格
- 目标受众：技术社区、开源爱好者

Content Structure:
1. 标题和引言（封面图占位符）
2. 项目简介
3. 孵化历程回顾
4. 关键成就亮点
5. 投票结果总结
6. 链接集合占位符
7. 致谢与展望

Writing Style:
- 段落简短（2-3 句）
- 避免 bullet points（除非简短列表）
- 主动语态
- 避免 AI 检测短语

Data Visualization Placeholders:
- [COMMUNITY_TREND_CHART]
- [RELEASE_TIMELINE_CHART]
- [VOTE_DISTRIBUTION_CHART]

Output Format:
JSON schema:
{
  "title": "...",
  "meta_description": "...",
  "content": "# 标题\n正文..."
}
```

#### 1.3 关键规则说明

**NO LINKS**：
- 文章正文中不包含任何链接
- 链接在后续阶段统一插入
- 避免链接打断阅读流

**NO FLUFF**：
- 直接进入主题
- 避免 "In this article we will discuss..." 等空话
- 每句话都要有价值

**NO HALLUCINATIONS**：
- 只使用提供的数据
- 不编造事实或统计数据
- 不确定的信息明确标注

**STRICT WORD LIMIT**：
- 硬性上限：3000 words
- 更短更好
- 避免冗余描述

### 2. 投票提取 Prompt

#### 2.1 设计思路
当正则表达式无法准确提取投票信息时，使用 LLM 辅助解析。

#### 2.2 Prompt 结构
```
System Role: Data extraction expert

Input: 邮件正文内容

Extraction Rules:
1. 投票值：查找 "+1"、"-1"、"+0"（通常位于正文开头）
2. 绑定类型：查找 "binding" 或 "non-binding"（大小写不敏感）
3. 原始文本：包含投票值的一行

Output Schema:
{
  "vote_value": "+1" | "-1" | "+0" | null,
  "binding_type": "binding" | "non-binding" | null,
  "confidence": "high" | "medium" | "low",
  "raw_text": "原始投票文本"
}
```

### 3. 大纲生成 Prompt

#### 3.1 设计思路
采用结构化的 outline 生成模式

#### 3.2 输出格式
```json
{
  "headline_suggestions": ["标题1", "标题2", "标题3"],
  "sections": [
    {"heading": "H2 标题", "notes": "简短说明"},
    {"heading": "H3 标题", "notes": "简短说明"}
  ],
  "keyword_placement": "关键词布局建议"
}
```

#### 3.3 关键要求
- 只生成标题，不写正文
- H2/H3 结构清晰
- 符合 SEO 模板结构

### 4. 引用提取 Prompt

#### 4.1 设计思路
从投票邮件中提取正面评价和祝贺语。

#### 4.2 提取规则
- 优先选择 IPMC 成员（binding votes）的引用
- 查找关键词："Good luck", "Congrats", "Best wishes", "Congratulations"
- 保持原文，不改写

#### 4.3 输出格式
Markdown blockquote 格式，带 attribution：
```
> 引用内容 — 姓名
```

### 5. 封面图 Prompt

#### 5.1 设计参考
使用已有的 `cover_image_prompts.md` 中的详细提示词。

#### 5.2 增强策略
```
原始 Prompt

Visual Style:
- Aesthetic: formal, ultra-premium editorial quality
- Dimensions: 1200x630px (16:9 aspect ratio)
- High resolution, print-quality digital art style

Avoid: Text overlays, watermarks, cluttered compositions, generic stock photo aesthetics
```

#### 5.3 设计要点
- 突出 Apache 品牌权威性
- 正式、专业的视觉语言
- 适合官方公告和企业传播

## 三、实现亮点

1. **统一的设计模式**：工作流、LLM 接口、Prompt 结构
2. **使用已有数据**：直接使用提供的统计和需求分析文档
3. **模块化设计**：核心功能独立，易于测试和扩展
4. **Prompt 模板化**：集中管理，便于维护和优化
5. **错误处理**：正则表达式优先，LLM 辅助解析

## 五、输出文件说明

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
- `outputs/images/cover_image_prompt.txt` - 封面图生成提示词（供手动使用）

## 六、使用说明

### 生成投票统计
```bash
python scripts/analyze_votes.py --use-summary
```

### 生成文章
```bash
export CHATAI_API_KEY=your_key
export CHATAI_BASE_URL=https://www.chataiapi.com/v1
export DEFAULT_LLM_MODEL=gemini-2.5-flash
python scripts/generate_article.py
```

### 生成封面图
```bash
python scripts/generate_cover_image.py
```

如果配置了 `DASHSCOPE_API_KEY`，将自动使用通义万相API生成封面图；否则会生成提示词文件供手动使用。

### 测试通义万相API
```bash
python scripts/test_dashscope.py
```

### 执行所有任务
```bash
python scripts/run_all.py
```

## 七、后续优化建议

1. **封面图生成**：✓ 已集成通义万相API自动生成
2. **引用提取优化**：改进 prompt，提高引用提取准确率
3. **错误处理增强**：添加重试机制和更详细的错误信息
4. **性能优化**：并行处理多个任务，提高生成速度
5. **图片生成优化**：支持更多图片尺寸和风格选项