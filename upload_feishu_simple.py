#!/usr/bin/env python3
"""简单上传脚本 - 直接使用凭证上传到飞书"""
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import requests
import json

# 你的飞书凭证
APP_ID = "cli_a87e3c2eab79100d"
APP_SECRET = "EkPzmPPYoM98NxIlBnxZXeVURGIwOlFP"

# 你的个人文件夹 token（如果知道的话，可以直接设置）
# 如果不知道，运行 scripts/get_feishu_folders.py 来查找
FOLDER_TOKEN = None  # 例如: "fldcnxxxxxxxxxxxxx"

def get_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if data.get("code") == 0:
            token = data.get("tenant_access_token", "")
            print(f"✓ Token 获取成功", flush=True)
            return token
        else:
            print(f"✗ 获取token失败: {data.get('msg')}", flush=True)
            return None
    except Exception as e:
        print(f"✗ 错误: {e}", flush=True)
        return None

def get_user_folders(token):
    """获取用户的文件夹列表，找到个人目录"""
    url = "https://open.feishu.cn/open-apis/drive/v1/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    
    # 获取根目录下的文件夹
    params = {
        "parent_type": "space",
        "order_by": "created_time",
        "direction": "desc",
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                files = data.get("data", {}).get("files", [])
                # 查找个人目录（通常名称包含"个人"或"我的"）
                for file in files:
                    if file.get("type") == "folder":
                        name = file.get("name", "")
                        if "个人" in name or "我的" in name or "Personal" in name:
                            folder_token = file.get("token", "")
                            print(f"  找到个人目录: {name} (token: {folder_token})", flush=True)
                            return folder_token
    except Exception as e:
        print(f"  获取文件夹列表失败: {e}", flush=True)
    
    return None  # 如果找不到，返回 None，文档会创建在默认位置

def create_doc(token, title, folder_token=None):
    """创建文档到指定文件夹"""
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    
    payload = {"title": title}
    if folder_token:
        payload["folder_token"] = folder_token
        print(f"  创建到文件夹: {folder_token}", flush=True)
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        data = response.json()
        if data.get("code") == 0:
            doc_id = data.get("data", {}).get("document", {}).get("document_id", "")
            print(f"✓ 文档创建成功: {title}", flush=True)
            print(f"  文档 ID: {doc_id}", flush=True)
            return doc_id
        else:
            print(f"✗ 创建文档失败: {data.get('msg')}", flush=True)
            return None
    except Exception as e:
        print(f"✗ 错误: {e}", flush=True)
        return None

def get_document_page_block(token, doc_id):
    """获取文档的页面块 ID（block_type=1）"""
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 0:
                items = data.get("data", {}).get("items", [])
                # 查找页面块（block_type = 1）
                for item in items:
                    if item.get("block_type") == 1:
                        page_block_id = item.get("block_id", "")
                        if page_block_id:
                            print(f"  找到页面块 ID: {page_block_id}", flush=True)
                            return page_block_id
    except Exception as e:
        print(f"  获取页面块失败: {e}", flush=True)
    
    # 如果找不到，返回文档 ID（某些情况下文档 ID 就是页面块 ID）
    return doc_id

def write_content_to_doc(token, doc_id, content):
    """写入文档内容"""
    # 获取页面块 ID（block_type=1）
    page_block_id = get_document_page_block(token, doc_id)
    
    # 将 Markdown 转换为 blocks 格式
    blocks = markdown_to_blocks(content)
    
    if not blocks:
        print("⚠ 无法解析内容为 blocks，跳过写入", flush=True)
        return False
    
    # 使用 children 接口在页面块下创建子 blocks
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{doc_id}/blocks/{page_block_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    
    # 分批写入（每次最多 50 个 blocks）
    batch_size = 50
    success = False
    
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i+batch_size]
        payload = {
            "children": batch,
            "index": -1,  # 在末尾追加
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                data = response.json()
                if data.get("code") == 0:
                    success = True
                    continue
            
            # 如果失败，尝试打印错误信息
            try:
                error_data = response.json()
                print(f"  批次 {i//batch_size + 1} 写入失败: {error_data.get('msg', 'Unknown error')}", flush=True)
            except:
                print(f"  批次 {i//batch_size + 1} 写入失败: HTTP {response.status_code}", flush=True)
        except Exception as e:
            print(f"  批次 {i//batch_size + 1} 写入出错: {e}", flush=True)
    
    if success:
        print(f"✓ 内容写入成功", flush=True)
    else:
        print(f"⚠ 内容写入失败（文档已创建，可手动编辑）", flush=True)
    
    return success

def markdown_to_blocks(content):
    """将 Markdown 转换为飞书 blocks 格式（正确的格式）"""
    lines = content.split("\n")
    blocks = []
    
    for line in lines[:300]:  # 限制前300行
        line = line.rstrip()
        
        # 空行跳过
        if not line.strip():
            continue
        
        # 标题 (# ## ###)
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("#").strip()
            if 1 <= level <= 9 and text:
                # 飞书 block_type: 2=heading1, 3=heading2, ..., 10=heading9
                # 格式：{"block_type": level+1, "heading{level}": {"elements": [...]}}
                block = {
                    "block_type": level + 1,
                    f"heading{level}": {
                        "elements": [
                            {
                                "text_run": {
                                    "content": text
                                }
                            }
                        ]
                    }
                }
                blocks.append(block)
                continue
        
        # 列表项 (- 或 *)
        if line.lstrip().startswith("- ") or line.lstrip().startswith("* "):
            text = line.lstrip()[2:].strip()
            if text:
                blocks.append({
                    "block_type": 12,  # 无序列表
                    "bullet": {
                        "elements": [
                            {
                                "text_run": {
                                    "content": text
                                }
                            }
                        ]
                    }
                })
                continue
        
        # 数字列表 (1. 2. 等)
        stripped = line.lstrip()
        if stripped and stripped[0].isdigit():
            dot_pos = stripped.find(". ")
            if dot_pos > 0 and dot_pos <= 3:
                text = stripped[dot_pos+2:].strip()
                if text:
                    blocks.append({
                        "block_type": 13,  # 有序列表
                        "ordered": {
                            "elements": [
                                {
                                    "text_run": {
                                        "content": text
                                    }
                                }
                            ]
                        }
                    })
                    continue
        
        # 代码块标记跳过
        if line.strip().startswith("```"):
            continue
        
        # 普通段落
        text = line.strip()
        if text:
            blocks.append({
                "block_type": 2,  # 段落
                "text": {
                    "elements": [
                        {
                            "text_run": {
                                "content": text
                            }
                        }
                    ]
                }
            })
    
    return blocks[:200]  # 限制 blocks 数量

def main():
    print("=" * 60, flush=True)
    print("开始上传到飞书云文档", flush=True)
    print("=" * 60, flush=True)
    
    # 获取 token
    token = get_token()
    if not token:
        print("无法获取 token，退出", flush=True)
        return
    
    # 获取个人文件夹 token
    folder_token = FOLDER_TOKEN  # 优先使用手动设置的
    
    if not folder_token:
        print("\n正在查找个人目录...", flush=True)
        folder_token = get_user_folders(token)
        if folder_token:
            print(f"✓ 找到个人目录，文档将创建到你的目录下", flush=True)
        else:
            print("⚠ 未找到个人目录，文档将创建到默认位置", flush=True)
            print("  提示：运行 'python3 scripts/get_feishu_folders.py' 来查找文件夹 token", flush=True)
            print("  或者：你可以在飞书云文档中手动移动文档到你的目录", flush=True)
    else:
        print(f"\n✓ 使用指定的文件夹 token: {folder_token[:20]}...", flush=True)
    
    # 读取文件
    from src.core.file_manager import FileManager
    fm = FileManager("/Users/wy770/Apache")
    
    files_to_upload = [
        ("docs/实现思路和Prompt说明.md", "Apache HugeGraph 项目 - 实现思路和 Prompt 说明"),
        ("config/prompts/article_generation.md", "Apache HugeGraph 项目 - 文章生成 Prompt"),
        ("config/prompts/outline_generation.md", "Apache HugeGraph 项目 - 大纲生成 Prompt"),
        ("config/prompts/quote_extraction.md", "Apache HugeGraph 项目 - 引用提取 Prompt"),
    ]
    
    results = []
    for filepath, title in files_to_upload:
        try:
            print(f"\n处理文件: {filepath}", flush=True)
            content = fm.read_text(filepath)
            
            # 创建文档（指定文件夹）
            doc_id = create_doc(token, title, folder_token)
            if doc_id:
                # 写入内容
                write_content_to_doc(token, doc_id, content)
                
                # 构造文档链接
                doc_url = f"https://bytedance.feishu.cn/docx/{doc_id}"
                results.append((title, doc_id, doc_url))
        except Exception as e:
            print(f"✗ 上传 {title} 失败: {e}", flush=True)
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60, flush=True)
    print("上传完成！", flush=True)
    print("=" * 60, flush=True)
    print("\n文档列表：", flush=True)
    for title, doc_id, url in results:
        print(f"\n{title}", flush=True)
        print(f"  文档 ID: {doc_id}", flush=True)
        print(f"  链接: {url}", flush=True)
    
    print("\n" + "=" * 60, flush=True)
    print("说明：", flush=True)
    print("1. 文档已创建在你的飞书云空间中", flush=True)
    print("2. 如果内容未完全写入，可以在飞书中手动编辑", flush=True)
    print("3. 链接中的域名可能需要根据你的企业替换", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
