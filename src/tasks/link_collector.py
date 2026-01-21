import json
from typing import Any, Dict, List, Optional

from src.core.file_manager import FileManager


class LinkCollector:
    def __init__(self, file_manager: Optional[FileManager] = None) -> None:
        self.fm = file_manager or FileManager("/Users/wy770/Apache")

    def load_links(self, path: str = "config/links.json") -> Dict[str, Any]:
        raw = self.fm.read_text(path)
        return json.loads(raw)

    def generate_link_collection(self, path: str = "config/links.json") -> str:
        data = self.load_links(path)
        lines: List[str] = ["## 相关资源", ""]

        def render_section(title: str, items: List[Dict[str, str]]) -> None:
            if not items:
                return
            lines.append(f"### {title}")
            for item in items:
                name = item.get("title", "").strip()
                url = item.get("url", "").strip()
                desc = item.get("description", "").strip()
                if not name or not url:
                    continue
                suffix = f" - {desc}" if desc else ""
                lines.append(f"- [{name}]({url}){suffix}")
            lines.append("")

        render_section("项目链接", data.get("project_links", []))
        render_section("投票与提案", data.get("vote_links", []))
        render_section("相关项目", data.get("related_projects", []))

        return "\n".join(lines).rstrip() + "\n"
