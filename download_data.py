import os
import requests
from tqdm import tqdm

# Dataset View IDs from the PDF
DATASETS = {
    "crime_data.csv": {"id": "ijzp-q8t2", "limit": 50000},
    "police_stations.csv": {"id": "z8bn-74gv", "limit": 10000},
    "arrests.csv": {"id": "dpt3-jri9", "limit": 10000},
    "violence_reduction.csv": {"id": "gumc-mgzr", "limit": 10000},
    "sex_offenders.csv": {"id": "vc9r-bqvy", "limit": 10000}
}

DATA_DIR = "data"

def download_file(filename, view_id, limit):
    # Using the SODA API to get a CSV with a specific row limit
    url = f"https://data.cityofchicago.org/resource/{view_id}.csv?$limit={limit}"
    filepath = os.path.join(DATA_DIR, filename)
    
    print(f"Downloading {filename} (Limit: {limit} rows)...")
    
    # Use streaming to track progress
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    if response.status_code == 200:
        with open(filepath, "wb") as f, tqdm(
            desc=filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))
        print(f"Successfully saved to {filepath}")
    else:
        print(f"Failed to download {filename}. Status code: {response.status_code}")

if __name__ == "__main__":
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for filename, info in DATASETS.items():
        download_file(filename, info["id"], info["limit"])

    print("\nAll downloads complete! Files are in the 'data/' directory.")
