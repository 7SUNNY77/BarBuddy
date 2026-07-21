from __future__ import annotations

import json
import time
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote

import requests

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

DATASET_PATH = DATA_DIR / "cocktails_enriched.json"
REPORT_PATH = DATA_DIR / "cocktaildb_match_report.json"
OUTPUT_PATH = DATA_DIR / "cocktails_enriched_retry.json"
OUTPUT_REPORT_PATH = DATA_DIR / "cocktaildb_match_report_retry.json"

API_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php?s="

ALIASES = {
    "Corpse Reviver #2": "Corpse Reviver",
    "Horse's Neck": "Horse Neck",
    "Long Island Ice Tea": "Long Island Iced Tea",
    "Mai-Tai": "Mai Tai",
    "Bee's Knees": "Bees Knees",
    "Dark ‘n' stormy": "Dark and Stormy",
    "Lemon drop Martini": "Lemon Drop",
    "Planter's Punch": "Planters Punch",
    "Tommy's Margarita": "Tommy Margarita",
    "Vieux Carrè": "Vieux Carre",
    "VE.N.TO": "Vento",
    "Ramos Fizz": "Ramos Gin Fizz",
    "Spritz": "Aperol Spritz",
    "Last word": "The Last Word",
}

HEADERS = {
    "User-Agent": "BarBuddy/0.1 educational-project",
}


def normalize_name(value: str) -> str:
    return (
        value.lower()
        .replace("'", "")
        .replace("’", "")
        .replace("`", "")
        .replace("-", " ")
        .replace(".", "")
        .replace("#", "")
        .strip()
    )


def similarity(first: str, second: str) -> float:
    return SequenceMatcher(
        None,
        normalize_name(first),
        normalize_name(second),
    ).ratio()


def get_candidates(
    session: requests.Session,
    query: str,
) -> list[dict]:
    url = f"{API_URL}{quote(query)}"

    for attempt in range(1, 4):
        try:
            response = session.get(url, timeout=(15, 90))
            response.raise_for_status()
            return response.json().get("drinks") or []

        except requests.RequestException as error:
            print(f"  Попытка {attempt}/3: {error}")

            if attempt < 3:
                time.sleep(attempt * 8)

    return []


def choose_best_match(
    original_name: str,
    candidates: list[dict],
) -> tuple[dict | None, float]:
    if not candidates:
        return None, 0.0

    best = max(
        candidates,
        key=lambda item: similarity(
            original_name,
            item.get("strDrink", ""),
        ),
    )

    score = similarity(
        original_name,
        best.get("strDrink", ""),
    )

    return best, score


def apply_metadata(cocktail: dict, match: dict, score: float) -> None:
    cocktail["cocktaildb_id"] = match.get("idDrink", "")
    cocktail["cocktaildb_name"] = match.get("strDrink", "")
    cocktail["cocktaildb_match_score"] = round(score, 3)
    cocktail["image_url"] = match.get("strDrinkThumb", "")
    cocktail["glass"] = match.get("strGlass", "")
    cocktail["is_alcoholic"] = match.get("strAlcoholic", "")
    cocktail["cocktaildb_tags"] = match.get("strTags", "") or ""
    cocktail["instructions_cocktaildb_en"] = (
        match.get("strInstructions", "") or ""
    )
    cocktail["instructions_cocktaildb_ru"] = (
        match.get("strInstructionsRU", "") or ""
    )


def main() -> None:
    with DATASET_PATH.open(encoding="utf-8") as file:
        cocktails = json.load(file)

    with REPORT_PATH.open(encoding="utf-8") as file:
        report = json.load(file)

    retry_names = {
        item["name_en"]
        for item in report
        if item["status"] in {"request_error", "not_found"}
    }

    print(f"К повторной обработке: {len(retry_names)}")

    session = requests.Session()
    session.headers.update(HEADERS)

    updated_report = []
    matched_count = 0

    for index, cocktail in enumerate(cocktails, start=1):
        name = cocktail["name_en"]

        if name not in retry_names:
            continue

        query = ALIASES.get(name, name)

        print(f"\n[{index}/{len(cocktails)}] {name}")
        print(f"  Поисковый запрос: {query}")

        candidates = get_candidates(session, query)
        match, score = choose_best_match(name, candidates)

        if match is None:
            status = "not_found_after_retry"

            print("  Результат: не найдено")

            updated_report.append(
                {
                    "name_en": name,
                    "search_query": query,
                    "status": status,
                    "match_score": 0.0,
                }
            )

        else:
            apply_metadata(cocktail, match, score)
            matched_count += 1

            status = (
                "matched_after_retry"
                if score >= 0.78
                else "manual_review"
            )

            print(
                f"  Результат: {match.get('strDrink')} "
                f"(score: {score:.3f}, status: {status})"
            )

            updated_report.append(
                {
                    "name_en": name,
                    "search_query": query,
                    "status": status,
                    "cocktaildb_name": match.get("strDrink", ""),
                    "cocktaildb_id": match.get("idDrink", ""),
                    "match_score": round(score, 3),
                }
            )

        time.sleep(3)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(cocktails, file, ensure_ascii=False, indent=2)

    with OUTPUT_REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(updated_report, file, ensure_ascii=False, indent=2)

    review_count = sum(
        item["status"] == "manual_review"
        for item in updated_report
    )

    not_found_count = sum(
        item["status"] == "not_found_after_retry"
        for item in updated_report
    )

    print("\nПовторная обработка завершена.")
    print(f"Новых совпадений: {matched_count}")
    print(f"Требуют ручной проверки: {review_count}")
    print(f"Не найдены после retry: {not_found_count}")
    print(f"Файл: {OUTPUT_PATH}")
    print(f"Отчёт: {OUTPUT_REPORT_PATH}")


if __name__ == "__main__":
    main()