"""Application configuration loaded from the environment."""

import os

DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./library.db")
API_KEY: str = os.environ["API_KEY"]
