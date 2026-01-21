#!/usr/bin/env python3
"""将思路和 prompt 上传到飞书云文档"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.utils.feishu_doc_client import FeishuDocClient
from src.core.file_manager import FileManager


def main() -> None:
    import argparse
    
    parser = argparse.ArgumentParser(description="将思路和 prompt 上传到飞书云文档")
    parser.add_argument("--app-id", help="飞书应用 ID")
    parser.add_argument("--app-secret", help="飞书应用 Secret")
    parser.add_argument("--token", help="飞书 tenant_access_token（如果直接提供token）")
    parser.add_argument("--folder-token", help="文件夹 token（可选）")
    args = parser.parse_args()
    
    # 从环境变量或参数获取配置
    app_id = args.app_id or os.getenv("FEISHU_APP_ID", "")
    app_secret = args.app_secret or os.getenv("FEISHU_APP_SECRET", "")
    token = args.token or os.getenv("FEISHU_TENANT_ACCESS_TOKEN", "")
    
    if not token and (not app_id or not app_secret):
        print("错误: 请提供 --app-id 和 --app-secret，或直接提供 --token")
        print("也可以通过环境变量设置: FEISHU_APP_ID, FEISHU_APP_SECRET, 或 FEISHU_TENANT_ACCESS_TOKEN")
        sys.exit(1)
    
    try:
        print("=" * 60)
        print("正在连接飞书云文档...")
        print("=" * 60)
        
        client = FeishuDocClient(
            app_id=app_id,
            app_secret=app_secret,
            tenant_access_token=token,
        )
        print("✓ 飞书客户端初始化成功")
        
        fm = FileManager("/Users/wy770/Apache")
        
        # 1. 上传实现思路文档
        print("\n正在上传实现思路文档...")
        implementation_guide = fm.read_text("docs/实现思路和Prompt说明.md")
        result1 = client.upload_markdown_document(
            title="Apache HugeGraph 项目 - 实现思路和 Prompt 说明",
            markdown_content=implementation_guide,
            folder_token=args.folder_token,
        )
        print(f"✓ 实现思路文档已创建")
        print(f"  文档链接: {result1.get('url', 'N/A')}")
        print(f"  文档 Token: {result1.get('obj_token', 'N/A')}")
        
        # 2. 上传所有 Prompt 文件
        prompt_files = [
            ("article_generation.md", "文章生成 Prompt"),
            ("outline_generation.md", "大纲生成 Prompt"),
            ("quote_extraction.md", "引用提取 Prompt"),
        ]
        
        print("\n正在上传 Prompt 文件...")
        for filename, title_prefix in prompt_files:
            try:
                prompt_content = fm.read_text(f"config/prompts/{filename}")
                result = client.upload_markdown_document(
                    title=f"Apache HugeGraph 项目 - {title_prefix}",
                    markdown_content=prompt_content,
                    folder_token=args.folder_token,
                )
                print(f"✓ {title_prefix} 已上传")
                print(f"  文档链接: {result.get('url', 'N/A')}")
            except Exception as e:
                print(f"✗ {title_prefix} 上传失败: {e}")
        
        # 3. 上传检查报告
        print("\n正在上传检查报告...")
        try:
            check_report = fm.read_text("docs/实现检查报告.md")
            result3 = client.upload_markdown_document(
                title="Apache HugeGraph 项目 - 实现检查报告",
                markdown_content=check_report,
                folder_token=args.folder_token,
            )
            print(f"✓ 检查报告已上传")
            print(f"  文档链接: {result3.get('url', 'N/A')}")
        except Exception as e:
            print(f"✗ 检查报告上传失败: {e}")
        
        print("\n" + "=" * 60)
        print("所有文档上传完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
