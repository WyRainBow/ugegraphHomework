# Apache HugeGraph 毕业项目

本项目用于生成 HugeGraph 从 Apache 孵化器毕业的文章与投票统计结果。

## 功能

- 毕业文章生成（公众号风格）
- 投票结果统计（Binding / Non-Binding 分组）
- 数据可视化图表生成
- 封面图自动生成（通义万相API）

## 目录结构

- `config/prompts/`：Prompt 模板
- `src/core/`：核心模块（LLM 客户端、文件管理）
- `src/tasks/`：任务实现（文章生成、投票分析）
- `src/utils/`：工具函数
- `src/workflows/`：工作流整合
- `scripts/`：执行脚本
- `outputs/`：输出文件

## 环境变量

复制 `.env.example` 为 `.env` 并填写：

```
# ChatAI API 配置（用于文章生成）
CHATAI_API_KEY=your_chatai_api_key
CHATAI_BASE_URL=https://www.chataiapi.com/v1
DEFAULT_LLM_MODEL=gemini-2.5-pro

# 通义万相API配置（用于封面图生成）
DASHSCOPE_API_KEY=your_dashscope_api_key
DASHSCOPE_REGION=cn-beijing
```

**说明：**
- `CHATAI_API_KEY`: 用于文章生成的ChatAI API密钥
- `DASHSCOPE_API_KEY`: 用于封面图生成的通义万相API密钥（可选，未配置时将使用手动生成方式）
- `DASHSCOPE_REGION`: 通义万相API地域，可选值：`cn-beijing`（北京）、`ap-southeast-1`（新加坡）、`us-east-1`（弗吉尼亚）

## 运行

### 生成投票统计
```bash
python scripts/analyze_votes.py --use-summary
```

### 生成封面图
```bash
python scripts/generate_cover_image.py
```
如果配置了 `DASHSCOPE_API_KEY`，将自动使用通义万相API生成封面图；否则提示词已硬编码在代码中（`ImageGenerator._COVER_IMAGE_PROMPT`），可手动生成。

### 测试通义万相API
```bash
python scripts/test_dashscope.py
```

### 生成文章
```bash
python scripts/generate_article.py
```

### 执行所有任务
```bash
python scripts/run_all.py
```

### 上传到飞书云文档
```bash
# 方式1: 使用 app_id 和 app_secret
python scripts/upload_to_feishu.py --app-id YOUR_APP_ID --app-secret YOUR_APP_SECRET

# 方式2: 直接使用 token
python scripts/upload_to_feishu.py --token YOUR_TENANT_ACCESS_TOKEN

# 方式3: 使用环境变量
export FEISHU_APP_ID=your_app_id
export FEISHU_APP_SECRET=your_app_secret
python scripts/upload_to_feishu.py
```

脚本会上传以下内容到飞书云文档：
- 实现思路和 Prompt 说明
- 所有 Prompt 模板文件
- 实现检查报告
