import os
import shutil
import subprocess
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    repo_dir = project_root / "lighteval"
    target_url = "https://github.com/pjavanrood/lighteval.git"

    if not repo_dir.exists():
        subprocess.check_call(
            [
                "git",
                "clone",
                target_url,
                str(repo_dir),
            ]
        )
    else:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_dir), "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
            )
            current_url = result.stdout.strip()
            if current_url == target_url:
                subprocess.check_call(["git", "-C", str(repo_dir), "pull", "origin", "main"])
            else:
                shutil.rmtree(repo_dir)
                subprocess.check_call(
                    [
                        "git",
                        "clone",
                        target_url,
                        str(repo_dir),
                    ]
                )
        except subprocess.CalledProcessError:
            shutil.rmtree(repo_dir)
            subprocess.check_call(
                [
                    "git",
                    "clone",
                    target_url,
                    str(repo_dir),
                ]
            )

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-e", str(repo_dir)],
        env=os.environ.copy(),
    )


if __name__ == "__main__":
    main()


