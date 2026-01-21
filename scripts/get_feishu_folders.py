#!/usr/bin/env python3
"""获取飞书文件夹列表，找到个人目录的 folder_token"""
import requests
import json

APP_ID = "cli_a87e3c2eab79100d"
APP_SECRET = "EkPzmPPYoM98NxIlBnxZXeVURGIwOlFP"

def get_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": APP_ID, "app_secret": APP_SECRET}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if data.get("code") == 0:
            return data.get("tenant_access_token", "")
    except:
        pass
    return None

def get_folders(token):
    """获取文件夹列表"""
    url = "https://open.feishu.cn/open-apis/drive/v1/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    
    # 获取根目录
    params = {
        "parent_type": "space",
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get("code") == 0:
                files = data.get("data", {}).get("files", [])
                print(f"\n找到 {len(files)} 个文件/文件夹：\n")
                
                for file in files:
                    file_type = file.get("type", "")
                    name = file.get("name", "")
                    token_val = file.get("token", "")
                    
                    if file_type == "folder":
                        print(f"📁 文件夹: {name}")
                        print(f"   Token: {token_val}")
                        print()
                
                return files
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    return []

def main():
    print("=" * 60)
    print("获取飞书文件夹列表")
    print("=" * 60)
    
    token = get_token()
    if not token:
        print("无法获取 token")
        return
    
    print("✓ Token 获取成功\n")
    
    folders = get_folders(token)
    
    print("\n" + "=" * 60)
    print("提示：")
    print("1. 找到你的个人目录（通常是名称包含'个人'或'我的'的文件夹）")
    print("2. 复制该文件夹的 Token")
    print("3. 在 upload_feishu_simple.py 中设置 FOLDER_TOKEN 变量")
    print("=" * 60)

if __name__ == "__main__":
    main()
