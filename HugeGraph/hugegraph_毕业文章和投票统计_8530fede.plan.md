---
name: HugeGraph 毕业文章和投票统计
overview: 为 HugeGraph 从 Apache 基金会毕业创建公众号风格文章和投票结果统计。包含文章内容撰写、封面图生成，以及从邮件列表链接提取并分组统计投票结果。
todos:
  - id: extract_vote_data
    content: 从Apache邮件列表页面提取所有投票数据（姓名、投票值、绑定类型、时间）
    status: pending
  - id: process_vote_statistics
    content: 按绑定类型和投票类型分组统计投票结果，生成结构化报告
    status: pending
    dependencies:
      - extract_vote_data
  - id: research_project_info
    content: 收集HugeGraph项目相关信息（孵化历程、社区数据、技术亮点等）
    status: pending
  - id: write_article_content
    content: 撰写综合全面的毕业文章（包含所有主要方面）
    status: pending
    dependencies:
      - research_project_info
      - process_vote_statistics
  - id: generate_cover_image
    content: 设计并生成封面图/主题图（现代简洁科技风格）
    status: pending
  - id: create_output_files
    content: 整理所有输出文件（文章、图片、统计报告、实现说明）
    status: pending
    dependencies:
      - write_article_content
      - generate_cover_image
      - process_vote_statistics
---

# HugeGraph 毕业文章和投票统计任务计划

## 一、需求分析

### 任务1：毕业文章撰写

- **目标**：创建一篇公众号风格的毕业文章，庆祝 HugeGraph 从 Apache 孵化器毕业为顶级项目
- **包含内容**：
- 文章正文（综合全面，包含项目简介、孵化历程、社区成长、技术亮点、投票结果总结等）
- 封面图/主题图生成（推荐现代简洁科技风格，符合 Apache 品牌规范）
- **输出**：Markdown 格式文章 + 图片文件

### 任务2：投票结果统计

- **数据源**：Apache 邮件列表投票线程
- 链接：https://lists.apache.org/thread/djkxttgpj08v74r8rqdv3np856g3krlr
- **统计维度**：
- **分组方式**：按绑定类型（binding/non-binding）和投票类型（+1/+0/-1）同时分组
- 提取每个投票人的姓名、投票值、绑定类型、投票时间
- **输出**：结构化的投票统计表格/报告

## 二、技术实现方案

### 1. 投票数据提取（具体方案）

- **数据源**：Apache Pony Mail JSON API
  - 线程信息：`https://lists.apache.org/api/thread.lua?id=djkxttgpj08v74r8rqdv3np856g3krlr`
  - 单封邮件：`https://lists.apache.org/api/email.lua?id={email_id}`
- **提取方法**：

  1. 调用 thread API 获取所有邮件ID（递归遍历children数组）
  2. 批量调用 email API 获取每封邮件的详细信息
  3. 使用正则表达式从 `body` 字段提取投票信息：

     - 投票值：`^\s*[+\-]?1\s*`，`^\s*\+0\s*`（匹配 +1, -1, +0）
     - 绑定类型：`\(?binding\)?`，`\(?non-?binding\)?`（匹配 binding/non-binding）
     - 投票人：从 `from` 字段提取姓名和邮箱
     - 时间戳：从 `epoch` 字段转换
- **数据清洗**：
  - 过滤非投票邮件（如讨论、回复等）
  - 去重（同一人多次投票取最早或最新）
  - 处理格式变体（+1 binding, +1(binding), +1 binding kirs等）
- **无需使用**：Selenium/Playwright等浏览器自动化工具

### 2. 投票数据分组统计

- **分组维度**（从实际数据观察）：
  - **主要维度**：绑定类型（Binding / Non-Binding）
    - Binding：有决定权的投票（IPMC成员）
    - Non-Binding：意见性投票
  - **次要维度**：投票值（+1 / +0 / -1）
    - 从数据看主要是 +1 投票
    - +0 和 -1 投票较少或不存在
- **分组结果表格**：
  ```
  | 分组 | Binding +1 | Binding +0 | Binding -1 | Non-Binding +1 | Non-Binding +0 | Non-Binding -1 | 总计 |
  ```

- **统计指标**：
  - 各分组投票人数和列表
  - 总投票数（Binding vs Non-Binding）
  - 投票时间分布
  - 投票人来源（PMC成员、Committer等）

### 3. 文章内容生成（丰富版）

- **结构框架**：

1. **标题和引言**（毕业消息，带封面图）
2. **项目简介**（HugeGraph 是什么，核心特性）
3. **孵化历程回顾**（2022年1月至今）

   - 时间线可视化（使用matplotlib/plotly生成时间线图）

4. **关键成就亮点**：

   - 社区成长（210+贡献者，10位新committer等）
     - 数据可视化：社区贡献趋势图（贡献者数量随时间变化）
   - 版本发布（5个Apache版本 1.0-1.7）
     - 数据可视化：版本发布时间线图
   - 生产应用（金融、电商、电信等行业）
   - 生态系统（与SeaTunnel、TinkerPop集成等）

5. **投票结果总结**

   - 统计表格
   - 饼图/柱状图展示投票分布
   - 引用金句（从投票邮件中摘录推荐语，如"Good luck", "Congrats"等正面评价）

6. **链接集合**：

   - 官网：https://hugegraph.apache.org
   - GitHub：https://github.com/apache/incubator-hugegraph
   - 文档链接
   - 投票线程链接
   - 相关讨论链接

7. **致谢和展望**

- **风格要求**：公众号风格，中文，专业但易读，适合技术社区
- **数据可视化工具**：Python matplotlib 或 plotly，生成PNG图片嵌入文章

### 4. 封面图生成（明确方案）

- **工具选择**：Google Nanobraow / Nano Banana（图像生成AI工具）
  - **使用方式**：在官网输入英文提示词生成图片
  - **提示词语言**：英文（参考3D打印示例的详细描述方式）
  - **提示词文件**：已准备详细提示词文档（`cover_image_prompts.md`）
- **设计方案**（推荐：正式庄重风格）：
  - **主视觉**：Apache羽毛标志 + HugeGraph Logo
  - **主题文字**："Apache HugeGraph Graduates to Top-Level Project"
  - **副标题**："2022-2026 | Successfully Incubated"
  - **配色**：Apache品牌红 (#D22128) + HugeGraph品牌色
  - **风格**：正式、权威、庆祝，适合官方公告
- **技术规格**：
  - 尺寸：1200x630px（社交媒体标准，16:9宽高比）
  - 格式：PNG（支持透明）或 JPG
  - 包含元素：官方Logo、品牌色、清晰文字
- **实现步骤**：

  1. 查看 `cover_image_prompts.md` 获取正式庄重风格的详细英文提示词
  2. 在Google Nanobraow官网生成封面图
  3. 如需要，基于第一次结果微调提示词再次生成
  4. 保存最终版本为PNG/JPG格式

## 三、实施步骤

### 阶段1：数据收集与分析

1. 使用Python requests调用Apache Pony Mail JSON API

   - 获取线程结构和所有邮件ID
   - 批量获取每封邮件的详细信息

2. 使用正则表达式解析投票数据

   - 提取投票值、绑定类型、投票人、时间

3. 数据清洗和验证

   - 去重、格式标准化

4. 按分组逻辑组织数据（Binding/Non-Binding × +1/+0/-1）

### 阶段2：投票统计生成

1. 生成统计表格（按绑定类型和投票类型分组）
2. 计算汇总数据
3. 输出格式化的统计报告

### 阶段3：文章撰写

1. 收集项目相关信息（从投票邮件正文和链接）
2. 生成数据可视化图表：

   - 社区贡献趋势图
   - 版本发布时间线图
   - 投票分布饼图/柱状图

3. 从投票邮件中提取引用金句
4. 撰写文章各个部分
5. 整合投票统计、图表、引用到文章
6. 添加链接集合
7. 润色和格式调整

### 阶段4：封面图生成

1. 查看 `cover_image_prompts.md` 获取正式庄重风格的详细英文提示词
2. 在Google Nanobraow官网生成封面图
3. 如需要，基于第一次结果微调提示词再次生成
4. 保存最终封面图文件（PNG/JPG，1200x630px）

### 阶段5：输出整理

1. 生成最终文章文件（Markdown）
2. 保存封面图文件
3. 创建包含实现说明的文档

## 四、输出文件

1. `hugegraph_graduation_article.md` - 毕业文章正文（包含数据可视化图表）
2. `hugegraph_cover_image.png` - 封面图（正式庄重风格）
3. `vote_statistics.md` - 投票统计报告（分组表格和详细列表）
4. `data_visualizations/` - 数据可视化图表文件

   - `community_growth_trend.png` - 社区贡献趋势图
   - `release_timeline.png` - 版本发布时间线
   - `vote_distribution.png` - 投票分布图

6. `implementation_guide.md` - 实现说明文档

   - API调用方法
   - 正则表达式提取规则
   - 数据清洗流程
   - 可视化图表生成方法
   - Nanobraow使用说明

7. `vote_data.json` - 原始投票数据（JSON格式，便于后续分析）