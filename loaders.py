import json
import pandas as pd

# -------------------------
# Load JSON file
# -------------------------
def load_json(uploaded_file):
    return json.load(uploaded_file)


# -------------------------
# Load CSV file
# -------------------------
RELATION_MAP = {
    "daughter": "parent",
    "son": "parent",
    "father": "parent",
    "mother": "parent",
    "grandson": "parent",
    "granddaughter": "parent",
    "adoptive grandson": "parent",
    "adoptive granddaughter": "parent",
    "friend": "friend",
    "spouse": "spouse"
}

def load_csv(uploaded_file):
    df = pd.read_csv(uploaded_file)

    characters = {}

    for _, row in df.iterrows():
        character = str(row["character"]).strip()
        relative = str(row["relative"]).strip()
        raw_relation = str(row["relationship"]).lower().strip()

        relation_type = RELATION_MAP.get(raw_relation)
        if not relation_type:
            continue  # skip unsupported relations

        # Ensure both nodes exist
        for name in (character, relative):
            if name not in characters:
                characters[name] = {
                    "name": name,
                    "group": "Unknown",
                    "relations": []
                }

        characters[character]["relations"].append({
            "type": relation_type,
            "target": relative
        })

    return {"characters": list(characters.values())}
