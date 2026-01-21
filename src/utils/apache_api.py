import re
from typing import Dict, List, Optional

import requests

THREAD_API = "https://lists.apache.org/api/thread.lua"
EMAIL_API = "https://lists.apache.org/api/email.lua"


class ApacheAPIClient:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout

    def get_thread(self, thread_id: str) -> Dict:
        response = requests.get(THREAD_API, params={"id": thread_id}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_email(self, email_id: str) -> Dict:
        response = requests.get(EMAIL_API, params={"id": email_id}, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def extract_thread_id(self, thread_url: str) -> str:
        match = re.search(r"/thread/([a-z0-9]+)", thread_url)
        if not match:
            raise ValueError("Invalid thread URL")
        return match.group(1)

    def collect_email_ids(self, thread_data: Dict) -> List[str]:
        ids: List[str] = []

        def _walk(node: Dict) -> None:
            email_id = node.get("id") or node.get("message_id")
            if email_id:
                ids.append(email_id)
            for child in node.get("children", []) or []:
                _walk(child)

        _walk(thread_data)
        return ids
