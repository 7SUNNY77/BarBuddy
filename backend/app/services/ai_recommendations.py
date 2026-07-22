import json
import os

from google import genai
from pydantic import BaseModel, Field


ALLOWED_TAGS = [
    "сладкий",
    "кислый",
    "цитрусовый",
    "освежающий",
    "лёгкий",
    "крепкий",
    "насыщенный",
    "кофейный",
    "фруктовый",
    "персиковый",
    "ягодный",
    "игристый",
    "горький",
    "пряный",
    "травяной",
    "сливочный",
    "десертный",
]


class CocktailPreferences(BaseModel):
    taste_tags: list[str] = Field(
        description="Only Russian tags from ALLOWED_TAGS"
    )
    include_ingredients: list[str] = Field(
        description="Ingredients explicitly requested by the user"
    )
    exclude_ingredients: list[str] = Field(
        description="Ingredients explicitly excluded by the user"
    )
    strength: str = Field(
        description="One of: light, medium, strong, any"
    )
    reason: str = Field(
        description="One short Russian sentence explaining preferences"
    )


def parse_cocktail_query(query: str) -> CocktailPreferences:
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You extract cocktail preferences from a Russian user request.

Return JSON only, following the provided schema.

Allowed taste_tags:
{", ".join(ALLOWED_TAGS)}

Rules:
- taste_tags may contain only values from Allowed taste_tags.
- strength must be exactly one of: light, medium, strong, any.
- include_ingredients and exclude_ingredients must contain short English
  ingredient categories where possible: rum, vodka, gin, tequila, whiskey,
  coffee, cream, citrus, sparkling_wine.
- Do not invent cocktails, recipes, ingredients, or tags.
- reason must be one short Russian sentence.
- If a preference is absent, use an empty list or "any".

Taste interpretation:
- "кислый", "кисленький", "с кислинкой", "кисленькое" -> "кислый".
- "очень кислый", "максимально кислый", "жёстко кислый",
  "чтобы скулы сводило", "терпкий" -> "кислый".
- "сладкий", "сладенький", "десертный" -> "сладкий".
- "горький", "биттерный", "как негрони" -> "горький".
- "свежий", "освежающий", "летний", "лёгкий" -> "освежающий".
- "кофейный", "с кофе", "как эспрессо" -> "кофейный".
- "фруктовый", "ягодный", "персиковый", "тропический" -> "фруктовый".
- "игристый", "с пузырьками", "шампанское" -> "игристый".
- "сливочный", "молочный", "как десерт" -> "сливочный", "десертный".
- "пряный", "острый", "имбирный", "с перцем" -> "пряный".
- "травяной", "ботанический", "на джине" -> "травяной".

Strength interpretation:
- "лёгкий", "некрепкий", "слабоалкогольный" -> "light".
- "средней крепости", "умеренно крепкий" -> "medium".
- "крепкий", "убойный", "покрепче" -> "strong".
- Do not infer "strong" from "жёстко кислый", "очень кислый",
  "терпкий", "горький" or "острый".
- If strength is not explicitly mentioned, use "any".

Ingredient interpretation:
- "без рома", "не люблю ром", "не с ромом" -> exclude_ingredients: ["rum"].
- "без водки" -> exclude_ingredients: ["vodka"].
- "без джина" -> exclude_ingredients: ["gin"].
- "без текилы" -> exclude_ingredients: ["tequila"].
- "без виски" -> exclude_ingredients: ["whiskey"].
- "без кофе" -> exclude_ingredients: ["coffee"].
- "без сливок", "без молочного" -> exclude_ingredients: ["cream"].
- "без цитрусов", "без лимона", "без лайма" -> exclude_ingredients: ["citrus"].
- "с ромом" -> include_ingredients: ["rum"].
- "с джином" -> include_ingredients: ["gin"].
- "с текилой" -> include_ingredients: ["tequila"].
- "с виски" -> include_ingredients: ["whiskey"].
- "с кофе" -> include_ingredients: ["coffee"].

Examples:

User: "Хочу жёстко кислый, чтобы скулы сводило"
Output intent:
- taste_tags: ["кислый"]
- strength: "any"
- include_ingredients: []
- exclude_ingredients: []

User: "Что-то лёгкое, летнее и с пузырьками"
Output intent:
- taste_tags: ["лёгкий", "освежающий", "игристый"]
- strength: "light"
- include_ingredients: []
- exclude_ingredients: []

User: "Как негрони, но без джина и не слишком горькое"
Output intent:
- taste_tags: ["горький"]
- strength: "medium"
- include_ingredients: []
- exclude_ingredients: ["gin"]

User: "Сладкое кофейное, но без сливок"
Output intent:
- taste_tags: ["сладкий", "кофейный"]
- strength: "any"
- include_ingredients: ["coffee"]
- exclude_ingredients: ["cream"]
{query}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": CocktailPreferences.model_json_schema(),
        },
    )

    return CocktailPreferences.model_validate_json(response.text)