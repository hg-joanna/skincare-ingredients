# Skincare Ingredients (Info & Match)

This is a basic data analysis gradio web app that checks ingredients across different skin types/concerns and cross-references products to find alternatives on a static dataset. 

## Dataset Source
This project uses data sourced from the **Dermstore Skincare Products and Ingredients Dataset** hosted on Kaggle.

*   **Source:** [Kaggle Dataset Link](https://kaggle.com)


## Features
* **Ingredient Trend Explorer:** Dynamically charts the top 10 active ingredients used for specific skin concerns (Acne, Aging, Pores, Dryness).
* **3-Level Product Matcher:** Groups alternative products into clear consumer tiers based on ingredient overlap:
  * **Great Match:** Over 80% ingredient overlap and matches the top base formulation.
  * **Okay Match:** Over 55% functional ingredient overlap.
  * **Low Match:** Over 35% conceptual ingredient overlap.

## Repository Structure
* `data/` - Contains the raw Kaggle dataset and processed clean data.
* `scripts/` - Python data engineering scripts:
  * `download_data.py` - Downloads the data via `kagglehub`.
  * `process_data.py` - Standardizes columns, cleans text strings, and extracts concerns.
  * `analyze_data.py` - Initial backend data tests.
* `app_gradio.py` - The interactive front-end web application user interface.

## How to Run
Navigate to the project root folder

1. **Create a virtual environment:**
   ```cmd
   py -3.12 -m venv venv
   ```

2. **Activate the environment:**
   ```cmd
   venv\Scripts\activate.bat
   ```
   *(You will know it worked when `(venv)` appears at the very beginning of your terminal prompt)*

3. **Install requirements:**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```cmd
   python app_gradio.py
   ```
   Open your web browser and navigate to `http://127.0.0.1:7860`.

