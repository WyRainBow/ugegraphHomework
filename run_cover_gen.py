#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# 设置API key
os.environ["DASHSCOPE_API_KEY"] = "sk-234b7d3c15934e3d9f1968fea6779e73"
os.environ["DASHSCOPE_REGION"] = "cn-beijing"

sys.path.insert(0, str(Path(__file__).parent))

# 重定向输出到文件
log_file = Path("cover_gen.log")
with open(log_file, "w") as f:
    f.write("开始生成封面图...\n")
    f.flush()
    
    try:
        from src.utils.dashscope_image_client import DashScopeImageClient
        
        f.write("导入模块成功\n")
        f.flush()
        
        client = DashScopeImageClient()
        f.write("客户端初始化成功\n")
        f.flush()
        
        prompt = """Create a formal and authoritative celebration image for Apache HugeGraph's graduation from Apache Incubator to Top-Level Project status. The composition should feature: Central placement of the Apache feather logo (classic red Apache brand color #D22128) on the left side, HugeGraph project logo positioned next to the Apache logo, Large bold headline text in elegant sans-serif font: "Apache HugeGraph Graduates to Top-Level Project" in white or dark text, Subtitle text below: "2022-2026 | Successfully Incubated" in smaller refined typography, Professional color scheme: Apache red (#D22128), deep blue/dark navy for HugeGraph brand colors, clean white backgrounds, Subtle gradient background transitioning from dark to lighter tones, Celebration elements: subtle sparkles or light rays suggesting achievement and success, Corporate professional aesthetic suitable for official announcements, Clean spacious layout with excellent readability, Dimensions: 1696x960px (16:9 aspect ratio), High resolution print-quality digital art style, Modern minimalist design with formal presentation suitable for technical community and enterprise audience"""
        
        f.write("正在调用API生成图片...\n")
        f.flush()
        
        result = client.generate_and_save(
            prompt=prompt,
            output_path="outputs/images/hugegraph_cover_image.png",
            negative_prompt="低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。",
            size="1696*960",
            n=1,
            prompt_extend=True,
            watermark=False,
        )
        
        f.write(f"成功！图片已保存到: {result}\n")
        f.flush()
        print(f"成功！图片已保存到: {result}")
        
    except Exception as e:
        error_msg = f"错误: {e}\n"
        f.write(error_msg)
        import traceback
        f.write(traceback.format_exc())
        f.flush()
        print(error_msg)
        traceback.print_exc()
