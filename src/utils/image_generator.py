import base64
from pathlib import Path
from typing import Optional

from src.core.file_manager import FileManager
from src.core.llm_client import LLMClient
from src.utils.dashscope_image_client import DashScopeImageClient


class ImageGenerator:
    # 封面图提示词（硬编码在代码中）
    _COVER_IMAGE_PROMPT = """Create a formal and authoritative celebration image for Apache HugeGraph's graduation from Apache Incubator to Top-Level Project status. 

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
- Modern minimalist design with formal presentation suitable for technical community and enterprise audience"""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        file_manager: Optional[FileManager] = None,
        dashscope_client: Optional[DashScopeImageClient] = None,
    ) -> None:
        self.llm = llm_client
        self.fm = file_manager or FileManager("/Users/wy770/Apache")
        self.dashscope = dashscope_client

    def generate_cover_image_prompt(self, style: str = "formal") -> str:
        """
        生成封面图提示词
        
        Args:
            style: 风格（目前仅支持 "formal"）
        
        Returns:
            增强后的提示词
        """
        base_prompt = self._COVER_IMAGE_PROMPT
        
        enhanced_prompt = f"""{base_prompt}

Visual Style:
- Aesthetic: {style}, ultra-premium editorial quality
- Dimensions: 1696x960px (16:9 aspect ratio)
- High resolution, print-quality digital art style

Avoid: Text overlays, watermarks, cluttered compositions, generic stock photo aesthetics"""
        return enhanced_prompt

    def generate_cover_image(
        self,
        style: str = "formal",
        output_path: Optional[str] = None,
        use_llm_vision: bool = False,
        use_dashscope: bool = True,
        size: str = "1696*960",  # 16:9 比例，适合封面图
    ) -> Optional[str]:
        """
        生成封面图
        
        Args:
            style: 风格（目前仅支持 "formal"）
            output_path: 输出路径
            use_llm_vision: 是否使用LLM vision模型（已废弃，保留兼容性）
            use_dashscope: 是否使用通义万相API生成
            size: 图片尺寸，默认 1696*960 (16:9)
        
        Returns:
            生成的图片路径，如果失败返回 None
        """
        output_path = output_path or "outputs/images/hugegraph_cover_image.png"
        prompt = self.generate_cover_image_prompt(style)
        
        # 优先使用通义万相API
        if use_dashscope and self.dashscope:
            try:
                print("使用通义万相API生成封面图...")
                saved_path = self.dashscope.generate_and_save(
                    prompt=prompt,
                    output_path=output_path,
                    negative_prompt="低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。",
                    size=size,
                    n=1,
                    prompt_extend=True,
                    watermark=False,
                )
                print(f"封面图已生成并保存到: {saved_path}")
                return saved_path
            except Exception as e:
                print(f"通义万相API生成失败: {e}")
                print("提示：请手动使用其他工具生成封面图，提示词已硬编码在代码中")
                return None
        
        # 如果API不可用，返回 None（不抛出异常，让调用者决定如何处理）
        print("提示：通义万相API未配置，跳过封面图生成")
        print("提示：如需生成封面图，请配置 DASHSCOPE_API_KEY 环境变量")
        return None
