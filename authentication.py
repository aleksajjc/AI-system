import base64
import json
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from supabase import Client, ClientOptions, SupabaseException, create_client

load_dotenv()


class AuthConfigurationError(Exception):
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
