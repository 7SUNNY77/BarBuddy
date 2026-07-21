from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

INPUT_PATH = DATA_DIR / "cocktails_final.json"
OUTPUT_PATH = DATA_DIR / "cocktails_normalized.json"
REPORT_PATH = DATA_DIR / "ingredient_normalization_report.json"

ALIASES = {
    "angostura bitters": "Angostura Bitters",
    "fresh cream": "Fresh Cream",
    "fresh lemon juice": "Fresh Lemon Juice",
    "fresh lime": "Fresh Lime",
    "fresh lime juice": "Fresh Lime Juice",
    "fresh orange juice": "Fresh Orange Juice",
    "ginger beer": "Ginger Beer",
    "grenadine syrup": "Grenadine Syrup",
    "simple syrup": "Simple Syrup",
    "soda water": "Soda Water",
    "sugar syrup": "Sugar Syrup",
    "white rum": "White Rum",
    "whiskey": "Whisky",
    "rye whiskey": "Rye Whisky",
    "bourbon whiskey": "Bourbon Whisky",
}


def normalize_key(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(
        char
        for char in value
        if not unicodedata.combining(char)
    )
    value = value.lower().strip()
    value = re.sub(r"\s+", " ", value)
    return value


def canonical_name(name: str) -> str:
    key = normalize_key(name)

    if key in ALIASES:
        return ALIASES[key]

    return name.strip()


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8") as file:
        cocktails = json.load(file)

    changes = []
    names_before = set()
    names_after = set()

    for cocktail in cocktails:
        for ingredient in cocktail["ingredients"]:
            old_name = ingredient["name"]
            new_name = canonical_name(old_name)

            names_before.add(old_name)
            names_after.add(new_name)

            if old_name != new_name:
                changes.append(
                    {
                        "cocktail": cocktail["name_en"],
                        "old_name": old_name,
                        "new_name": new_name,
                    }
                )

                ingredient["name"] = new_name

    report = {
        "unique_ingredients_before": len(names_before),
        "unique_ingredients_after": len(names_after),
        "renamed_entries_count": len(changes),
        "changes": changes,
    }

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(cocktails, file, ensure_ascii=False, indent=2)

    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print("Нормализация ингредиентов завершена.")
    print(f"Уникальных до: {report['unique_ingredients_before']}")
    print(f"Уникальных после: {report['unique_ingredients_after']}")
    print(f"Переименовано записей: {report['renamed_entries_count']}")
    print(f"\nНовый датасет: {OUTPUT_PATH}")
    print(f"Отчёт: {REPORT_PATH}")

    print("\nПервые 15 изменений:")
    for item in changes[:15]:
        print(
            f"- {item['cocktail']}: "
            f"{item['old_name']} -> {item['new_name']}"
        )


if __name__ == "__main__":
    main()