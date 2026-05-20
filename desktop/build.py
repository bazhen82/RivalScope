import shutil
import subprocess
import sys
from pathlib import Path


def build() -> None:
    root = Path(__file__).resolve().parent
    project_root = root.parent
    logo_path = project_root / "frontend" / "assets" / "logo.png"
    if not shutil.which("pyinstaller"):
        print("PyInstaller is not installed. Run: pip install -r requirements.txt")
        sys.exit(1)

    args = [
        "pyinstaller",
        "--name",
        "RivalScope",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--clean",
    ]
    if logo_path.exists():
        args.extend(["--add-data", f"{logo_path};assets"])
    args.append("main.py")

    subprocess.run(args, cwd=root, check=True)


if __name__ == "__main__":
    build()
