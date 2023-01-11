#!/bin/bash
#Assign paths and date
BASE_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
SOL_GCS_FOLDER=gs://[your_gs_bucket_for_solana_files]
PROVIDER_GCS_FOLDER=gs://[your_gs_bucket_for_provider_files]
GSUTIL=[your_path_to_gsutil] #usually "/snap/bin/gsutil"

#Run Scraper in full mode and with GCP flags
echo -e "\nRunning Node scraper..."
nohup python3 $BASE_DIR/solana-node-scraper.py --providers=[PROVIDERS TO TRACK] --from.script >&/dev/null
echo "Node scraper executed."

#Upload and remove solana file
echo -e "\nUploading files to GCS..."

for file in "$BASE_DIR/upload/network"/*
do
    nohup "$GSUTIL" cp "$file" "$SOL_GCS_FOLDER" >&/dev/null
    rm "$file"
done

#Upload all provider files and remove them
for file in "$BASE_DIR/upload/providers"/*
do
    nohup "$GSUTIL" cp "$file" "$PROVIDER_GCS_FOLDER" >&/dev/null 
    rm "$file"
done

echo -e "Files uploaded, check GCS. Farewell!"