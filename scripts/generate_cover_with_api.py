#!/usr/bin/env python3
"""使用通义万相API生成封面图"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# 设置API key（如果环境变量中没有）
if not os.getenv("DASHSCOPE_API_KEY"):
    os.environ["DASHSCOPE_API_KEY"] = "sk-234b7d3c15934e3d9f1968fea6779e73"
    os.environ["DASHSCOPE_REGION"] = "cn-beijing"

from src.utils.dashscope_image_client import DashScopeImageClient
from src.utils.image_generator import ImageGenerator


def main() -> None:
    try:
        print("=" * 60)
        print("正在使用通义万相API生成封面图...")
        print("=" * 60)
        
        client = DashScopeImageClient()
        generator = ImageGenerator(dashscope_client=client)
        
        result = generator.generate_cover_image(
            style="formal",
            output_path="outputs/images/hugegraph_cover_image.png",
            use_dashscope=True,
            size="1696*960",
        )
        
        if result:
            print("=" * 60)
            print(f"✓ 封面图生成成功！")
            print(f"保存路径: {result}")
            print("=" * 60)
        else:
            print("✗ 封面图生成失败")
    except Exception as e:
        print(f"✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
