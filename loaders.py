import json
import pandas as pd


def load_csv(file):
    df = pd.read_csv(file)

    required = {"character", "relationship", "relative"}
    if not required.issubset(df.columns):
        raise ValueError("CSV must contain character, relationship, relative")

    records = []
    for _, row in df.iterrows():
        records.append({
            "character": str(row["character"]).strip(),
            "relationship": str(row["relationship"]).strip().lower(),
            "relative": str(row["relative"]).strip()
        })

    return records


def load_json(file):
    data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("JSON must be a list")

    records = []
    for item in data:
        records.append({
            "character": str(item["character"]).strip(),
            "relationship": str(item["relationship"]).strip().lower(),
            "relative": str(item["relative"]).strip()
        })

    return records
