import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo_dir = project_root / "lighteval"

    if not repo_dir.exists():
        subprocess.check_call(
            [
                "git",
                "clone",
                "https://github.com/huggingface/lighteval.git",
                str(repo_dir),
            ]
        )
    else:
        subprocess.check_call(["git", "-C", str(repo_dir), "pull", "--ff-only"])

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-e", str(repo_dir)],
        env=os.environ.copy(),
    )


if __name__ == "__main__":
    main()


