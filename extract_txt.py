import zipfile
from pathlib import Path
import io
import re
import json

# Section headers to parse
SECTION_HEADERS = [
    "Summary Note:",
    "Family Background:",
    "Occupation History:",
    "Wealth Summary:",
    "Client Summary:"
]

# Function to parse description.txt into a structured dict
def extract_sections(text):
    pattern = r"(?P<header>" + "|".join(re.escape(h) for h in SECTION_HEADERS) + r")"
    parts = re.split(pattern, text)
    result = {h: "" for h in SECTION_HEADERS}
    for i in range(1, len(parts) - 1, 2):
        header = parts[i].strip()
        content = parts[i + 1].strip()
        result[header] = content
    return result

# Paths
project_root = Path(__file__).resolve().parent
zip_path = project_root / "client_data.zip"

# Result dictionary
clients_data = {}

# Open client_data.zip
with zipfile.ZipFile(zip_path, 'r') as zip_file:
    # Find all paths that look like client folders with description.txt inside
    for file_path in zip_file.namelist():
        if file_path.endswith("description.txt") and file_path.count("/") == 2:
            client_folder = file_path.split("/")[1]  # e.g., 'client045' from 'client_data/client045/description.txt'
            try:
                with zip_file.open(file_path) as desc_file:
                    text = desc_file.read().decode("utf-8")
                    parsed = extract_sections(text)
                    clients_data[client_folder] = parsed
            except Exception as e:
                print(f"⚠️ Failed to process {file_path}: {e}")

# Save to JSON
output_path = project_root / "parsed_clients_by_folder.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(clients_data, f, indent=2, ensure_ascii=False)

print(f"✅ Parsed {len(clients_data)} clients. Output saved to: {output_path}")
