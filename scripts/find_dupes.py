import os
import pandas as pd

# Load the clean data
data_file = os.path.join("data", "cleaned_beauty_data.pkl")
if not os.path.exists(data_file):
    print("Error: Run other py files first.")
    exit()

df = pd.read_pickle(data_file)

def find_dupes(product_title, dataset):
    # Find our target product row
    target_row = dataset[dataset['title'].str.contains(product_title, case=False, na=False)]
    
    if target_row.empty:
        print(f"Could not find a product matching '{product_title}' in the database.")
        return
        
    target_product = target_row.iloc[0]
    target_ingredients = set(target_product['clean_ingredient_list'])
    target_top_5 = target_product['clean_ingredient_list'][:5]
    
    print(f"Finding alternatives for: '{target_product['title']}' by {target_product['brand']}")
    print(f"Original Price: ${target_product['price']}")
    print("=" * 60)
    
    # Loop through all other products to evaluate similarity
    results = []
    for idx, row in dataset.iterrows():
        if row['title'] == target_product['title']:
            continue # Skip comparing the product to itself
            
        candidate_ingredients = set(row['clean_ingredient_list'])
        candidate_top_5 = row['clean_ingredient_list'][:5]
        
        if not candidate_ingredients:
            continue
            
        # Calculate intersection overlap metrics
        shared_ingredients = target_ingredients.intersection(candidate_ingredients)
        overlap_percentage = (len(shared_ingredients) / len(target_ingredients)) * 100
        
        # Determine 3-Level Tier Logic using new clean labels
        top_5_match_count = len(set(target_top_5).intersection(set(candidate_top_5)))
        
        if overlap_percentage >= 80 and top_5_match_count >= 4:
            tier = "Great Match"
        elif overlap_percentage >= 55:
            tier = "Okay Match"
        elif overlap_percentage >= 35:
            tier = "Low Match"
        else:
            continue # Skip exceptionally weak matches
            
        results.append({
            "title": row['title'],
            "brand": row['brand'],
            "price": row['price'],
            "overlap": overlap_percentage,
            "tier": tier
        })
        
    results_df = pd.DataFrame(results)
    if results_df.empty:
        print("No notable matches found in this sample batch.")
        return
        
    # Sort results by overlap percentage
    results_df = results_df.sort_values(by="overlap", ascending=False)
    
    # Print out findings grouped by new consumer tier labels
    for tier_name, group in results_df.groupby("tier", sort=False):
        print(f"\n{tier_name}")
        for _, match in group.head(3).iterrows():
            print(f"  • [{match['brand']}] {match['title']} - ${match['price']} ({match['overlap']:.1f}% ingredient overlap)")
    print("=" * 60)

# Test algorithm on finding dupes
find_dupes("Doctor Rogers Night Repair", df)


