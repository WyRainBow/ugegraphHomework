import os
import time
from pathlib import Path
from typing import Optional

import requests
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()


class DashScopeImageClient:
    """通义万相文生图API客户端"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "wan2.6-t2i",
    ):
        """
        初始化通义万相客户端
        
        Args:
            api_key: API密钥，默认从环境变量 DASHSCOPE_API_KEY 读取
            base_url: API基础URL，默认使用北京地域
            model: 模型名称，默认使用 wan2.6-t2i
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY", "")
        self.model = model
        
        # 默认使用北京地域
        if base_url:
            self.base_url = base_url
        else:
            region = os.getenv("DASHSCOPE_REGION", "cn-beijing")
            if region == "cn-beijing":
                self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
            elif region == "ap-southeast-1":
                self.base_url = "https://dashscope-intl.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
            elif region == "us-east-1":
                self.base_url = "https://dashscope-us.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
            else:
                self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
        
        if not self.api_key:
            raise ValueError("DASHSCOPE_API_KEY is required")
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        size: str = "1280*1280",
        n: int = 1,
        prompt_extend: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None,
        timeout: int = 300,
    ) -> dict:
        """
        生成图片（同步调用，仅支持wan2.6）
        
        Args:
            prompt: 正向提示词
            negative_prompt: 反向提示词
            size: 图片尺寸，格式为 "宽*高"
            n: 生成图片数量（1-4）
            prompt_extend: 是否开启提示词智能改写
            watermark: 是否添加水印
            seed: 随机数种子
            timeout: 请求超时时间（秒）
        
        Returns:
            包含图片URL的响应字典
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        payload = {
            "model": self.model,
            "input": {
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "text": prompt
                            }
                        ]
                    }
                ]
            },
            "parameters": {
                "prompt_extend": prompt_extend,
                "watermark": watermark,
                "n": n,
                "negative_prompt": negative_prompt,
                "size": size,
            }
        }
        
        if seed is not None:
            payload["parameters"]["seed"] = seed
        
        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
            response.raise_for_status()
            result = response.json()
            
            # 检查是否有错误
            if "code" in result and result["code"]:
                raise Exception(f"API Error: {result.get('message', 'Unknown error')}")
            
            return result
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def download_image(self, image_url: str, save_path: str) -> str:
        """
        下载图片并保存到本地
        
        Args:
            image_url: 图片URL
            save_path: 保存路径
        
        Returns:
            保存的文件路径
        """
        try:
            response = requests.get(image_url, timeout=60)
            response.raise_for_status()
            
            # 确保目录存在
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, "wb") as f:
                f.write(response.content)
            
            return save_path
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download image: {str(e)}")
    
    def generate_and_save(
        self,
        prompt: str,
        output_path: str,
        negative_prompt: str = "",
        size: str = "1280*1280",
        n: int = 1,
        prompt_extend: bool = True,
        watermark: bool = False,
        seed: Optional[int] = None,
    ) -> str:
        """
        生成图片并保存到本地（一步完成）
        
        Args:
            prompt: 正向提示词
            output_path: 输出文件路径
            negative_prompt: 反向提示词
            size: 图片尺寸
            n: 生成图片数量
            prompt_extend: 是否开启提示词智能改写
            watermark: 是否添加水印
            seed: 随机数种子
        
        Returns:
            保存的文件路径
        """
        print(f"正在生成图片，请稍候...")
        result = self.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            size=size,
            n=n,
            prompt_extend=prompt_extend,
            watermark=watermark,
            seed=seed,
        )
        
        # 提取图片URL
        if "output" in result and "choices" in result["output"]:
            choices = result["output"]["choices"]
            if choices and len(choices) > 0:
                content = choices[0].get("message", {}).get("content", [])
                if content and len(content) > 0:
                    image_url = content[0].get("image")
                    if image_url:
                        print(f"图片生成成功，正在下载...")
                        return self.download_image(image_url, output_path)
        
        # 如果响应格式不符合预期，打印调试信息
        print(f"调试信息 - API响应结构: {list(result.keys())}")
        if "output" in result:
            print(f"调试信息 - output结构: {list(result['output'].keys())}")
        raise Exception(f"Failed to extract image URL from response. Response: {result}")
