from app.services.ai_recommendations import parse_cocktail_query

result = parse_cocktail_query(
    "Хочу освежающий кислый коктейль, не очень крепкий и без рома"
)

print(result.model_dump_json(indent=2))