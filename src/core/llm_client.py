import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import requests
from dotenv import load_dotenv
from openai import OpenAI

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    # 如果项目根目录没有 .env，尝试加载当前目录的
    load_dotenv()

DEFAULT_BASE_URL = "https://www.chataiapi.com/v1"
DEFAULT_MODEL = "gemini-2.5-pro"


def _safe_json_loads(text: str) -> Union[Dict[str, Any], str]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def _encode_image_to_data_url(image_path: str) -> str:
    with open(image_path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


class LLMClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 300,
    ) -> None:
        self.api_key = api_key or os.getenv("CHATAI_API_KEY", "")
        self.base_url = base_url or os.getenv("CHATAI_BASE_URL", DEFAULT_BASE_URL)
        self.model = model or os.getenv("DEFAULT_LLM_MODEL", DEFAULT_MODEL)
        self.timeout = timeout

        if not self.api_key:
            raise ValueError("CHATAI_API_KEY is required")

        # OpenAI-compatible client for vision-style requests
        self._openai_client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def craft_ai(
        self,
        task_category: Optional[str] = None,
        task_vibe: Optional[str] = None,
        task_summary: Optional[str] = None,
        task_instruction: Optional[str] = None,
        input_data: Optional[str] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        processing_context: Optional[str] = None,
        creativity_level: Optional[str] = None,
        image_sources: Optional[list] = None,
        **kwargs: Any,
    ) -> Union[str, Dict[str, Any]]:
        """
        LLM 调用函数，匹配 Sophia 的 craft_ai_func 签名。
        
        Args:
            task_category: 任务类别（如 "Creating", "Analyzing"）
            task_vibe: 任务氛围/类型（如 "Writing Content", "Outline"）
            task_summary: 任务摘要
            task_instruction: 任务指令（主要内容）
            input_data: 结构化输入数据（JSON 字符串或字典）
            output_schema: 输出 JSON schema（如果需要 JSON 输出）
            processing_context: 处理上下文信息
            creativity_level: 创造力级别 (conservative/balanced/creative)
            image_sources: 图片源列表（用于图片理解）
        
        Returns:
            LLM 响应文本或解析后的 JSON 对象
        """
        if not task_instruction:
            raise ValueError("task_instruction is required")

        # 构建系统消息
        system_content = "You are a helpful assistant."
        if processing_context:
            system_content = f"{system_content} {processing_context}"
        if task_vibe or task_category:
            system_content = f"{system_content} {task_category or ''} {task_vibe or ''}".strip()

        # 构建用户消息
        user_content = task_instruction
        
        # 添加输入数据
        if input_data:
            if isinstance(input_data, dict):
                input_data_str = json.dumps(input_data, ensure_ascii=False)
            else:
                input_data_str = str(input_data)
            user_content = f"{user_content}\n\n## Input Data:\n{input_data_str}"

        # 处理图片源（如果支持）
        messages = []
        if image_sources:
            # 构建包含图片的消息
            content_parts = [{"type": "text", "text": user_content}]
            for img_source in image_sources:
                if isinstance(img_source, str):
                    if img_source.startswith("http://") or img_source.startswith("https://"):
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {"url": img_source}
                        })
                    else:
                        # 本地文件，转换为 base64
                        img_data_url = _encode_image_to_data_url(img_source)
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {"url": img_data_url}
                        })
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": content_parts},
            ]
        else:
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ]

        # 设置温度
        if creativity_level == "conservative":
            temperature = 0.3
        elif creativity_level == "creative":
            temperature = 0.7
        else:  # balanced or default
            temperature = 0.5

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
        }

        if output_schema:
            payload["response_format"] = {"type": "json_object"}

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=self.timeout)
        response.raise_for_status()
        data = response.json()

        content = data["choices"][0]["message"]["content"]
        if output_schema:
            return _safe_json_loads(content)
        return content

    def generate_image_with_vision(
        self,
        image_path: str,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 300,
    ) -> str:
        resolved_model = model or self.model

        if image_path.startswith("http://") or image_path.startswith("https://"):
            image_url = image_path
        else:
            image_url = _encode_image_to_data_url(image_path)

        response = self._openai_client.chat.completions.create(
            model=resolved_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}},
                    ],
                }
            ],
            max_tokens=max_tokens,
            stream=False,
        )

        return response.choices[0].message.content or ""
