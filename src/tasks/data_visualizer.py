import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt

from src.core.file_manager import FileManager


class DataVisualizer:
    def __init__(self, file_manager: Optional[FileManager] = None) -> None:
        self.fm = file_manager or FileManager("/Users/wy770/Apache")

    def _parse_vote_counts(self, text: str) -> Tuple[int, int]:
        binding = re.search(r"\*\*\+1 IPMC Binding\*\*\s*\|\s*(\d+)票", text)
        non_binding = re.search(r"\*\*\+1 Non-Binding\*\*\s*\|\s*(\d+)票", text)
        binding_count = int(binding.group(1)) if binding else 0
        non_binding_count = int(non_binding.group(1)) if non_binding else 0
        return binding_count, non_binding_count

    def generate_community_trend(self) -> str:
        # 使用需求报告中的规模信息构造趋势（占位趋势）
        years = [2022, 2023, 2024, 2025, 2026]
        contributors = [20, 60, 120, 180, 210]

        plt.figure(figsize=(8, 4))
        plt.plot(years, contributors, marker="o")
        plt.title("Community Growth Trend")
        plt.xlabel("Year")
        plt.ylabel("Contributors")
        plt.tight_layout()

        output_path = Path("/Users/wy770/Apache/outputs/images/community_trend.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        return str(output_path)

    def generate_release_timeline(self) -> str:
        # 构造版本发布时间线（占位时间线）
        releases = ["1.0", "1.1", "1.2", "1.5", "1.7"]
        dates = [
            datetime(2022, 3, 1),
            datetime(2022, 9, 1),
            datetime(2023, 6, 1),
            datetime(2024, 5, 1),
            datetime(2025, 12, 1),
        ]

        plt.figure(figsize=(8, 2.5))
        plt.scatter(dates, [1] * len(dates))
        for date, rel in zip(dates, releases):
            plt.text(date, 1.02, rel, ha="center", fontsize=9)
        plt.yticks([])
        plt.title("Release Timeline")
        plt.tight_layout()

        output_path = Path("/Users/wy770/Apache/outputs/images/release_timeline.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        return str(output_path)

    def generate_vote_distribution(self) -> str:
        summary = self.fm.read_text("vote_statistics_summary.md")
        binding_count, non_binding_count = self._parse_vote_counts(summary)

        labels = ["Binding +1", "Non-Binding +1"]
        sizes = [binding_count, non_binding_count]

        plt.figure(figsize=(5, 4))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%")
        plt.title("Vote Distribution")
        plt.tight_layout()

        output_path = Path("/Users/wy770/Apache/outputs/images/vote_distribution.png")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        plt.close()
        return str(output_path)
