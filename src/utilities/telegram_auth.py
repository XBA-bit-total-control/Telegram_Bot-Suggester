import hashlib
import hmac
import json
import time
from urllib.parse import parse_qsl


def validate_telegram_init_data(
        init_data: str,
        bot_token: str,
        max_age_seconds: int = 3600,
) -> dict:
    """Проверяет подпись и срок действия Telegram initData."""

    if not init_data or not bot_token:
        raise ValueError("Missing init_data or bot token")

    pairs = parse_qsl(
        init_data,
        keep_blank_values=True,
        strict_parsing=True,
    )

    if len(pairs) != len(dict(pairs)):
        raise ValueError("Duplicate initData parameters")

    data = dict(pairs)

    received_hash = data.pop("hash", None)

    if not received_hash:
        raise ValueError("Missing hash")

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(data.items())
    )

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256,
    ).digest()

    expected_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(expected_hash, received_hash):
        raise ValueError("Invalid initData signature")

    try:
        auth_date = int(data["auth_date"])
    except (KeyError, ValueError):
        raise ValueError("Invalid auth_date") from None

    now = int(time.time())

    if auth_date > now + 30:
        raise ValueError("auth_date is in the future")

    if now - auth_date > max_age_seconds:
        raise ValueError("initData has expired")

    try:
        data["user"] = json.loads(data["user"])
    except (KeyError, json.JSONDecodeError):
        raise ValueError("Invalid user data") from None

    return data
