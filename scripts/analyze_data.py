import os
from collections import Counter
import pandas as pd

# Load clean data
data_file = os.path.join("data", "cleaned_beauty_data.pkl")
if not os.path.exists(data_file):
    print("Error: Cleaned data file missing. Run process_data.py first.")
    exit()

df = pd.read_pickle(data_file)

# =====================================================================
# FEATURE 1: Ingredient Trend Analysis by Skin Concern
# =====================================================================
def analyze_trends_by_concern(df, target_concern):
    print(f"[TREND ANALYSIS] Top Active Ingredients For: '{target_concern}'")
    
    # Filter for products matching the user concern
    concern_mask = df['extracted_concerns'].apply(lambda x: target_concern in x)
    filtered_df = df[concern_mask]
    
    # Unpack individual elements from the nested clean lists
    all_ingredients = [ing for ing_list in filtered_df['clean_ingredient_list'] for ing in ing_list]
    
    # Count frequency weights
    counts = Counter(all_ingredients)
    
    # Skip common base fillers to isolate true active ingredients
    filler_bases = [
        "aqua", "water", "glycerin", "phenoxyethanol", "butylene glycol", 
        "xanthan gum", "disodium edta", "caprylyl glycol", "chlorphenesin"
    ]
    top_actives = [(ing, count) for ing, count in counts.most_common(40) if ing not in filler_bases][:10]
    
    for i, (ing, count) in enumerate(top_actives, 1):
        percentage = (count / len(filtered_df)) * 100
        print(f"  {i}. {ing.title()} (Appears in {percentage:.1f}% of products)")
    print("-" * 60)

# Run trend analysis on two distinct user skin profiles
analyze_trends_by_concern(df, "Acne & Blemishes")
analyze_trends_by_concern(df, "Aging & Wrinkles")


# =====================================================================
# FEATURE 2: Product Rating Comparison (High vs. Low Ratings)
# =====================================================================
print("[COMPARATIVE ANALYSIS] High-Rated vs. Low-Rated Products")

# Segment formulations into high-rated (4.5+) and lower-performing entries (<= 3.5)
high_rated_df = df[df['rating_value'] >= 4.5]
low_rated_df = df[(df['rating_value'] <= 3.5) & (df['rating_value'] > 0)] # Skip unrated items

def get_frequent_ingredients(product_sub_df, top_n=40):
    all_ings = [ing for ing_list in product_sub_df['clean_ingredient_list'] for ing in ing_list]
    return set([ing for ing, _ in Counter(all_ings).most_common(top_n)])

high_top_ingredients = get_frequent_ingredients(high_rated_df)
low_top_ingredients = get_frequent_ingredients(low_rated_df)

# Find ingredients that occur frequently in poorly-rated items but NOT in highly-rated ones
unique_to_low = low_top_ingredients - high_top_ingredients

print(f"Found {len(unique_to_low)} ingredients disproportionately common in lower-rated items:")
if unique_to_low:
    for ing in list(unique_to_low)[:5]:
        print(f"  • {ing.title()}")
else:
    print("  • No unique ingredients found at this threshold—ingredient frequencies are highly similar.")
print("=" * 60)
