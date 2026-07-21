from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

INPUT_PATH = DATA_DIR / "cocktails_enriched_retry.json"
OUTPUT_PATH = DATA_DIR / "cocktails_final.json"
REPORT_PATH = DATA_DIR / "dataset_quality_report.json"

REJECTED_MATCHES = {
    "Martinez",
    "Planter's Punch",
    "Tuxedo",
}


def remove_cocktaildb_metadata(cocktail: dict) -> None:
    fields = [
        "cocktaildb_id",
        "cocktaildb_name",
        "cocktaildb_match_score",
        "image_url",
        "glass",
        "is_alcoholic",
        "cocktaildb_tags",
        "instructions_cocktaildb_en",
        "instructions_cocktaildb_ru",
    ]

    for field in fields:
        cocktail.pop(field, None)


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8") as file:
        cocktails = json.load(file)

    seen_ids = set()
    duplicate_ids = []
    missing_ingredients = []
    missing_instructions = []
    matched = 0
    unmatched = 0
    rejected = []

    for cocktail in cocktails:
        cocktail_id = cocktail["id"]
        name = cocktail["name_en"]

        if cocktail_id in seen_ids:
            duplicate_ids.append(cocktail_id)

        seen_ids.add(cocktail_id)

        if not cocktail["ingredients"]:
            missing_ingredients.append(name)

        if not cocktail["instructions_en"]:
            missing_instructions.append(name)

        if name in REJECTED_MATCHES:
            remove_cocktaildb_metadata(cocktail)
            rejected.append(name)

        if cocktail.get("cocktaildb_id"):
            matched += 1
        else:
            unmatched += 1

    cocktails.sort(
        key=lambda item: (
            item["iba_category"],
            item["name_en"],
        )
    )

    report = {
        "total_cocktails": len(cocktails),
        "cocktaildb_matched": matched,
        "cocktaildb_unmatched": unmatched,
        "rejected_ambiguous_matches": rejected,
        "duplicate_ids": duplicate_ids,
        "cocktails_without_ingredients": missing_ingredients,
        "cocktails_without_instructions": missing_instructions,
        "categories": {},
    }

    for cocktail in cocktails:
        category = cocktail["iba_category"]
        report["categories"][category] = (
            report["categories"].get(category, 0) + 1
        )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(cocktails, file, ensure_ascii=False, indent=2)

    with REPORT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)

    print("Финальный датасет создан.")
    print(f"Всего коктейлей: {report['total_cocktails']}")
    print(f"Совпадений с TheCocktailDB: {report['cocktaildb_matched']}")
    print(f"Без метаданных TheCocktailDB: {report['cocktaildb_unmatched']}")
    print(f"Отклонено неоднозначных совпадений: {len(rejected)}")
    print(f"Дубликатов ID: {len(duplicate_ids)}")
    print(f"Без ингредиентов: {len(missing_ingredients)}")
    print(f"Без инструкций: {len(missing_instructions)}")

    print("\nКатегории:")
    for category, count in report["categories"].items():
        print(f"- {category}: {count}")

    print(f"\nДатасет: {OUTPUT_PATH}")
    print(f"Отчёт: {REPORT_PATH}")


if __name__ == "__main__":
    main()