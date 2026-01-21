import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.core.file_manager import FileManager
from src.core.llm_client import LLMClient
from src.tasks.vote_statistics_formatter import VoteStatisticsFormatter


class ArticleGenerator:
    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        file_manager: Optional[FileManager] = None,
    ) -> None:
        self.llm = llm_client or LLMClient()
        if file_manager is None:
            # 获取项目根目录（src/tasks 的父目录的父目录）
            project_root = Path(__file__).resolve().parents[2]
            file_manager = FileManager(str(project_root))
        self.fm = file_manager

    def _load_prompt(self, path: str) -> str:
        return self.fm.read_text(path)

    def load_project_info(self) -> str:
        return self.fm.read_text("hugegraph_需求分析报告.md")

    def load_vote_summary(self) -> str:
        vote_data_path = "outputs/data/vote_data.json"
        formatter = VoteStatisticsFormatter()
        if self.fm.file_exists(vote_data_path):
            vote_data = self.fm.read_json(vote_data_path)
            summary_text = vote_data.get("summary_text") or self.fm.read_text("vote_statistics_summary.md")
            counts = vote_data.get("summary_counts")
            return formatter.format_summary(summary_text, counts)
        summary_text = self.fm.read_text("vote_statistics_summary.md")
        return formatter.format_summary(summary_text)

    def load_vote_data(self) -> Dict[str, Any]:
        if self.fm.file_exists("outputs/data/vote_data.json"):
            data = self.fm.read_json("outputs/data/vote_data.json")
            # 如果没有 votes 字段，尝试从 summary_text 中提取基本信息
            if "votes" not in data and "summary_text" in data:
                # 从摘要中提取投票者信息作为降级方案
                summary = data.get("summary_text", "")
                votes = self._extract_votes_from_summary(summary)
                if votes:
                    data["votes"] = votes
            return data
        return {}
    
    def _extract_votes_from_summary(self, summary: str) -> List[Dict[str, Any]]:
        """从摘要文本中提取基本的投票信息（降级方案）"""
        votes = []
        # 提取 IPMC Binding Votes
        binding_match = re.search(r"### IPMC Binding Votes.*?\n\n(.*?)(?=\n###|\n---|$)", summary, re.DOTALL)
        if binding_match:
            binding_text = binding_match.group(1)
            for line in binding_text.split("\n"):
                if line.strip() and re.match(r"^\d+\.", line):
                    name_match = re.search(r"\*\*(.*?)\*\*", line)
                    if name_match:
                        votes.append({
                            "name": name_match.group(1),
                            "vote_value": "+1",
                            "binding_type": "binding",
                            "raw_text": line.strip(),
                        })
        
        # 提取 Non-Binding Votes
        non_binding_match = re.search(r"### Non-Binding Votes.*?\n\n(.*?)(?=\n---|$)", summary, re.DOTALL)
        if non_binding_match:
            non_binding_text = non_binding_match.group(1)
            for line in non_binding_text.split("\n"):
                if line.strip() and re.match(r"^\d+\.", line):
                    name_match = re.search(r"\*\*(.*?)\*\*", line)
                    if name_match:
                        votes.append({
                            "name": name_match.group(1),
                            "vote_value": "+1",
                            "binding_type": "non-binding",
                            "raw_text": line.strip(),
                        })
        
        return votes

    def generate_outline(self, topic: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        prompt_template = self._load_prompt("config/prompts/outline_generation.md")
        instruction = (
            f"{prompt_template}\n\n"
            f"主题: {topic}\n"
            f"需求: {json.dumps(requirements, ensure_ascii=False)}"
        )
        return self.llm.craft_ai(
            task_category="Creating",
            task_vibe="Outline",
            task_summary="Generate outline",
            task_instruction=instruction,
            output_schema={"type": "object"},
            creativity_level="conservative",
        )

    def generate_article_content(self, topic: str, project_info: str, vote_summary: str) -> Dict[str, Any]:
        prompt_template = self._load_prompt("config/prompts/article_generation.md")
        instruction = (
            f"{prompt_template}\n\n"
            f"## 主题\n{topic}\n\n"
            f"## 项目信息\n{project_info}\n\n"
            f"## 投票统计\n{vote_summary}\n\n"
            f"## ⚠️ 重要提醒：字数要求\n"
            f"**必须达到 2000-3000 字，这是硬性要求！**\n\n"
            f"请详细展开每个部分：\n"
            f"- 项目简介部分：至少 300 字，详细介绍 HugeGraph 的功能、特点和应用场景\n"
            f"- 孵化历程部分：至少 400 字，详细描述四年的发展过程、关键事件和里程碑\n"
            f"- 关键成就亮点部分：每个亮点至少 200 字，详细展开社区成长、版本发布、生产应用、生态系统、治理合规等内容\n"
            f"- 投票结果部分：至少 300 字，详细分析投票数据、社区反馈和意义\n"
            f"- 致谢与展望部分：至少 300 字，详细表达感谢和未来规划\n\n"
            f"**请确保文章内容丰富、详细，不要过于简洁。每个章节都要有足够的篇幅和细节。**"
        )
        return self.llm.craft_ai(
            task_category="Creating",
            task_vibe="Writing Content",
            task_summary="Generate graduation article with 2000-3000 words in detail",
            task_instruction=instruction,
            output_schema={"type": "object"},
            creativity_level="balanced",  # 改为 balanced 以获得更丰富的内容
        )

    def extract_quotes(self, votes: List[Dict[str, Any]]) -> str:
        if not votes:
            return ""
        prompt_template = self._load_prompt("config/prompts/quote_extraction.md")
        formatted_emails = self._build_vote_email_context(votes)
        instruction = f"{prompt_template}\n\n投票邮件正文:\n{formatted_emails}"
        result = self.llm.craft_ai(
            task_category="Creating",
            task_vibe="Quote Extraction",
            task_summary="Extract quotes",
            task_instruction=instruction,
            creativity_level="conservative",
        )
        if not isinstance(result, str):
            return ""
        sanitized = self._sanitize_quotes(result)
        if sanitized:
            return sanitized
        return self._fallback_extract_quotes(votes)

    def _build_vote_email_context(self, votes: List[Dict[str, Any]]) -> str:
        items = []
        for vote in votes:
            raw = (vote.get("raw_text") or "").strip()
            name = (vote.get("name") or "").strip()
            binding = (vote.get("binding_type") or "").strip()
            if not raw:
                continue
            items.append(
                "\n".join(
                    [
                        f"Name: {name or 'Unknown'}",
                        f"Binding: {binding or 'unknown'}",
                        "Body:",
                        raw,
                    ]
                )
            )
        return "\n\n---\n\n".join(items[:20])

    def _sanitize_quotes(self, result: str) -> str:
        lower = result.lower()
        blocked = ["很抱歉", "未能找到", "没有找到", "无法找到", "规则", "未找到"]
        if any(token in result for token in blocked):
            return ""
        if any(token in lower for token in ["apologize", "sorry", "unable to find"]):
            return ""

        lines = [line.strip() for line in result.splitlines() if line.strip()]
        quote_lines = [line for line in lines if line.startswith(">")]
        if quote_lines:
            return "\n".join(quote_lines)
        if not lines:
            return ""
        return "\n".join([f"> {line}" for line in lines])

    def _fallback_extract_quotes(self, votes: List[Dict[str, Any]]) -> str:
        patterns = re.compile(
            r"(congrat|congrats|congratulations|good luck|best wishes|thank you|great work|well done|happy to|pleased to|excited to|support)",
            re.IGNORECASE,
        )
        quotes = []
        for vote in votes:
            raw = (vote.get("raw_text") or "").strip()
            name = (vote.get("name") or "").strip()
            if not raw:
                continue
            sentence = self._find_positive_sentence(raw, patterns)
            if sentence:
                quotes.append(f"> {sentence} — {name or 'Unknown'}")
            if len(quotes) >= 3:
                break
        return "\n".join(quotes)

    def _find_positive_sentence(self, text: str, pattern: re.Pattern) -> str:
        parts = re.split(r"(?<=[.!?])\s+|\n", text)
        for part in parts:
            candidate = part.strip().strip('"').strip("'")
            if not candidate:
                continue
            if pattern.search(candidate):
                return candidate
        return ""

    def assemble_article(self, content: str, quotes: str) -> str:
        if quotes.strip():
            return f"{content}\n\n## 引用金句\n\n{quotes}\n"
        return content

    def generate(self) -> Dict[str, Any]:
        topic = "Apache HugeGraph 毕业公告"
        project_info = self.load_project_info()
        vote_summary = self.load_vote_summary()
        vote_data = self.load_vote_data()
        votes = vote_data.get("votes", []) if isinstance(vote_data, dict) else []

        outline = self.generate_outline(topic, {"style": "公众号", "language": "中文"})
        content_result = self.generate_article_content(topic, project_info, vote_summary)
        quotes = self.extract_quotes(votes)

        title = content_result.get("title", "") if isinstance(content_result, dict) else ""
        meta_description = content_result.get("meta_description", "") if isinstance(content_result, dict) else ""
        content = content_result.get("content", "") if isinstance(content_result, dict) else ""
        final_content = self.assemble_article(content, quotes)

        return {
            "title": title,
            "meta_description": meta_description,
            "content": final_content,
            "outline": outline,
        }

    def save_outputs(self, result: Dict[str, Any]) -> None:
        self.fm.write_text("outputs/articles/hugegraph_graduation_article.md", result.get("content", ""))
        self.fm.write_json("outputs/data/article_outline.json", result.get("outline", {}))
