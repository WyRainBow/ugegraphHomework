"""
飞书云文档客户端
用于将思路和 prompt 上传到飞书云文档
"""
import json
import os
from typing import Optional, Dict, Any
import requests


class FeishuDocClient:
    """飞书云文档API客户端"""
    
    def __init__(
        self,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        tenant_access_token: Optional[str] = None,
    ):
        """
        初始化飞书客户端
        
        Args:
            app_id: 飞书应用 ID
            app_secret: 飞书应用 Secret
            tenant_access_token: 租户访问令牌（如果直接提供token，可跳过获取步骤）
        """
        self.app_id = app_id or os.getenv("FEISHU_APP_ID", "")
        self.app_secret = app_secret or os.getenv("FEISHU_APP_SECRET", "")
        self.tenant_access_token = tenant_access_token or os.getenv("FEISHU_TENANT_ACCESS_TOKEN", "")
        self.base_url = "https://open.feishu.cn/open-apis"
        
        # 如果没有提供token，尝试获取
        if not self.tenant_access_token and self.app_id and self.app_secret:
            self.tenant_access_token = self._get_tenant_access_token()
    
    def _get_tenant_access_token(self) -> str:
        """
        获取 tenant_access_token
        
        Returns:
            tenant_access_token
        """
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret,
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取token失败: {data.get('msg', 'Unknown error')}")
            
            return data.get("tenant_access_token", "")
        except Exception as e:
            raise Exception(f"获取 tenant_access_token 失败: {str(e)}")
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        if not self.tenant_access_token:
            raise ValueError("tenant_access_token 未设置，请提供 app_id 和 app_secret 或直接提供 token")
        
        return {
            "Authorization": f"Bearer {self.tenant_access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }
    
    def markdown_to_feishu_content(self, markdown_text: str) -> Dict[str, Any]:
        """
        将 Markdown 文本转换为飞书文档内容格式
        
        Args:
            markdown_text: Markdown 文本
        
        Returns:
            飞书文档内容结构
        """
        lines = markdown_text.split("\n")
        content = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 空行
            if not line:
                content.append({
                    "tag": "paragraph",
                    "content": []
                })
                i += 1
                continue
            
            # 标题
            if line.startswith("#"):
                level = len(line) - len(line.lstrip("#"))
                text = line.lstrip("#").strip()
                content.append({
                    "tag": "heading",
                    "attrs": {"level": min(level, 3)},
                    "content": [{"tag": "text", "text": text}]
                })
                i += 1
                continue
            
            # 列表项
            if line.startswith("- ") or line.startswith("* "):
                text = line[2:].strip()
                content.append({
                    "tag": "bulletListItem",
                    "content": [{"tag": "text", "text": text}]
                })
                i += 1
                continue
            
            # 代码块
            if line.startswith("```"):
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    i += 1  # 跳过结束的 ```
                
                content.append({
                    "tag": "codeBlock",
                    "content": [{"tag": "text", "text": "\n".join(code_lines)}]
                })
                continue
            
            # 普通段落
            content.append({
                "tag": "paragraph",
                "content": [{"tag": "text", "text": line}]
            })
            i += 1
        
        return {
            "tag": "doc",
            "props": {},
            "content": content
        }
    
    def create_document(
        self,
        title: str,
        content: str,
        folder_token: Optional[str] = None,
        content_format: str = "markdown",
    ) -> Dict[str, Any]:
        """
        创建飞书云文档
        
        Args:
            title: 文档标题
            content: 文档内容（Markdown 格式）
            folder_token: 文件夹 token（可选，为空则创建在根目录）
            content_format: 内容格式，支持 "markdown" 或 "json"
        
        Returns:
            包含文档信息的字典（url, obj_token 等）
        """
        url = f"{self.base_url}/docx/v1/documents"
        
        # 转换内容格式
        if content_format == "markdown":
            doc_content = self.markdown_to_feishu_content(content)
        else:
            doc_content = json.loads(content) if isinstance(content, str) else content
        
        payload = {
            "title": title,
            "folder_token": folder_token or "",
        }
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"创建文档失败: {data.get('msg', 'Unknown error')}")
            
            doc_info = data.get("data", {})
            obj_token = doc_info.get("document", {}).get("document_id", "")
            
            # 写入内容
            if obj_token:
                self.update_document_content(obj_token, doc_content)
            
            return {
                "obj_token": obj_token,
                "url": doc_info.get("document", {}).get("url", ""),
                "title": title,
            }
        except Exception as e:
            raise Exception(f"创建飞书文档失败: {str(e)}")
    
    def update_document_content(self, obj_token: str, content: Dict[str, Any]) -> None:
        """
        更新文档内容
        
        Args:
            obj_token: 文档 token
            content: 文档内容结构
        """
        url = f"{self.base_url}/docx/v1/documents/{obj_token}/content"
        
        payload = {
            "content": json.dumps(content, ensure_ascii=False),
        }
        
        try:
            response = requests.patch(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"更新文档内容失败: {data.get('msg', 'Unknown error')}")
        except Exception as e:
            raise Exception(f"更新文档内容失败: {str(e)}")
    
    def upload_markdown_document(
        self,
        title: str,
        markdown_content: str,
        folder_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        上传 Markdown 文档到飞书云文档（简化接口）
        
        Args:
            title: 文档标题
            markdown_content: Markdown 内容
            folder_token: 文件夹 token（可选）
        
        Returns:
            包含文档信息的字典
        """
        return self.create_document(
            title=title,
            content=markdown_content,
            folder_token=folder_token,
            content_format="markdown",
        )
