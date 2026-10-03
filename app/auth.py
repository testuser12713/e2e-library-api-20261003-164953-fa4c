"""API-key authentication for the write endpoints.

The ``require_api_key`` dependency reads the ``X-API-Key`` header and rejects
missing or wrong keys with 401.
"""

from fastapi import Header, HTTPException, status

from app.config import API_KEY


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> str:
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger oder fehlender API-Key",
        )
    return x_api_key
