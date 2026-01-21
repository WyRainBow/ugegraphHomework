import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.core.file_manager import FileManager
from src.tasks.vote_analyzer import VoteAnalyzer
from src.core.llm_client import LLMClient
from src.workflows.graduation_workflow import GraduationWorkflow


def main() -> None:
    """
    执行所有任务：投票分析 + 文章生成
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="执行所有任务：投票分析和文章生成")
    parser.add_argument("--use-summary", action="store_true", help="使用已有的统计摘要文件")
    parser.add_argument("--thread", default="https://lists.apache.org/thread/djkxttgpj08v74r8rqdv3np856g3krlr", help="投票线程 URL")
    args = parser.parse_args()
    
    fm = FileManager("/Users/wy770/Apache")
    
    try:
        # 步骤1: 投票分析
        print("=" * 60)
        print("步骤 1/2: 分析投票数据")
        print("=" * 60)
        
        if args.use_summary:
            print("使用已有的统计摘要文件...")
            import re
            SUMMARY_PATH = "/Users/wy770/Apache/vote_statistics_summary.md"
            summary_text = fm.read_text(SUMMARY_PATH)
            
            binding = re.search(r"\*\*\+1 IPMC Binding\*\*\s*\|\s*(\d+)票", summary_text)
            non_binding = re.search(r"\*\*\+1 Non-Binding\*\*\s*\|\s*(\d+)票", summary_text)
            total = re.search(r"\*\*总计\*\*\s*\|\s*\*\*(\d+)票\*\*", summary_text)
            
            counts = {
                "binding_plus_one": int(binding.group(1)) if binding else 0,
                "non_binding_plus_one": int(non_binding.group(1)) if non_binding else 0,
                "total": int(total.group(1)) if total else 0,
            }
            
            fm.write_text("outputs/statistics/vote_statistics.md", summary_text)
            fm.write_json("outputs/data/vote_data.json", {"summary_counts": counts, "summary_text": summary_text})
            print("统计文件已保存")
        else:
            print("正在分析投票数据...")
            llm_client = None
            try:
                llm_client = LLMClient()
            except Exception as e:
                print(f"警告: LLM 客户端初始化失败，将仅使用正则表达式: {e}")
            
            analyzer = VoteAnalyzer(llm_client=llm_client)
            votes = analyzer.analyze_votes(args.thread)
            stats = analyzer.compute_statistics(votes)
            analyzer.save_outputs(votes, stats)
            
            print(f"总票数: {stats['total']}")
            print("统计文件已保存")
        
        # 步骤2: 文章生成
        print("\n" + "=" * 60)
        print("步骤 2/2: 生成文章")
        print("=" * 60)
        
        workflow = GraduationWorkflow()
        workflow.run()
        
        print("\n" + "=" * 60)
        print("所有任务执行完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n错误: 任务执行失败: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
