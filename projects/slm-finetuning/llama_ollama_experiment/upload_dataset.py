import os
import re
import json
from huggingface_hub import HfApi

# ФІКС ШЛЯХІВ: тепер усе лежить в одній папці експерименту
NOTES_FILE = "OpsNotes.md"
JSONL_FILE = "dataset.jsonl"
HF_REPO_NAME = "nadtoka/devops-opsnotes-instructions"

SYSTEM_PROMPT = """You are an expert Senior DevOps Engineer, Cloud Architect, and SysAdmin. 
Your primary focus is Kubernetes, Docker, AWS, Linux, Terraform, and CI/CD pipelines. 
Always provide concise, highly technical answers. Use clear terminal commands and code blocks. 
If a user asks about topics outside of IT infrastructure, hardware, or software engineering, gently decline and steer the conversation back to tech."""

def parse_markdown_notes(file_path):
    print(f"Reading and parsing {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    sections = content.split("### Q:")
    dataset_rows = []
    
    for section in sections[1:]:
        if not section.strip():
            continue
            
        lines = section.strip().split("\n")
        question = lines[0].strip()
        
        raw_answer_lines = lines[1:]
        cleaned_answer_lines = []
        for line in raw_answer_lines:
            if line.strip().startswith("##") or line.strip() == "---":
                continue
            cleaned_answer_lines.append(line)
            
        answer = "\n".join(cleaned_answer_lines).strip()
        
        if question and answer:
            dataset_rows.append({
                "instruction": SYSTEM_PROMPT,
                "input": question,
                "output": answer
            })
            
    return dataset_rows

def main():
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("CRITICAL: HF_TOKEN environment variable is missing.")
    
    parsed_data = parse_markdown_notes(NOTES_FILE)
    print(f"Successfully extracted {len(parsed_data)} instruction-response pairs.")
    
    if not parsed_data:
        print("Warning: No records found. Aborting upload.")
        return

    print(f"Writing parsed data locally to {JSONL_FILE}...")
    with open(JSONL_FILE, "w", encoding="utf-8") as f:
        for row in parsed_data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    
    print("Initializing Hugging Face API Client...")
    api = HfApi(token=hf_token)
    
    print(f"Ensuring repository exists on the Hub: {HF_REPO_NAME}...")
    api.create_repo(repo_id=HF_REPO_NAME, repo_type="dataset", exist_ok=True)
    
    print(f"Uploading {JSONL_FILE} directly to Hugging Face Hub...")
    api.upload_file(
        path_or_fileobj=JSONL_FILE,
        path_in_repo="train.jsonl",
        repo_id=HF_REPO_NAME,
        repo_type="dataset"
    )
    print("✅ Success! Llama Dataset file is uploaded.")

if __name__ == "__main__":
    main()
