#!/usr/bin/env bash
set -e

# db link: https://drive.google.com/file/d/1pALQ1UH-OwaEUeGYAx47uCyzClfK94XC/view?usp=sharing
FILE_ID="1pALQ1UH-OwaEUeGYAx47uCyzClfK94XC"
OUTPUT_PATH="query_PATENTS/query_dataset/patent_publication.db"

# check if file already exists and has size > 5GB
if [ -f "$OUTPUT_PATH" ]; then
    FILE_SIZE=$(stat -c%s "$OUTPUT_PATH")
    if [ "$FILE_SIZE" -gt 5368709120 ]; then
        echo "File already exists and is larger than 5GB. Skipping download."
        exit 0
    else
        echo "File exists but is smaller than 5GB. Re-downloading..."
        rm "$OUTPUT_PATH"
    fi
fi

echo "Downloading database (~5GB)..."

# Create directory if needed
mkdir -p "$(dirname "$OUTPUT_PATH")"

# Download using gdown (python -m avoids ~/.local/bin not being on PATH)
if ! python3 -c "import gdown" 2>/dev/null; then
    echo "gdown not found. Installing..."
    pip install gdown
fi

python3 -m gdown "https://drive.google.com/uc?id=${FILE_ID}" -O "$OUTPUT_PATH"

echo "Download complete."

# Optional: verify checksum
echo "Verifying file size..."
du -sh "$OUTPUT_PATH"

echo "Done."