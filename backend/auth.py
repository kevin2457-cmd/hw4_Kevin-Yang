"""Account creation, login, and session tokens for Campus Customs (Problem 4).

Passwords are stored in the same format as the accounts already in the DB:
    pbkdf2_sha256$<salt>$<hex digest>
PBKDF2-HMAC-SHA256, 120,000 iterations, salt used as UTF-8 text.
(Verified against the seeded test account.)
"""

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
import time

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from db import get_db

HASH_ALGORITHM = "pbkdf2_sha256"
HASH_ITERATIONS = 120_000
MIN_PASSWORD_LENGTH = 8
TOKEN_TTL_SECONDS = 7 * 24 * 3600
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Signs login tokens so the frontend can't forge another user's id.
# Set AUTH_SECRET in the environment; the fallback is for local development only.
AUTH_SECRET = os.getenv("AUTH_SECRET", "campus-customs-dev-secret").encode()


# ---------- password hashing ----------

def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(8)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), HASH_ITERATIONS).hex()
    return f"{HASH_ALGORITHM}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, _digest = stored_hash.split("$")
    except ValueError:
        return False
    if algorithm != HASH_ALGORITHM:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored_hash)


# ---------- signed session tokens: "<user_id>.<expires>.<signature>" ----------

def _sign(payload: str) -> str:
    return hmac.new(AUTH_SECRET, payload.encode(), hashlib.sha256).hexdigest()


def create_token(user_id: int) -> str:
    payload = f"{user_id}.{int(time.time()) + TOKEN_TTL_SECONDS}"
    return f"{payload}.{_sign(payload)}"


def user_id_from_token(token: str) -> int | None:
    try:
        user_id, expires, signature = token.split(".")
        if not hmac.compare_digest(_sign(f"{user_id}.{expires}"), signature):
            return None
        if int(expires) < time.time():
            return None
        return int(user_id)
    except ValueError:
        return None


# ---------- API ----------

class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    name: str
    email: str


class AuthResponse(BaseModel):
    token: str
    user: UserOut


def user_out(row: sqlite3.Row) -> UserOut:
    # Older rows may have NULL first/last name; fall back to splitting `name`.
    first, _, last = row["name"].partition(" ")
    return UserOut(
        id=row["id"],
        first_name=row["first_name"] or first,
        last_name=row["last_name"] or last,
        name=row["name"],
        email=row["email"],
    )


def _find_user_by_email(conn: sqlite3.Connection, email: str) -> sqlite3.Row | None:
    return conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()


# ---------- "who is logged in" dependencies (used by /me and the chat routes) ----------

def optional_user(authorization: str = Header(default="")) -> UserOut | None:
    """The logged-in user from the `Authorization: Bearer <token>` header, or None for a guest.
    Identity comes only from the signed token, never from a user_id sent by the browser.
    A token that is present but invalid/expired is a 401, so the frontend can log out."""
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        return None
    user_id = user_id_from_token(token)
    if user_id is None:
        raise HTTPException(401, "Your session has expired. Please log in again.")
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if row is None:
        raise HTTPException(401, "Your session has expired. Please log in again.")
    return user_out(row)


def require_user(user: UserOut | None = Depends(optional_user)) -> UserOut:
    if user is None:
        raise HTTPException(401, "Not logged in.")
    return user


router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(body: RegisterRequest) -> AuthResponse:
    first, last = body.first_name.strip(), body.last_name.strip()
    email = body.email.strip().lower()
    if not (first and last and email and body.password):
        raise HTTPException(400, "Please fill in first name, last name, email, and password.")
    if not EMAIL_RE.match(email):
        raise HTTPException(400, "Please enter a valid email address.")
    if len(body.password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(400, f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")

    with get_db() as conn:
        if _find_user_by_email(conn, email):
            raise HTTPException(409, "An account with this email already exists. Try logging in.")
        try:
            cur = conn.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (f"{first} {last}", email, hash_password(body.password), first, last),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(409, "An account with this email already exists. Try logging in.")
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()
    return AuthResponse(token=create_token(row["id"]), user=user_out(row))


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest) -> AuthResponse:
    email = body.email.strip().lower()
    if not email or not body.password:
        raise HTTPException(400, "Please enter your email and password.")
    with get_db() as conn:
        row = _find_user_by_email(conn, email)
    if row is None:
        raise HTTPException(404, "No account found with that email.")
    if not verify_password(body.password, row["password_hash"]):
        raise HTTPException(401, "Incorrect password. Please try again.")
    return AuthResponse(token=create_token(row["id"]), user=user_out(row))


@router.get("/me", response_model=UserOut)
def me(user: UserOut = Depends(require_user)) -> UserOut:
    return user
