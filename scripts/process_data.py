import os
import json
import pandas as pd

# 1. Locate and read the JSON data file
data_path = os.path.join("data", "dermstore-skincare-products-and-ingredients-dataset.json") # check if name matches your exact file

if not os.path.exists(data_path):
    # Fallback checking if it saved as a standard name inside the directory
    for file in os.listdir("data"):
        if file.endswith(".json"):
            data_path = os.path.join("data", file)

# Load json using pandas
df = pd.read_json(data_path)

# 2. Basic Data Uniformity Cleaning

# Fill empty rating strings with 0.0 so math sorting functions won't fail
df['rating_value'] = pd.to_numeric(df['rating_value'], errors='coerce').fillna(0.0)
df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0.0)

# Fill empty textual blocks
df['ingredients'] = df['ingredients'].fillna("")
df['category'] = df['category'].fillna("Uncategorized")

# 3. Clean and isolate the raw ingredient text loops
def parse_ingredients(text):
    if not text:
        return []
    # Drop the standard disclaimer line if it is present in the text string
    disclaimer = "For the latest information, it is recommended to review the ingredient list"
    clean_text = text.split(disclaimer)[0]
    
    # Split ingredients by commas, make lowercase, and strip trailing spaces
    raw_list = clean_text.split(",")
    return [item.replace("\n", " ").strip().lower() for item in raw_list if item.strip()]

# Apply the text transformer matrix
df['clean_ingredient_list'] = df['ingredients'].apply(parse_ingredients)

# Print a preview summary
print("\n--- Cleaning Complete ---")
print(f"Total entries loaded: {len(df)}")
print(df[['title', 'brand', 'rating_value', 'clean_ingredient_list']].head(2))

# Save newly cleaned checkpoint out as a dataframe file
df.to_pickle(os.path.join("data", "cleaned_beauty_data.pkl"))
print("\nSaved processed data to data/cleaned_beauty_data.pkl!")
