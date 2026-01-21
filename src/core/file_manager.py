import json
from pathlib import Path
from typing import Any, Dict, Optional


class FileManager:
    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()

    def _resolve(self, path: str) -> Path:
        p = Path(path)
        if not p.is_absolute():
            p = self.base_dir / p
        return p

    def read_text(self, path: str, encoding: str = "utf-8") -> str:
        file_path = self._resolve(path)
        return file_path.read_text(encoding=encoding)

    def write_text(self, path: str, content: str, encoding: str = "utf-8") -> None:
        file_path = self._resolve(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding=encoding)

    def read_json(self, path: str, encoding: str = "utf-8") -> Dict[str, Any]:
        text = self.read_text(path, encoding=encoding)
        return json.loads(text)

    def write_json(self, path: str, data: Dict[str, Any], encoding: str = "utf-8") -> None:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        self.write_text(path, content, encoding=encoding)

    def ensure_dir(self, path: str) -> None:
        dir_path = self._resolve(path)
        dir_path.mkdir(parents=True, exist_ok=True)

    def file_exists(self, path: str) -> bool:
        """检查文件是否存在"""
        file_path = self._resolve(path)
        return file_path.exists()
