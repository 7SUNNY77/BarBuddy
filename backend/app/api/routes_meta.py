import json
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/meta",
    tags=["Metadata"],
)

DATA_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "cocktails_ready.json"
)


def load_cocktails() -> list[dict]:
    with DATA_PATH.open(encoding="utf-8") as file:
        return json.load(file)


@router.get("/filters")
def get_filters() -> dict:
    cocktails = load_cocktails()

    categories = sorted(
        {
            cocktail["iba_category"]
            for cocktail in cocktails
        }
    )

    ingredients = sorted(
        {
            ingredient["name"]
            for cocktail in cocktails
            for ingredient in cocktail["ingredients"]
        }
    )

    alcohol_types = sorted(
        {
            cocktail.get("is_alcoholic", "")
            for cocktail in cocktails
            if cocktail.get("is_alcoholic", "")
        }
    )

    return {
        "categories": categories,
        "ingredients": ingredients,
        "alcohol_types": alcohol_types,
        "total_cocktails": len(cocktails),
    }