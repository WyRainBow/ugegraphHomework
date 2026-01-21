---
name: Apache HugeGraph 项目 - Plan 1: 项目初始化和核心基础设施
overview: 创建项目基础结构、LLM客户端、文件管理工具等核心基础设施，为后续功能实现打下基础。
todos:
  - id: init_project_structure
    content: 创建项目目录结构和基础文件（README.md, requirements.txt, .env.example）
    status: pending
  - id: implement_llm_client
    content: 实现 LLM 客户端（统一的调用接口）
    status: pending
  - id: implement_file_manager
    content: 实现文件管理工具（读取/写入文件、数据加载）
    status: pending
  - id: create_config_files
    content: 创建配置文件和环境变量示例
    status: pending
---

# Plan 1: 项目初始化和核心基础设施

## 目标

创建项目的基础架构，包括：
- 项目目录结构
- LLM 客户端（统一的调用接口设计）
- 文件管理工具
- 配置文件和环境变量

## 任务列表

### 1. 创建项目目录结构

创建以下目录和文件：
```
/Users/wy770/Apache/
├── README.md
├── requirements.txt
├── .env.example
├── config/
│   └── prompts/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── llm_client.py
│   │   └── file_manager.py
│   ├── tasks/
│   │   └── __init__.py
│   ├── utils/
│   │   └── __init__.py
│   └── workflows/
│       └── __init__.py
├── scripts/
├── outputs/
│   ├── articles/
│   ├── images/
│   ├── statistics/
│   └── data/
└── docs/
```

### 2. 实现 LLM 客户端 (`src/core/llm_client.py`)

LLM 客户端设计：

**功能要求**：
- 支持 ChatAI API（兼容 OpenAI 格式）
- 统一的函数签名：`craft_ai(task_category, task_vibe, task_summary, task_instruction, output_schema, creativity_level)`
- 支持 JSON schema 输出
- 温度控制（conservative/creative）
- 错误处理和重试机制
- 支持图片上传（base64 编码）

**API 配置**：
- Base URL: `https://www.chataiapi.com/v1`
- API Key: `sk-QepRoUIhcVEz3qMWDd8m1bJBY11Da6JZ2PkovAanrfU2Xv7G`
- 默认模型: `gemini-2.5-flash`（该 API 仅支持 Gemini 模型）

**接口设计**：
```python
class LLMClient:
    def __init__(
        self, 
        api_key: str = "sk-QepRoUIhcVEz3qMWDd8m1bJBY11Da6JZ2PkovAanrfU2Xv7G",
        base_url: str = "https://www.chataiapi.com/v1",
        model: str = "gemini-2.5-flash"
    )
    
    def craft_ai(
        self,
        task_category: str = None,
        task_vibe: str = None,
        task_summary: str = None,
        task_instruction: str = None,
        output_schema: dict = None,
        creativity_level: str = "conservative",
    ) -> Union[str, Dict]
    
    def generate_image_with_vision(
        self,
        image_path: str,
        prompt: str,
        model: str = "gemini-2.5-flash"
    ) -> str
```

**实现参考**：
- 使用 `requests` 库进行 HTTP 调用
- 使用 `openai` 库的 OpenAI 客户端（兼容格式）
- 支持流式和非流式输出
- 图片上传支持网络 URL 和本地 base64 编码
- **模型限制**：该 API 仅支持 Gemini 模型，默认使用 `gemini-2.5-flash`

### 3. 实现文件管理工具 (`src/core/file_manager.py`)

**功能要求**：
- 读取 Markdown 文件（投票统计、需求分析等）
- 写入输出文件
- JSON 数据加载和保存
- 路径管理

### 4. 创建配置文件

- `requirements.txt`：Python 依赖包
- `.env.example`：环境变量示例
- `README.md`：项目说明文档

## 依赖包

```
openai>=1.0.0
requests>=2.31.0
httpx>=0.25.0
python-dotenv>=1.0.0
```

## 环境变量

```
CHATAI_API_KEY=sk-QepRoUIhcVEz3qMWDd8m1bJBY11Da6JZ2PkovAanrfU2Xv7G
CHATAI_BASE_URL=https://www.chataiapi.com/v1
DEFAULT_LLM_MODEL=gemini-2.5-flash
```

**注意**：该 API 仅支持 Gemini 模型系列。

**注意**：API Key 已提供，可以直接在代码中使用，也可以从环境变量读取。

## 成功标准

1. ✅ 项目目录结构完整
2. ✅ LLM 客户端可以成功调用 ChatAI API
3. ✅ 文件管理工具可以读取和写入文件
4. ✅ 配置文件完整，环境变量设置正确
5. ✅ LLM 客户端支持 JSON schema 输出
6. ✅ 支持图片上传功能（base64 编码）

## API 调用示例

### 普通问答调用
```python
from src.core.llm_client import LLMClient

client = LLMClient()
response = client.craft_ai(
    task_category="Creating",
    task_vibe="Writing Content",
    task_summary="Generate article",
    task_instruction="Write a short article about Apache HugeGraph",
    creativity_level="conservative"
)
```

### 图片上传调用
```python
# 使用本地图片（base64 编码）
response = client.generate_image_with_vision(
    image_path="/path/to/local/image.png",
    prompt="介绍一下这张图"
)

# 使用网络图片 URL
response = client.generate_image_with_vision(
    image_path="https://example.com/image.jpg",
    prompt="介绍一下这张图"
)
```
