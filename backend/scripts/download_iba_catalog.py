from pathlib import Path

import pandas as pd

URL = (
    "https://raw.githubusercontent.com/"
    "rasmusab/iba-cocktails/main/"
    "iba-web/iba-cocktails-web.csv"
)

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data"
CSV_PATH = OUTPUT_DIR / "iba_catalog_raw.csv"
JSON_PATH = OUTPUT_DIR / "iba_catalog_raw.json"


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(URL)

    print("Исходные колонки:")
    print(df.columns.tolist())

    print(f"\nКоличество записей: {len(df)}")

    print("\nПервые 5 строк:")
    print(df.head().to_string(index=False))

    df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    df.to_json(
        JSON_PATH,
        orient="records",
        indent=2,
        force_ascii=False,
    )

    print(f"\nCSV сохранён: {CSV_PATH}")
    print(f"JSON сохранён: {JSON_PATH}")

    for column in ["category", "iba_category", "Category"]:
        if column in df.columns:
            print(f"\nРаспределение по полю {column}:")
            print(df[column].value_counts(dropna=False))
            break


if __name__ == "__main__":
    main()