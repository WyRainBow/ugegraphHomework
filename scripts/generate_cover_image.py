import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.image_generator import ImageGenerator
from src.utils.dashscope_image_client import DashScopeImageClient


def main() -> None:
    # 初始化通义万相客户端（如果API Key存在）
    dashscope_client = None
    try:
        dashscope_client = DashScopeImageClient()
        print("已检测到通义万相API配置，将使用API自动生成封面图")
    except ValueError:
        print("未配置 DASHSCOPE_API_KEY，将使用手动生成方式")
    
    generator = ImageGenerator(dashscope_client=dashscope_client)
    result = generator.generate_cover_image(style="formal", use_dashscope=(dashscope_client is not None))
    if result:
        print(f"封面图已生成: {result}")
    else:
        print("请按照提示使用通义万相或 Google Nanobraow 生成封面图")


if __name__ == "__main__":
    main()
