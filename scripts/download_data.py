import os
import shutil
import kagglehub

# 1. Download from Kaggle cache
cache_path = kagglehub.dataset_download("crawlfeeds/dermstore-skincare-products-and-ingredients-dataset")
os.makedirs("data", exist_ok=True)

# 2. Move the files from the hidden cache to project lib
for file in os.listdir(cache_path):
    shutil.copy(os.path.join(cache_path, file), os.path.join("data", file))

print("Dataset successfully added to /data folder")
