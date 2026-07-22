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
- Do not invent cocktails or recipes.
- reason must be one short Russian sentence.
- If a preference is absent, use an empty list or "any".

User request:
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