from pathlib import Path
import os


BOT_TOKEN = input("Enter your bot token: ")
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
