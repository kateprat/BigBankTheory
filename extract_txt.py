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

# ADJUST PATHS
project_root = Path(__file__).resolve().parent
juliusbaer_dir = project_root.parent / "juliusbaer"

# Result dictionary
clients_data = {}

# Loop through the 6 top-level ZIP files
for main_zip_path in juliusbaer_dir.glob("*.zip"):
    with zipfile.ZipFile(main_zip_path, 'r') as main_zip:
        for client_zip_name in main_zip.namelist():
            if not client_zip_name.endswith(".zip"):
                continue
            with main_zip.open(client_zip_name) as client_zip_file:
                client_zip_bytes = io.BytesIO(client_zip_file.read())
                with zipfile.ZipFile(client_zip_bytes, 'r') as client_zip:
                    for name in client_zip.namelist():
                        if "description.txt" in name:
                            with client_zip.open(name) as desc_file:
                                try:
                                    text = desc_file.read().decode("utf-8")
                                except UnicodeDecodeError:
                                    print(f"⚠️ Skipping undecodable file: {name}")
                                    continue
                                parsed = extract_sections(text)
                                # Use the client zip name as the top-level key
                                clients_data[client_zip_name] = {
                                    **parsed,
                                }

# Save to JSON
output_path = project_root / "parsed_clients_by_name.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(clients_data, f, indent=2, ensure_ascii=False)

print(f"✅ Processed {len(clients_data)} clients. Output saved to: {output_path}")
