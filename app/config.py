"""Application configuration loaded from the environment.

Values are read lazily with safe development defaults. The API key default is a
development convenience only; a real deployment must set ``API_KEY`` explicitly.
"""

import os

DATABASE_URL: str = os.environ.get("DATABASE_URL", "sqlite:///./library.db")
API_KEY: str = os.environ.get("API_KEY", "dev-api-key")
