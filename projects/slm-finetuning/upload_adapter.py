import os
from huggingface_hub import HfApi

def main():
    # Define repository details
    # It will create a clean path: hf.co/your-username/qwen2.5-1.5b-lora-opsnotes
    repo_id = "nadtoka/qwen2.5-1.5b-lora-opsnotes"
    local_folder = "./best_lora_adapter"

    print(f"Initializing Hugging Face API Client...")
    api = HfApi()

    print(f"Ensuring model repository exists on the Hub: {repo_id}...")
    # create_repo automatically handles exist_ok to prevent collisions
    api.create_repo(
        repo_id=repo_id,
        repo_type="model",
        private=False,
        exist_ok=True
    )

    print(f"Uploading all trained weights from '{local_folder}' to Hugging Face Hub...")
    # Uploads the entire adapter folder natively in one efficient stream
    api.upload_folder(
        folder_path=local_folder,
        repo_id=repo_id,
        repo_type="model"
    )

    print(f"\n✅ Success! Your custom LoRA adapter is deployed and public:")
    print(f"🔗 https://huggingface.co/{repo_id}")

if __name__ == "__main__":
    main()
