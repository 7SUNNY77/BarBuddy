import hashlib
import hmac
import json
import os
from datetime import datetime, timezone
from urllib.parse import parse_qsl

import requests
from fastapi import HTTPException


TELEGRAM_API_URL = "https://api.telegram.org"


def get_telegram_user(init_data: str) -> dict | None:
    """
    Возвращает проверенные данные пользователя Mini App.
    Для теста в обычном браузере init_data пустая строка:
    заказ всё равно придёт админу, но без данных пользователя.
    """
    if not init_data:
        return None

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    data = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = data.pop("hash", None)

    if not received_hash:
        raise HTTPException(
            status_code=401,
            detail="Telegram authorization data is missing",
        )

    auth_date = data.get("auth_date")

    try:
        auth_timestamp = int(auth_date)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Telegram authorization data is invalid",
        )

    now = datetime.now(timezone.utc).timestamp()

    if now - auth_timestamp > 3600:
        raise HTTPException(
            status_code=401,
            detail="Telegram authorization data has expired",
        )

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(data.items())
    )

    secret_key = hmac.new(
        b"WebAppData",
        token.encode(),
        hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=401,
            detail="Telegram authorization data is invalid",
        )

    user_json = data.get("user")

    if not user_json:
        return None

    return json.loads(user_json)


def send_order_notification(
    cocktail: dict,
    telegram_user: dict | None,
) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_chat_id = os.getenv("ADMIN_CHAT_ID")

    if not token or not admin_chat_id:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN or ADMIN_CHAT_ID is not configured"
        )

    cocktail_name = (
        cocktail.get("name_ru")
        or cocktail.get("name_en")
        or cocktail["id"]
    )

    ingredients = cocktail.get("ingredients", [])

    ingredient_lines = "\n".join(
        f"• {item.get('name') or item.get('ingredient', 'Ингредиент')} "
        f"{item.get('amount', '')} {item.get('unit', '')}".strip()
        for item in ingredients
    )

    if telegram_user:
        first_name = telegram_user.get("first_name", "Без имени")
        username = telegram_user.get("username")
        user_id = telegram_user.get("id")

        user_line = first_name

        if username:
            user_line += f" (@{username})"

        user_line += f"\nTelegram ID: {user_id}"
    else:
        user_line = "Открыто вне Telegram"

    text = (
        "🍸 <b>Новая заявка BarBuddy</b>\n\n"
        f"<b>Коктейль:</b> {cocktail_name}\n"
        f"<b>Пользователь:</b> {user_line}\n\n"
        f"<b>Ингредиенты:</b>\n{ingredient_lines or 'Не указаны'}"
    )

    response = requests.post(
        f"{TELEGRAM_API_URL}/bot{token}/sendMessage",
        json={
            "chat_id": admin_chat_id,
            "text": text,
            "parse_mode": "HTML",
        },
        timeout=10,
    )

    if not response.ok:
        raise RuntimeError(
            f"Telegram notification failed: {response.text}"
        )