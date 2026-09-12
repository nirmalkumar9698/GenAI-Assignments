import json

# Load the scraped JSON file
with open("farmer_schemes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Display total count
print(f"====================================")
print(f"Total Schemes Scraped: {len(data)}")
print(f"====================================\n")

# Display the title of every scraped scheme
print("Scraped Scheme Names:")
for idx, scheme in enumerate(data, 1):
    print(f"{idx}. {scheme.get('scheme_name')}")

# Print full raw data of the first scheme as an example
print("\n--- Sample Scraped Entry (Scheme #1) ---")
print(json.dumps(data[0], indent=2, ensure_ascii=False))