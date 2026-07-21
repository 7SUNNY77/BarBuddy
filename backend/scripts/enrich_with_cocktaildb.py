from __future__ import annotations

import json
import time
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import quote

import requests

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

INPUT_PATH = DATA_DIR / "cocktails.json"
OUTPUT_PATH = DATA_DIR / "cocktails_enriched.json"
REPORT_PATH = DATA_DIR / "cocktaildb_match_report.json"

API_URL = "https://www.thecocktaildb.com/api/json/v1/1/search.php?s="

HEADERS = {
    "User-Agent": "BarBuddy/0.1 educational-project",
}


def normalize_name(value: str) -> str:
    return (
        value.lower()
        .replace("'", "")
        .replace("’", "")
        .replace("-", " ")
        .replace(".", "")
        .strip()
    )


def similarity(first: str, second: str) -> float:
    return SequenceMatcher(
        None,
        normalize_name(first),
        normalize_name(second),
    ).ratio()


def get_candidates(session: requests.Session, name: str) -> list[dict]:
    url = f"{API_URL}{quote(name)}"
    response = session.get(url, headers=HEADERS, timeout=(10, 30))
    response.raise_for_status()

    payload = response.json()
    return payload.get("drinks") or []


def choose_best_match(name: str, candidates: list[dict]) -> tuple[dict | None, float]:
    if not candidates:
        return None, 0.0

    best = max(
        candidates,
        key=lambda item: similarity(name, item.get("strDrink", "")),
    )

    score = similarity(name, best.get("strDrink", ""))
    return best, score


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8") as file:
        cocktails = json.load(file)

    session = requests.Session()
    session.headers.update(HEADERS)

    report = []
    enriched = []

    for index, cocktail in enumerate(cocktails, start=1):
        name = cocktail["name_en"]

        try:
            candidates = get_candidates(session, name)
            match, score = choose_best_match(name, candidates)

        except requests.RequestException as error:
            print(f"[{index}/{len(cocktails)}] Ошибка запроса: {name} — {error}")

            report.append(
                {
                    "name_en": name,
                    "status": "request_error",
                    "error": str(error),
                }
            )

            enriched.append(cocktail)
            time.sleep(1)
            continue

        if match is None or score < 0.78:
            print(f"[{index}/{len(cocktails)}] Не найдено: {name}")

            report.append(
                {
                    "name_en": name,
                    "status": "not_found",
                    "best_score": round(score, 3),
                }
            )

            enriched.append(cocktail)
            time.sleep(1)
            continue

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

        russian_instruction = match.get("strInstructionsRU", "") or ""
        cocktail["instructions_cocktaildb_ru"] = russian_instruction

        enriched.append(cocktail)

        print(
            f"[{index}/{len(cocktails)}] Найдено: "
            f"{name} -> {cocktail['cocktaildb_name']} "
            f"({cocktail['cocktaildb_match_score']})"
        )

        report.append(
            {
                "name_en": name,
                "status": "matched",
                "cocktaildb_name": cocktail["cocktaildb_name"],
                "cocktaildb_id": cocktail["cocktaildb_id"],
                "match_score": cocktail["cocktaildb_match_score"],
            }
        )

        time.sleep(0.4)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(enriched, file, ensure_ascii=False, indent=2)

    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    matched = sum(item["status"] == "matched" for item in report)
    not_found = sum(item["status"] == "not_found" for item in report)
    request_errors = sum(
        item["status"] == "request_error"
        for item in report
    )

    print("\nОбогащение завершено.")
    print(f"Совпадений: {matched}")
    print(f"Не найдено: {not_found}")
    print(f"Ошибок запросов: {request_errors}")
    print(f"Датасет: {OUTPUT_PATH}")
    print(f"Отчёт: {REPORT_PATH}")


if __name__ == "__main__":
    main()