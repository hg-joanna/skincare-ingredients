import os
import pandas as pd
import gradio as gr
from collections import Counter

# Load the clean data
data_file = os.path.join("data", "cleaned_beauty_data.pkl")
if not os.path.exists(data_file):
    print("Error: Cleaned data file missing. Run scripts/process_data.py first.")
    exit()

df = pd.read_pickle(data_file)
product_list = sorted(df['title'].tolist())

# =====================================================================
# INGREDIENT TREND EXPLORER
# =====================================================================
def get_ingredient_trends(concern):
    concern_mask = df['extracted_concerns'].apply(lambda x: concern in x)
    filtered_df = df[concern_mask]
    
    if filtered_df.empty:
        return f"<p style='color: #cc0000 !important; font-weight: bold;'>No products matching '{concern}' found.</p>", None
    
    # Calculate ingredient frequencies
    all_ingredients = [ing for ing_list in filtered_df['clean_ingredient_list'] for ing in ing_list]
    counts = Counter(all_ingredients)
    
    filler_bases = ["aqua", "water", "glycerin", "phenoxyethanol", "butylene glycol", "xanthan gum", "disodium edta", "caprylyl glycol", "chlorphenesin"]
    top_actives = [(ing.title(), count) for ing, count in counts.most_common(40) if ing not in filler_bases][:10]
    
    plot_df = pd.DataFrame(top_actives, columns=["Ingredient", "Frequency"])
    
    # Render scrollable product list panel with explicit high-contrast rules
    prod_summary_html = f"""
    <div style='background-color: #fafbfc; border: 1px solid #cbd5e0; padding: 15px; border-radius: 8px;'>
        <h4 style='margin-top: 0; color: #000000 !important; font-weight: bold;'>🛒 Formulations Matching This Profile ({len(filtered_df)} items):</h4>
        <div style='max-height: 400px; overflow-y: auto; padding-right: 10px;'>
    """
    
    for idx, row in filtered_df.iterrows():
        stars = "⭐" * int(round(row['rating_value'])) if row['rating_value'] > 0 else "Unrated"
        prod_summary_html += f"""
        <div style='padding: 12px; background: #ffffff; border: 1px solid #cbd5e0; margin-bottom: 8px; border-radius: 6px; color: #000000 !important;'>
            <b style='color: #1a56db !important; font-size: 14px;'>[{row['brand']}] {row['title']}</b><br>
            <span style='color: #000000 !important; font-weight: bold; font-size: 14px;'>Price: ${row['price']}</span><br>
            <small style='color: #2d3748 !important; font-weight: 500;'>Consumer Rating: {stars} ({row['rating_value']} stars)</small><br>
            <span style='font-size: 13px; color: #4a5568 !important; display: block; margin-top: 4px;'><b>Ingredients:</b> {', '.join(row['clean_ingredient_list'][:10])}...</span>
        </div>
        """
        
    prod_summary_html += "</div></div>"
    return prod_summary_html, plot_df

# =====================================================================
# SIMILARITY MATCHER
# =====================================================================
def match_skincare_dupes(selected_title):
    if not selected_title:
        return "<p style='color: #000000 !important; font-weight: bold;'>Please select a product above.</p>"
    
    target_row = df[df['title'] == selected_title]
    if target_row.empty:
        return "<p style='color: #cc0000 !important; font-weight: bold;'>Product not found.</p>"
        
    target_product = target_row.iloc[0]
    target_ingredients = set(target_product['clean_ingredient_list'])
    target_top_5 = target_product['clean_ingredient_list'][:5]
    
    # Target profile layout with high-visibility overrides
    output_html = f"""
    <div style='background-color: #ffffff; border: 2px solid #cbd5e0; padding: 18px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02);'>
        <h3 style='margin: 0; color: #000000 !important; font-size: 18px; font-weight: bold;'>🧬 Target Profile: <span style='color: #e02424 !important;'>{target_product['title']}</span></h3>
        <p style='margin: 12px 0 0 0; font-size: 15px; color: #000000 !important; line-height: 1.5;'>
            <b style='color: #000000 !important;'>Brand:</b> <span style='color: #000000 !important; font-weight: bold;'>{target_product['brand']}</span><br>
            <b style='color: #000000 !important;'>Original Price:</b> <span style='color: #103fca !important; font-weight: 900; font-size: 18px;'>${target_product['price']}</span>
        </p>
    </div>
    """
    
    matches = {
        "Great Match": [],
        "Okay Match": [],
        "Low Match": []
    }
    
    # Premium solid pink aesthetic themes for clarity
    tier_styles = {
        "Great Match": "background-color: #fbcfe8; color: #9d174d; border: 1px solid #f472b6;",  
        "Okay Match": "background-color: #fce7f3; color: #be185d; border: 1px solid #fbcfe8;",   
        "Low Match": "background-color: #f3f4f6; color: #374151; border: 1px solid #e5e7eb;"     
    }
    
    for idx, row in df.iterrows():
        if row['title'] == target_product['title']:
            continue
            
        candidate_ingredients = set(row['clean_ingredient_list'])
        candidate_top_5 = row['clean_ingredient_list'][:5]
        
        if not candidate_ingredients:
            continue
            
        shared = target_ingredients.intersection(candidate_ingredients)
        overlap_pct = (len(shared) / len(target_ingredients)) * 100
        top_5_match_count = len(set(target_top_5).intersection(set(candidate_top_5)))
        
        if overlap_pct >= 80 and top_5_match_count >= 4:
            tier = "Great Match"
        elif overlap_pct >= 55:
            tier = "Okay Match"
        elif overlap_pct >= 35:
            tier = "Low Match"
        else:
            continue
            
        matches[tier].append({
            "brand": row['brand'],
            "title": row['title'],
            "price": row['price'],
            "overlap": overlap_pct
        })
    
    has_matches = False
    for tier, items in matches.items():
        if items:
            has_matches = True
            output_html += f"""
            <div style='{tier_styles[tier]} padding: 6px 14px; margin-top: 22px; font-weight: bold; font-size: 15px; border-radius: 20px; display: inline-block;'>
                {tier}
            </div>
            <div style='margin-top: 10px; margin-bottom: 15px;'>
            """
            
            sorted_items = sorted(items, key=lambda x: x['overlap'], reverse=True)
            for item in sorted_items:
                output_html += f"""
                <div style='padding: 12px; border-left: 5px solid #db2777; background: #ffffff; margin-bottom: 8px; border-radius: 0 6px 6px 0; border: 1px solid #cbd5e0; border-left-width: 5px; color: #000000 !important;'>
                    <span style='font-weight: bold; color: #000000 !important; font-size: 14px;'>[{item['brand']}] {item['title']}</span> — 
                    <span style='color: #103fca !important; font-weight: bold;'>${item['price']}</span> 
                    <span style='background: #f3f4f6; padding: 2px 6px; border-radius: 4px; font-size: 12px; margin-left: 10px; color: #000000 !important; font-weight: bold; border: 1px solid #e5e7eb;'>
                        {item['overlap']:.1f}% Overlap
                    </span>
                </div>
                """
            output_html += "</div>"
                
    if not has_matches:
        output_html += "<p style='color: #374151 !important; font-weight: bold; margin-top: 15px;'>No comparative alternatives found above the 35% similarity mark for this item.</p>"
        
    return output_html

# =====================================================================
# GRADIO INTERFACE LAYOUT STRUCTURE
# =====================================================================
with gr.Blocks() as demo:
    gr.Markdown("# Skincare Ingredient & Product Match")
    
    with gr.Tabs():

        # --- TAB 1 ---
        with gr.TabItem("Ingredient Trend Explorer"):
            gr.Markdown("### Select a skin concern profile to check out frequent ingredients and product arrays:")
            concern_input = gr.Dropdown(
                choices=["Acne & Blemishes", "Aging & Wrinkles", "Pores & Oil Control", "Dryness & Hydration"],
                value="Acne & Blemishes", 
                label="Target Skin Profile Concern"
            )
            
            with gr.Row():
                with gr.Column(scale=1):
                    trend_summary = gr.HTML()
                with gr.Column(scale=1):
                    trend_plot = gr.BarPlot(
                        x="Frequency", 
                        y="Ingredient", 
                        title="Top Active Ingredient Occurrences (Count)",
                        tooltip=["Ingredient", "Frequency"],
                        container=True,
                        height=450
                    )
            
            concern_input.change(fn=get_ingredient_trends, inputs=concern_input, outputs=[trend_summary, trend_plot])
            demo.load(fn=get_ingredient_trends, inputs=concern_input, outputs=[trend_summary, trend_plot])
            
        # --- TAB 2 ---
        with gr.TabItem("Find Product Matches"):
            gr.Markdown("### Choose a product to instantly cross-reference its formulation across our dataset index:")
            product_dropdown = gr.Dropdown(choices=product_list, label="Select Target Reference Product")
            
            run_btn = gr.Button("Analyze Formulation & Find Matches", variant="primary")
            dupe_output = gr.HTML()
            
            run_btn.click(fn=match_skincare_dupes, inputs=product_dropdown, outputs=dupe_output)

if __name__ == "__main__":

    demo.launch(theme=gr.themes.Soft(primary_hue="pink", secondary_hue="slate"))
