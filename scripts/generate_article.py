import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# 加载 .env 文件
env_path = ROOT / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

from src.workflows.graduation_workflow import GraduationWorkflow


def main() -> None:
    workflow = GraduationWorkflow()
    workflow.run()


if __name__ == "__main__":
    main()
