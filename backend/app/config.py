from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_environment() -> None:
    load_dotenv(PROJECT_ROOT / ".env")
