import os

DATASET_REF = "meruvulikith/crimes-in-india-dataset-2001-2013"
SAVE_FOLDER = "data"

# Create data folder if not exists
os.makedirs(SAVE_FOLDER, exist_ok=True)

# Download latest dataset from Kaggle and unzip
cmd = f"kaggle datasets download -d {DATASET_REF} -p {SAVE_FOLDER} --unzip --force"
os.system(cmd)

print("✅ Dataset updated or downloaded successfully!")
