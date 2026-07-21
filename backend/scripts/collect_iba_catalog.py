from __future__ import annotations

import re
import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://iba-world.com"

CATALOG_URLS = [
    f"{BASE_URL}/cocktails/all-cocktails/",
    f"{BASE_URL}/cocktails/all-cocktails/page/2/",
    f"{BASE_URL}/cocktails/all-cocktails/page/3/",
    f"{BASE_URL}/cocktails/all-cocktails/page/4/",
    f"{BASE_URL}/cocktails/all-cocktails/page/5/",
    f"{BASE_URL}/cocktails/all-cocktails/page/6/",
]

CATEGORY_MAP = {
    "the unforgettables": "The Unforgettables",
    "contemporary classics": "Contemporary Classics",
    "new era": "New Era Drinks",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/138.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data"
CSV_PATH = OUTPUT_DIR / "iba_catalog_raw.csv"
JSON_PATH = OUTPUT_DIR / "iba_catalog_raw.json"


def create_session() -> requests.Session:
    retry = Retry(
        total=4,
        connect=4,
        read=4,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )

    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(HEADERS)

    return session


def slugify(value: str) -> str:
    value = value.lower().replace("’", "").replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def normalize_category(value: str) -> str | None:
    value = " ".join(value.lower().split())

    for source, normalized in CATEGORY_MAP.items():
        if source in value:
            return normalized

    return None


def extract_cocktails(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    cocktails = []

    for heading in soup.find_all(["h2", "h3"]):
        name = heading.get_text(" ", strip=True)

        if not name or name.lower() == "all cocktails":
            continue

        parent = heading.parent
        category = None

        for element in [parent, *heading.parents]:
            context = element.get_text(" ", strip=True)
            category = normalize_category(context)

            if category:
                parent = element
                break

        if category is None:
            continue

        link = parent.find("a", href=True)
        source_url = urljoin(BASE_URL, link["href"]) if link else ""

        cocktails.append(
            {
                "id": slugify(name),
                "name_en": name,
                "name_ru": "",
                "iba_category": category,
                "source_url": source_url,
                "source": "IBA",
            }
        )

    return cocktails


def save_records(records: list[dict]) -> pd.DataFrame:
    df = (
        pd.DataFrame(records)
        .drop_duplicates(subset="name_en")
        .sort_values(["iba_category", "name_en"])
        .reset_index(drop=True)
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    df.to_json(JSON_PATH, orient="records", indent=2, force_ascii=False)

    return df


def main() -> None:
    session = create_session()
    records = []

    for number, url in enumerate(CATALOG_URLS, start=1):
        print(f"\nСтраница {number}/{len(CATALOG_URLS)}: {url}")

        try:
            response = session.get(url, timeout=(15, 120))
            response.raise_for_status()
        except requests.RequestException as error:
            print(f"Не удалось загрузить страницу: {error}")
            print("Пропускаю её. Запусти скрипт ещё раз позже.")
            continue

        page_records = extract_cocktails(response.text)
        records.extend(page_records)

        df = save_records(records)
        print(
            f"Найдено на странице: {len(page_records)}. "
            f"Всего уникальных: {len(df)}."
        )

        time.sleep(3)

    if not records:
        raise RuntimeError(
            "Не удалось загрузить ни одной страницы. "
            "Проверь сайт IBA в браузере и повтори запуск позже."
        )

    df = save_records(records)

    print("\nСбор завершён.")
    print(f"Уникальных коктейлей: {len(df)}")
    print("\nРаспределение по категориям:")
    print(df["iba_category"].value_counts())
    print(f"\nCSV: {CSV_PATH}")
    print(f"JSON: {JSON_PATH}")


if __name__ == "__main__":
    main()