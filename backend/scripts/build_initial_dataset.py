from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

CATALOG_PATH = DATA_DIR / "iba_catalog_raw.csv"

INGREDIENTS_URL = (
    "https://raw.githubusercontent.com/"
    "rasmusab/iba-cocktails/main/"
    "iba-web/iba-cocktails-ingredients-web.csv"
)

OUTPUT_CSV_PATH = DATA_DIR / "cocktails.csv"
OUTPUT_JSON_PATH = DATA_DIR / "cocktails.json"
RAW_INGREDIENTS_PATH = DATA_DIR / "iba_ingredients_raw.csv"


def clean_text(value: object) -> str:
    if pd.isna(value):
        return ""

    return " ".join(str(value).replace("\n", " ").split())


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = value.replace("’", "").replace("'", "")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def build_ingredients_map(
    ingredients_df: pd.DataFrame,
) -> dict[str, list[dict]]:
    ingredients_by_cocktail = {}

    for cocktail_name, group in ingredients_df.groupby("name", dropna=False):
        cocktail_key = clean_text(cocktail_name).lower()
        ingredient_items = []

        for _, row in group.iterrows():
            name = clean_text(row["ingredient"])

            if not name:
                continue

            amount = clean_text(row["quantity"])
            unit = clean_text(row["unit"])
            note = clean_text(row["note"])
            direction = clean_text(row["ingredient_direction"])

            raw = " ".join(
                part
                for part in [amount, unit, name, note]
                if part
            )

            ingredient_items.append(
                {
                    "name": name,
                    "amount": amount,
                    "unit": unit,
                    "note": note,
                    "direction": direction,
                    "raw": raw,
                }
            )

        ingredients_by_cocktail[cocktail_key] = ingredient_items

    return ingredients_by_cocktail


def main() -> None:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"Файл не найден: {CATALOG_PATH}\n"
            "Сначала запусти download_iba_catalog.py"
        )

    cocktails_df = pd.read_csv(CATALOG_PATH)
    ingredients_df = pd.read_csv(INGREDIENTS_URL)

    ingredients_df.to_csv(
        RAW_INGREDIENTS_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    print("Колонки каталога:")
    print(cocktails_df.columns.tolist())

    print("\nКолонки ингредиентов:")
    print(ingredients_df.columns.tolist())

    print(f"\nКоктейлей: {len(cocktails_df)}")
    print(f"Строк ингредиентов: {len(ingredients_df)}")

    ingredients_by_cocktail = build_ingredients_map(ingredients_df)

    records = []

    for _, row in cocktails_df.iterrows():
        name_en = clean_text(row["name"])
        ingredients = ingredients_by_cocktail.get(name_en.lower(), [])

        record = {
            "id": slugify(name_en),
            "name_en": name_en,
            "name_ru": "",
            "iba_category": clean_text(row["category"]),
            "ingredients": ingredients,
            "ingredients_raw": clean_text(row["ingredients"]),
            "instructions_en": clean_text(row["method"]),
            "instructions_ru": "",
            "garnish": clean_text(row["garnish"]),
            "glass": "",
            "abv_estimate": None,
            "preparation_time_minutes": None,
            "taste_tags": [],
            "taste_description_ru": "",
            "image_url": "",
            "source": "IBA",
        }

        records.append(record)

    with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as file:
        json.dump(records, file, ensure_ascii=False, indent=2)

    output_records = []

    for cocktail in records:
        output_records.append(
            {
                "id": cocktail["id"],
                "name_en": cocktail["name_en"],
                "name_ru": cocktail["name_ru"],
                "iba_category": cocktail["iba_category"],
                "ingredients_json": json.dumps(
                    cocktail["ingredients"],
                    ensure_ascii=False,
                ),
                "ingredients_raw": cocktail["ingredients_raw"],
                "instructions_en": cocktail["instructions_en"],
                "instructions_ru": cocktail["instructions_ru"],
                "garnish": cocktail["garnish"],
                "glass": cocktail["glass"],
                "abv_estimate": cocktail["abv_estimate"],
                "preparation_time_minutes": cocktail[
                    "preparation_time_minutes"
                ],
                "taste_tags": json.dumps(
                    cocktail["taste_tags"],
                    ensure_ascii=False,
                ),
                "taste_description_ru": cocktail[
                    "taste_description_ru"
                ],
                "image_url": cocktail["image_url"],
                "source": cocktail["source"],
            }
        )

    pd.DataFrame(output_records).to_csv(
        OUTPUT_CSV_PATH,
        index=False,
        encoding="utf-8-sig",
    )

    ingredient_count = sum(
        len(cocktail["ingredients"])
        for cocktail in records
    )

    ingredients_with_amount = sum(
        bool(ingredient["amount"])
        for cocktail in records
        for ingredient in cocktail["ingredients"]
    )

    print("\nДатасет BarBuddy создан.")
    print(f"JSON: {OUTPUT_JSON_PATH}")
    print(f"CSV: {OUTPUT_CSV_PATH}")
    print(f"Коктейлей без ингредиентов: {sum(not c['ingredients'] for c in records)}")
    print(f"Всего ингредиентов: {ingredient_count}")
    print(f"Ингредиентов с количеством: {ingredients_with_amount}")

    print("\nПример Bellini:")
    bellini = next(
        cocktail
        for cocktail in records
        if cocktail["id"] == "bellini"
    )
    print(json.dumps(bellini["ingredients"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()