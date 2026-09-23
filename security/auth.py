"""
Authentication module for establishing user identity.
Implements signed token creation, verification, and FastAPI security dependency.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone
import base64
import hashlib
import hmac
import json
import time
from pydantic import BaseModel, Field
from fastapi import Header, HTTPException, status

# Default development secret key (can be overridden via environment)
AUTH_SECRET_KEY = "dev-insecure-secret-key-change-in-production"
TOKEN_EXPIRY_SECONDS = 3600  # 1 hour


class UserPrincipal(BaseModel):
    user_id: int
    username: str
    email: str
    role: str = "viewer"  # viewer, agent, manager, admin
    department: str = "General"
    extra_permissions: list[str] = Field(default_factory=list)


def _b64_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64_decode(data: str) -> bytes:
    padding = "=" * ((4 - len(data) % 4) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_access_token(
    user_id: int,
    username: str,
    email: str,
    role: str = "viewer",
    department: str = "General",
    secret_key: str = AUTH_SECRET_KEY,
    expires_in: int = TOKEN_EXPIRY_SECONDS,
) -> str:
    """Creates an HMAC-SHA256 signed bearer token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user_id),
        "username": username,
        "email": email,
        "role": role,
        "department": department,
        "exp": int(time.time()) + expires_in,
        "iat": int(time.time()),
    }

    header_b64 = _b64_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64_encode(json.dumps(payload).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64_encode(signature)

    return f"{header_b64}.{payload_b64}.{sig_b64}"


def authenticate_token(token: str, secret_key: str = AUTH_SECRET_KEY) -> UserPrincipal:
    """Verifies HMAC signature, validates expiration, and returns UserPrincipal."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    parts = token.strip().split(".")
    if len(parts) != 3:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token format.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(secret_key.encode("utf-8"), signing_input, hashlib.sha256).digest()

    try:
        actual_sig = _b64_decode(sig_b64)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature encoding.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not hmac.compare_digest(expected_sig, actual_sig):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = json.loads(_b64_decode(payload_b64).decode("utf-8"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload JSON.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    now = int(time.time())
    if "exp" in payload and payload["exp"] < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return UserPrincipal(
        user_id=int(payload.get("sub", 0)),
        username=payload.get("username", "anonymous"),
        email=payload.get("email", ""),
        role=payload.get("role", "viewer"),
        department=payload.get("department", "General"),
    )


def get_current_user(authorization: Optional[str] = Header(None)) -> UserPrincipal:
    """FastAPI dependency to extract Bearer token and authenticate caller."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Must be 'Bearer <token>'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization[7:].strip()
    return authenticate_token(token)
