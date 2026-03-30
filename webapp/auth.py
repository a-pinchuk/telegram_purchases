from __future__ import annotations

import hashlib
import hmac
import json
from urllib.parse import parse_qs, unquote


def validate_init_data(init_data: str, bot_token: str) -> dict | None:
    """Validate Telegram WebApp initData and return parsed user data.

    See: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
    """
    parsed = parse_qs(init_data, keep_blank_values=True)
    if "hash" not in parsed:
        return None

    received_hash = parsed.pop("hash")[0]

    # Build data-check-string: sorted key=value pairs joined by \n
    data_check_parts = []
    for key in sorted(parsed.keys()):
        val = parsed[key][0]
        data_check_parts.append(f"{key}={val}")
    data_check_string = "\n".join(data_check_parts)

    # Secret key = HMAC-SHA256 of bot token with "WebAppData" as key
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    user_data = parsed.get("user", [None])[0]
    if user_data:
        return json.loads(unquote(user_data))
    return None
