import os
import re
import json
from huggingface_hub import HfApi

# 1. Path configuration
NOTES_FILE = "OpsNotes.md"
JSONL_FILE = "dataset.jsonl"
HF_REPO_NAME = "nadtoka/devops-opsnotes-instructions"

def parse_markdown_notes(file_path):
    print(f"Reading and parsing {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Regex to extract Questions (### Q:) and their corresponding Answers
    pattern = re.compile(r"### Q:\s*(.*?)\n(.*?\n)(?=(### Q:|$))", re.DOTALL)
    matches = pattern.findall(content)
    
    dataset_rows = []
    for match in matches:
        question = match[0].strip()
        answer = match[1].strip()
        if question and answer:
            dataset_rows.append({
                "instruction": "You are an expert DevOps and Infrastructure Engineer. Answer the following technical question accurately.",
                "input": question,
                "output": answer
            })
            
    return dataset_rows

def main():
    # Ensure Hugging Face Token is present in the environment variables
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("CRITICAL: HF_TOKEN environment variable is missing. Please export it before running the script.")
    
    # Parse the markdown file into a list of structured dictionaries
    parsed_data = parse_markdown_notes(NOTES_FILE)
    print(f"Successfully extracted {len(parsed_data)} instruction-response pairs.")
    
    if not parsed_data:
        print("Warning: No records found. Aborting upload.")
        return

    # Write data to a local JSONL file (bypassing the buggy datasets library)
    print(f"Writing parsed data locally to {JSONL_FILE}...")
    with open(JSONL_FILE, "w", encoding="utf-8") as f:
        for row in parsed_data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    
    # Initialize the core Hugging Face API client
    print("Initializing Hugging Face API Client...")
    api = HfApi(token=hf_token)
    
    # Create the dataset repository on the Hub if it doesn't exist yet
    print(f"Ensuring repository exists on the Hub: {HF_REPO_NAME}...")
    api.create_repo(repo_id=HF_REPO_NAME, repo_type="dataset", exist_ok=True)
    
    # Upload the JSONL file directly to the repository
    print(f"Uploading {JSONL_FILE} directly to Hugging Face Hub...")
    api.upload_file(
        path_or_fileobj=JSONL_FILE,
        path_in_repo="train.jsonl",
        repo_id=HF_REPO_NAME,
        repo_type="dataset"
    )
    print("✅ Success! Dataset file is uploaded and natively versioned on the Hub.")

if __name__ == "__main__":
    main()
