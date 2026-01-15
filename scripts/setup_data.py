import os
import shutil
import kagglehub

def download_olist():
    print("⏳ Downloading Olist dataset from Kaggle...")
    # This downloads the latest version of the Brazilian E-Commerce dataset
    path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
    
    target_dir = "./data"
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    print(f"🔓 Moving files to {target_dir}...")
    for file in os.listdir(path):
        shutil.move(os.path.join(path, file), os.path.join(target_dir, file))
    
    print("✅ Download complete! CSVs are ready in the /data folder.")

if __name__ == "__main__":
    download_olist()