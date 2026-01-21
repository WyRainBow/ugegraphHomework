import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.core.file_manager import FileManager
from src.core.llm_client import LLMClient
from src.utils.apache_api import ApacheAPIClient


VOTE_VALUE_RE = re.compile(r"^[\s>]*(\+1|\+0|-1)\b", re.IGNORECASE | re.MULTILINE)
BINDING_RE = re.compile(r"\b(non-?binding|binding)\b", re.IGNORECASE)


class VoteAnalyzer:
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        api_client: Optional[ApacheAPIClient] = None,
        file_manager: Optional[FileManager] = None,
    ) -> None:
        from pathlib import Path
        self.llm = llm_client
        self.api = api_client or ApacheAPIClient()
        if file_manager is None:
            # 获取项目根目录（src/tasks 的父目录的父目录）
            project_root = Path(__file__).resolve().parents[2]
            file_manager = FileManager(str(project_root))
        self.fm = file_manager

    def _extract_vote_with_llm(self, body: str) -> Optional[Dict[str, Any]]:
        """
        使用 LLM 辅助解析投票信息（当正则表达式失败时使用）
        
        Args:
            body: 邮件正文内容
        
        Returns:
            投票信息字典，如果解析失败返回 None
        """
        if not self.llm:
            return None
        
        try:
            prompt = f"""从以下邮件正文中提取投票信息：

邮件正文：
{body[:1000]}  # 限制长度避免 token 过多

请提取以下信息：
1. 投票值：查找 "+1"、"-1"、"+0"（通常位于正文开头）
2. 绑定类型：查找 "binding" 或 "non-binding"（大小写不敏感）
3. 原始文本：包含投票值的一行

如果找不到投票信息，返回 null。

返回 JSON 格式：
{{
  "vote_value": "+1" | "-1" | "+0" | null,
  "binding_type": "binding" | "non-binding" | null,
  "raw_text": "原始投票文本"
}}"""
            
            schema = {
                "type": "object",
                "properties": {
                    "vote_value": {"type": ["string", "null"]},
                    "binding_type": {"type": ["string", "null"]},
                    "raw_text": {"type": ["string", "null"]},
                },
                "required": ["vote_value", "binding_type", "raw_text"],
            }
            
            result = self.llm.craft_ai(
                task_category="Analyzing",
                task_vibe="Data Extraction",
                task_summary="Extract vote information from email",
                task_instruction=prompt,
                output_schema=schema,
                creativity_level="conservative",
            )
            
            if isinstance(result, dict) and result.get("vote_value"):
                return {
                    "vote_value": result.get("vote_value", "").lower(),
                    "binding_type": result.get("binding_type", "").lower() if result.get("binding_type") else None,
                    "raw_text": result.get("raw_text", ""),
                }
        except Exception as e:
            # LLM 解析失败，返回 None
            pass
        
        return None

    def _extract_vote_from_body(self, body: str) -> Optional[Dict[str, Any]]:
        """
        从邮件正文中提取投票信息
        
        优先使用正则表达式，失败时使用 LLM 辅助解析
        
        Args:
            body: 邮件正文内容
        
        Returns:
            投票信息字典，如果解析失败返回 None
        """
        if not body:
            return None

        # 优先使用正则表达式提取
        vote_match = VOTE_VALUE_RE.search(body)
        if vote_match:
            vote_value = vote_match.group(1).lower()
            binding_match = BINDING_RE.search(body)
            binding_type = None
            if binding_match:
                binding_type = binding_match.group(1).lower()
                if binding_type == "binding":
                    binding_type = "binding"
                elif "non" in binding_type:
                    binding_type = "non-binding"

            raw_text = vote_match.group(0).strip()
            return {
                "vote_value": vote_value,
                "binding_type": binding_type,
                "raw_text": raw_text,
            }
        
        # 正则表达式失败，尝试使用 LLM 辅助解析
        if self.llm:
            return self._extract_vote_with_llm(body)
        
        return None

    def _extract_from_field(self, from_field: str) -> Dict[str, str]:
        name = from_field
        email = ""
        match = re.match(r"(.*)<(.*)>", from_field)
        if match:
            name = match.group(1).strip().strip('"')
            email = match.group(2).strip()
        return {"name": name, "email": email}

    def _format_timestamp(self, epoch: Optional[int]) -> str:
        if not epoch:
            return ""
        return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")

    def analyze_votes(self, thread_url: str) -> List[Dict[str, Any]]:
        """
        分析投票线程中的所有投票
        
        Args:
            thread_url: 投票线程的 URL
        
        Returns:
            投票信息列表
        """
        try:
            thread_id = self.api.extract_thread_id(thread_url)
            thread_data = self.api.get_thread(thread_id)
            email_ids = self.api.collect_email_ids(thread_data)
        except Exception as e:
            print(f"错误: 无法获取线程数据: {e}")
            raise

        votes: List[Dict[str, Any]] = []
        failed_count = 0
        
        for email_id in email_ids:
            try:
                email_data = self.api.get_email(email_id)
                body = email_data.get("body", "")
                vote_info = self._extract_vote_from_body(body)
                
                if not vote_info:
                    failed_count += 1
                    continue

                from_field = email_data.get("from", "")
                name_info = self._extract_from_field(from_field)
                epoch = email_data.get("epoch")

                votes.append(
                    {
                        "email_id": email_id,
                        "name": name_info.get("name", ""),
                        "email": name_info.get("email", ""),
                        "vote_value": vote_info.get("vote_value"),
                        "binding_type": vote_info.get("binding_type"),
                        "timestamp": self._format_timestamp(epoch),
                        "epoch": epoch,
                        "raw_text": vote_info.get("raw_text"),
                    }
                )
            except Exception as e:
                print(f"警告: 处理邮件 {email_id} 时出错: {e}")
                failed_count += 1
                continue

        if failed_count > 0:
            print(f"警告: {failed_count} 封邮件未能提取投票信息")
        
        return votes

    def compute_statistics(self, votes: List[Dict[str, Any]]) -> Dict[str, Any]:
        stats = {
            "total": len(votes),
            "by_binding": defaultdict(int),
            "by_value": defaultdict(int),
            "by_binding_value": defaultdict(int),
        }

        for vote in votes:
            binding = vote.get("binding_type") or "unknown"
            value = vote.get("vote_value") or "unknown"
            stats["by_binding"][binding] += 1
            stats["by_value"][value] += 1
            stats["by_binding_value"][f"{binding}:{value}"] += 1

        stats["by_binding"] = dict(stats["by_binding"])
        stats["by_value"] = dict(stats["by_value"])
        stats["by_binding_value"] = dict(stats["by_binding_value"])
        return stats

    def render_markdown(self, votes: List[Dict[str, Any]], stats: Dict[str, Any]) -> str:
        lines = ["# HugeGraph 毕业投票统计结果", "", "## 投票数据总览", ""]
        lines.append(f"- 总票数: {stats['total']}")
        lines.append("")
        lines.append("## 详细投票列表")
        lines.append("")

        for vote in votes:
            name = vote.get("name", "")
            value = vote.get("vote_value", "")
            binding = vote.get("binding_type", "")
            ts = vote.get("timestamp", "")
            lines.append(f"- {name} - {value} ({binding}) - {ts}")

        return "\n".join(lines)

    def save_outputs(self, votes: List[Dict[str, Any]], stats: Dict[str, Any]) -> None:
        self.fm.write_json("outputs/data/vote_data.json", {"votes": votes, "stats": stats})
        markdown = self.render_markdown(votes, stats)
        self.fm.write_text("outputs/statistics/vote_statistics.md", markdown)
