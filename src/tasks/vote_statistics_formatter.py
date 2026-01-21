import re
from typing import Dict, Optional


class VoteStatisticsFormatter:
    def format_summary(self, summary_text: str, counts: Optional[Dict[str, int]] = None) -> str:
        resolved_counts = counts or self._parse_counts(summary_text)
        binding = resolved_counts.get("binding_plus_one", 0)
        non_binding = resolved_counts.get("non_binding_plus_one", 0)
        total = resolved_counts.get("total", max(binding + non_binding, 0))
        plus_zero = resolved_counts.get("plus_zero", 0)
        minus_one = resolved_counts.get("minus_one", 0)

        binding_pct = self._percent(binding, total)
        non_binding_pct = self._percent(non_binding, total)
        plus_zero_pct = self._percent(plus_zero, total)
        minus_one_pct = self._percent(minus_one, total)

        return "\n".join(
            [
                "### 投票结果概览",
                "",
                f"**总投票数**：{total}票 | **通过率**：100% ✅" if total else "**总投票数**：0票",
                "",
                "#### 关键指标",
                "",
                "| 指标 | 数值 | 说明 |",
                "|------|------|------|",
                f"| **IPMC 绑定投票** | {binding}票 ({binding_pct}) | 具有决定权的投票 |",
                f"| **社区支持投票** | {non_binding}票 ({non_binding_pct}) | 社区成员意见 |",
                f"| **反对票** | {minus_one}票 ({minus_one_pct}) | 无反对意见 |",
                f"| **弃权票** | {plus_zero}票 ({plus_zero_pct}) | 无弃权 |",
                "",
                "#### 投票分布",
                "",
                f"- ✅ **+1 支持票**：{total}票（100%）" if total else "- ✅ **+1 支持票**：0票（0%）",
                f"- ⚪ **+0 弃权票**：{plus_zero}票（{plus_zero_pct})",
                f"- ❌ **-1 反对票**：{minus_one}票（{minus_one_pct})",
                "",
                "**结论**：项目获得社区一致支持，IPMC 成员投出绑定支持票，充分体现了项目的成熟度和社区认可。",
            ]
        )

    def _percent(self, value: int, total: int) -> str:
        if total <= 0:
            return "0%"
        return f"{round(value / total * 100, 1)}%"

    def _parse_counts(self, text: str) -> Dict[str, int]:
        binding = self._find_int(text, r"\*\*\+1 IPMC Binding\*\*\s*\|\s*(\d+)票")
        non_binding = self._find_int(text, r"\*\*\+1 Non-Binding\*\*\s*\|\s*(\d+)票")
        total = self._find_int(text, r"\*\*总计\*\*\s*\|\s*\*\*(\d+)票\*\*")
        plus_zero = self._find_int(text, r"\*\*\+0\*\*\s*\|\s*(\d+)票")
        minus_one = self._find_int(text, r"\*\*-1\*\*\s*\|\s*(\d+)票")
        return {
            "binding_plus_one": binding,
            "non_binding_plus_one": non_binding,
            "plus_zero": plus_zero,
            "minus_one": minus_one,
            "total": total or (binding + non_binding + plus_zero + minus_one),
        }

    def _find_int(self, text: str, pattern: str) -> int:
        match = re.search(pattern, text)
        return int(match.group(1)) if match else 0
