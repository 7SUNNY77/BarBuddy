from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

INPUT_PATH = DATA_DIR / "cocktails_normalized.json"
PROFILES_PATH = DATA_DIR / "cocktail_profiles.json"
OUTPUT_PATH = DATA_DIR / "cocktails_ready.json"


def main() -> None:
    with INPUT_PATH.open(encoding="utf-8") as file:
        cocktails = json.load(file)

    with PROFILES_PATH.open(encoding="utf-8") as file:
        profiles = json.load(file)

    for cocktail in cocktails:
        profile = profiles.get(cocktail["id"], {})

        cocktail["name_ru"] = profile.get(
            "name_ru",
            cocktail.get("name_ru", ""),
        )

        cocktail["instructions_ru"] = profile.get(
            "instructions_ru",
            cocktail.get("instructions_ru", ""),
        )

        cocktail["taste_tags"] = profile.get(
            "taste_tags",
            cocktail.get("taste_tags", []),
        )

        cocktail["taste_description_ru"] = profile.get(
            "taste_description_ru",
            cocktail.get("taste_description_ru", ""),
        )

        cocktail["preparation_time_minutes"] = profile.get(
            "preparation_time_minutes",
            cocktail.get("preparation_time_minutes"),
        )

        cocktail["abv_estimate"] = profile.get(
            "abv_estimate",
            cocktail.get("abv_estimate"),
        )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(cocktails, file, ensure_ascii=False, indent=2)

    profiles_count = sum(
        cocktail["id"] in profiles
        for cocktail in cocktails
    )

    print("Профили объединены.")
    print(f"Всего коктейлей: {len(cocktails)}")
    print(f"Заполнено профилей: {profiles_count}")
    print(f"Файл: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()