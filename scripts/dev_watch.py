import os
import subprocess
import sys
from pathlib import Path

from watchfiles import run_process


ROOT = Path(__file__).resolve().parents[1]
BOT_PATH = ROOT / "bots" / "whatsapp" / "bot.py"
WATCH_PATHS = [
    ROOT / "bot_core",
    ROOT / "bots" / "whatsapp",
    ROOT / "scripts",
]


def _run_bot() -> None:
    env = os.environ.copy()
    env.setdefault("DATABASE_URL", "sqlite:///bot.db")
    env.setdefault("TESTING", "false")
    env.setdefault("PYTHONPATH", ".")
    subprocess.run([sys.executable, str(BOT_PATH)], cwd=str(ROOT), env=env, check=False)


if __name__ == "__main__":
    run_process(*(str(p) for p in WATCH_PATHS), target=_run_bot)
