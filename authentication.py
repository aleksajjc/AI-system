import base64
import json
import os
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from supabase import Client, ClientOptions, SupabaseException, create_client
from supabase_auth.errors import AuthApiError

load_dotenv()


class AuthConfigurationError(Exception):
    pass


class AuthRejectedError(Exception):
    pass


class AuthUnavailableError(Exception):
    pass


def _key_role(key: str):
    try:
        parts = key.split(".")
        if len(parts) != 3:
            return None
        payload = parts[1] + "=" * (-len(parts[1]) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode("ascii"))
        decoded_payload = json.loads(decoded.decode("utf-8"))
        return decoded_payload.get("role") if isinstance(decoded_payload, dict) else None
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def supabase_settings():
    url = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
    key = os.getenv("SUPABASE_KEY", "").strip()

    if not url or not key or "your-project-ref" in url or key == "your_supabase_anon_key":
        raise AuthConfigurationError

    parsed_url = urlparse(url)
    hostname = (parsed_url.hostname or "").lower()
    if (
        parsed_url.scheme != "https"
        or not hostname.endswith(".supabase.co")
        or parsed_url.username
        or parsed_url.password
        or parsed_url.query
        or parsed_url.fragment
        or parsed_url.path not in ("", "/")
    ):
        raise AuthConfigurationError

    if key.startswith("sb_secret_") or _key_role(key) == "service_role":
        raise AuthConfigurationError

    return url, key


def create_supabase_client() -> Client:
    url, key = supabase_settings()
    try:
        return create_client(
            url,
            key,
            options=ClientOptions(
                auto_refresh_token=False,
                persist_session=False,
            ),
        )
    except SupabaseException as exc:
        raise AuthConfigurationError from exc


def safe_user(user):
    created_at = getattr(user, "created_at", None)
    if hasattr(created_at, "isoformat"):
        created_at = created_at.isoformat()

    return {
        "id": str(user.id),
        "email": user.email,
        "created_at": created_at,
    }


def sign_up(email: str, password: str):
    try:
        response = create_supabase_client().auth.sign_up(
            {"email": email, "password": password}
        )
    except AuthApiError as exc:
        raise AuthRejectedError from exc
    except httpx.HTTPError as exc:
        raise AuthUnavailableError from exc

    if response is None or response.user is None:
        raise AuthRejectedError

    return safe_user(response.user)


def sign_in(email: str, password: str):
    try:
        response = create_supabase_client().auth.sign_in_with_password(
            {"email": email, "password": password}
        )
    except AuthApiError as exc:
        raise AuthRejectedError from exc
    except httpx.HTTPError as exc:
        raise AuthUnavailableError from exc

    if response.session is None:
        raise AuthRejectedError

    return {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
    }


def verify_access_token(token: str):
    try:
        response = create_supabase_client().auth.get_user(token)
    except AuthApiError as exc:
        raise AuthRejectedError from exc
    except httpx.HTTPError as exc:
        raise AuthUnavailableError from exc

    if response is None or response.user is None:
        raise AuthRejectedError

    return safe_user(response.user)
