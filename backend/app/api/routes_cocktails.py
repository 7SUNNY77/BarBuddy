import json
from pathlib import Path
from app.ingredient_translations import INGREDIENT_TRANSLATIONS
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.services.telegram_orders import (
    get_telegram_user,
    send_order_notification,
)
from fastapi import APIRouter, HTTPException, Query, Request
from app.services.ai_recommendations import parse_cocktail_query
from app.limiter import limiter

router = APIRouter(
    prefix="/api/cocktails",
    tags=["Cocktails"],
)



class RecommendationRequest(BaseModel):
    query: str = Field(min_length=3, max_length=300)

class OrderRequest(BaseModel):
    cocktail_id: str = Field(min_length=1, max_length=100)
    init_data: str = Field(default="", max_length=4096)

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
        "ingredients": translate_ingredients(
            cocktail.get("ingredients", [])
        ),
    }

INGREDIENT_ALIASES = {
    "rum": ["rum", "rhum", "ron", "cachaça"],
    "vodka": ["vodka"],
    "gin": ["gin"],
    "tequila": ["tequila", "mezcal"],
    "whiskey": ["whiskey", "whisky", "bourbon", "scotch", "rye"],
    "coffee": ["coffee", "espresso", "kahlúa", "coffee liqueur"],
    "cream": ["cream", "milk", "egg white"],
    "citrus": ["lime", "lemon", "orange", "grapefruit"],
    "sparkling_wine": ["champagne", "prosecco", "sparkling wine"],
}


def get_ingredient_names(cocktail: dict) -> list[str]:
    return [
        (
            item.get("name")
            or item.get("ingredient")
            or ""
        ).lower()
        for item in cocktail.get("ingredients", [])
    ]


def has_ingredient_group(
    ingredient_names: list[str],
    group: str,
) -> bool:
    aliases = INGREDIENT_ALIASES.get(group.lower(), [group.lower()])

    return any(
        alias in ingredient_name
        for ingredient_name in ingredient_names
        for alias in aliases
    )


def get_cocktail_tags(cocktail: dict) -> list[str]:
    tags = cocktail.get("taste_tags", [])

    if isinstance(tags, str):
        tags = tags.split(",")

    return [
        str(tag).strip().lower()
        for tag in tags
        if str(tag).strip()
    ]


def get_cocktail_text(cocktail: dict) -> str:
    values = [
        cocktail.get("name_en", ""),
        cocktail.get("name_ru", ""),
        cocktail.get("taste_description_ru", ""),
        cocktail.get("instructions_ru", ""),
        cocktail.get("instructions_en", ""),
        cocktail.get("iba_category", ""),
    ]

    return " ".join(
        str(value).lower()
        for value in values
        if value
    )


def matches_strength(cocktail: dict, strength: str) -> bool:
    if strength == "any":
        return True

    abv = cocktail.get("abv_estimate")

    if abv is None:
        return True

    try:
        abv = float(abv)
    except (TypeError, ValueError):
        return True

    if strength == "light":
        return abv <= 15

    if strength == "medium":
        return 15 < abv <= 25

    if strength == "strong":
        return abv > 25

    return True


def rank_cocktails(
    cocktails: list[dict],
    preferences,
) -> list[dict]:
    ranked = []

    for cocktail in cocktails:
        ingredient_names = get_ingredient_names(cocktail)

        if any(
            has_ingredient_group(ingredient_names, group)
            for group in preferences.exclude_ingredients
        ):
            continue

        score = 0
        tags = get_cocktail_tags(cocktail)
        searchable_text = get_cocktail_text(cocktail)

        for group in preferences.include_ingredients:
            if has_ingredient_group(ingredient_names, group):
                score += 4

        matched_taste_tags = 0

        for wanted_tag in preferences.taste_tags:
            wanted_tag = wanted_tag.lower()

            if wanted_tag in tags:
                score += 6
                matched_taste_tags += 1

            if wanted_tag in searchable_text:
                score += 2

        for group in preferences.include_ingredients:
            if has_ingredient_group(ingredient_names, group):
                score += 4

        if matches_strength(cocktail, preferences.strength):
            score += 2
        elif preferences.strength != "any":
            score -= 2

        # Если пользователь явно указал вкус — коктейль обязан
        # совпасть хотя бы с одним вкусовым тегом.
        if preferences.taste_tags and matched_taste_tags == 0:
            continue

        ranked.append(
            {
                "cocktail": cocktail,
                "score": score,
            }
        )

        ranked.append(
            {
                "cocktail": cocktail,
                "score": score,
            }
        )

    ranked.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    unique_cocktails = []
    seen_names = set()

    for item in ranked:
        cocktail = item["cocktail"]

        unique_key = (
            cocktail.get("name_en")
            or cocktail.get("name_ru")
            or cocktail.get("id")
        ).strip().lower()

        if unique_key in seen_names:
            continue

        seen_names.add(unique_key)
        unique_cocktails.append(cocktail)

        if len(unique_cocktails) == 3:
            break

    return unique_cocktails


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

@router.post("/recommendations")
@limiter.limit("1/7seconds")
def get_ai_recommendations(
    request: Request,
    payload: RecommendationRequest,
):
    try:
        preferences = parse_cocktail_query(payload.query)
    except Exception:
        raise HTTPException(
            status_code=503,
            detail="AI recommendation service is temporarily unavailable",
        )

    cocktails = load_cocktails()

    recommendations = rank_cocktails(
        cocktails,
        preferences,
    )

    return {
        "query": payload.query,
        "reason": preferences.reason,
        "preferences": preferences.model_dump(),
        "total": len(recommendations),
        "recommendations": [
            to_catalog_card(cocktail)
            for cocktail in recommendations
        ],
    }

@router.post("/orders")
@limiter.limit("1/7seconds")
def create_order(
    request: Request,
    payload: OrderRequest,
) -> dict:
    cocktails = load_cocktails()

    cocktail = next(
        (
            item
            for item in cocktails
            if item["id"] == payload.cocktail_id
        ),
        None,
    )

    if cocktail is None:
        raise HTTPException(
            status_code=404,
            detail="Коктейль не найден",
        )

    try:
        telegram_user = get_telegram_user(payload.init_data)

        send_order_notification(
            cocktail=cocktail,
            telegram_user=telegram_user,
        )
    except HTTPException:
        raise
    except Exception as error:
        print(f"Order notification error: {error}")

        raise HTTPException(
            status_code=503,
            detail="Не удалось отправить заявку",
        )

    return {
        "message": (
            "Заявка отправлена — если бар работает и хватает "
            "ингредиентов, то приготовим."
        )
    }