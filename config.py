import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    DATABASE_PATH = os.path.join(BASE_DIR, 'attendance.db')
    ASSETS_PATH = os.path.join(BASE_DIR, 'assets')