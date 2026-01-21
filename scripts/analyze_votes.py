import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.file_manager import FileManager

SUMMARY_PATH = "/Users/wy770/Apache/vote_statistics_summary.md"


def parse_summary_counts(text: str) -> dict:
    binding = re.search(r"\*\*\+1 IPMC Binding\*\*\s*\|\s*(\d+)票", text)
    non_binding = re.search(r"\*\*\+1 Non-Binding\*\*\s*\|\s*(\d+)票", text)
    total = re.search(r"\*\*总计\*\*\s*\|\s*\*\*(\d+)票\*\*", text)

    return {
        "binding_plus_one": int(binding.group(1)) if binding else 0,
        "non_binding_plus_one": int(non_binding.group(1)) if non_binding else 0,
        "total": int(total.group(1)) if total else 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="分析 Apache 投票结果")
    parser.add_argument("--thread", default="https://lists.apache.org/thread/djkxttgpj08v74r8rqdv3np856g3krlr", help="投票线程 URL")
    parser.add_argument("--use-summary", action="store_true", help="使用已有的统计摘要文件")
    args = parser.parse_args()

    fm = FileManager("/Users/wy770/Apache")

    try:
        if args.use_summary:
            print("使用已有的统计摘要文件...")
            summary_text = fm.read_text(SUMMARY_PATH)
            counts = parse_summary_counts(summary_text)
            fm.write_text("outputs/statistics/vote_statistics.md", summary_text)
            fm.write_json("outputs/data/vote_data.json", {"summary_counts": counts, "summary_text": summary_text})
            print("统计文件已保存")
            return

        from src.tasks.vote_analyzer import VoteAnalyzer
        from src.core.llm_client import LLMClient

        print("正在分析投票数据...")
        # 初始化 LLM 客户端（如果可用）用于辅助解析
        llm_client = None
        try:
            llm_client = LLMClient()
        except Exception as e:
            print(f"警告: LLM 客户端初始化失败，将仅使用正则表达式: {e}")

        analyzer = VoteAnalyzer(llm_client=llm_client)
        votes = analyzer.analyze_votes(args.thread)
        stats = analyzer.compute_statistics(votes)
        analyzer.save_outputs(votes, stats)
        
        print("=" * 60)
        print("投票分析完成！")
        print(f"总票数: {stats['total']}")
        print(f"统计文件已保存到: outputs/statistics/vote_statistics.md")
        print(f"数据文件已保存到: outputs/data/vote_data.json")
        print("=" * 60)
    except Exception as e:
        print(f"错误: 投票分析失败: {e}")
        raise


if __name__ == "__main__":
    main()
