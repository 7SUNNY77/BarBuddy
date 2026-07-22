import json
from pathlib import Path
from app.ingredient_translations import INGREDIENT_TRANSLATIONS
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(
    prefix="/api/cocktails",
    tags=["Cocktails"],
)

DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "cocktails_ready.json"
)

from app.ingredient_translations import INGREDIENT_TRANSLATIONS


def translate_ingredients(ingredients: list[dict]) -> list[dict]:
    translated = []

    for item in ingredients:
        original_name = (
            item.get("name")
            or item.get("ingredient")
            or ""
        )

        translated.append(
            {
                **item,
                "name": INGREDIENT_TRANSLATIONS.get(
                    original_name,
                    original_name,
                ),
                "ingredient": INGREDIENT_TRANSLATIONS.get(
                    original_name,
                    original_name,
                ),
            }
        )

    return translated

def load_cocktails() -> list[dict]:
    with DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


def to_catalog_card(cocktail: dict) -> dict:
    return {
        "id": cocktail["id"],
        "name_en": cocktail["name_en"],
        "name_ru": cocktail.get("name_ru", ""),
        "iba_category": cocktail["iba_category"],
        "image_url": cocktail.get("image_url", ""),
        "glass": cocktail.get("glass", ""),
        "is_alcoholic": cocktail.get("is_alcoholic", ""),
        "taste_tags": cocktail.get("taste_tags", []),
        "ingredients": [
            {
                **ingredient,
                "ingredient": INGREDIENT_TRANSLATIONS.get(
                    ingredient.get("ingredient", ""),
                    ingredient.get("ingredient", ""),
                ),
            }
            for ingredient in cocktail["ingredients"]
        ],
    }


@router.get("")
def get_cocktails(
    category: str | None = None,
    ingredient: str | None = None,
    q: str | None = Query(default=None, min_length=1),
) -> dict:
    cocktails = load_cocktails()

    if category:
        category_lower = category.lower()

        cocktails = [
            cocktail
            for cocktail in cocktails
            if category_lower in cocktail["iba_category"].lower()
        ]

    if ingredient:
        ingredient_lower = ingredient.lower()

        cocktails = [
            cocktail
            for cocktail in cocktails
            if any(
                ingredient_lower in item["name"].lower()
                for item in cocktail["ingredients"]
            )
        ]

    if q:
        query = q.lower()

        cocktails = [
            cocktail
            for cocktail in cocktails
            if query in cocktail["name_en"].lower()
            or query in cocktail["name_ru"].lower()
        ]

    return {
        "total": len(cocktails),
        "items": [
            to_catalog_card(cocktail)
            for cocktail in cocktails
        ],
    }


@router.get("/{cocktail_id}")
def get_cocktail(cocktail_id: str) -> dict:
    cocktails = load_cocktails()

    cocktail = next(
        (
            item
            for item in cocktails
            if item["id"] == cocktail_id
        ),
        None,
    )

    if cocktail is None:
        raise HTTPException(
            status_code=404,
            detail=f"Коктейль с id '{cocktail_id}' не найден",
        )
    

    return cocktail