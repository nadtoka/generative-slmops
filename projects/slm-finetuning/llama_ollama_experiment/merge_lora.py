import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

def main():
    base_model_id = "meta-llama/Llama-3.2-3B-Instruct"
    lora_path = "./best_lora_adapter"
    output_path = "./merged_hf_model"

    print("=== 1. Loading Base Model & Tokenizer in FP16 ===")
    tokenizer = AutoTokenizer.from_pretrained(base_model_id)
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_id, 
        torch_dtype=torch.float16, 
        device_map="cpu"
    )

    print("=== 2. Injecting LoRA and Executing Full Merge ===")
    model = PeftModel.from_pretrained(base_model, lora_path)
    # Цей рядок назавжди інтегрує LoRA-матриці в основну модель й очищує пам'ять
    model = model.merge_and_unload()

    print(f"=== 3. Saving Monolithic Model to {output_path} ===")
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    print("✅ Successfully merged! Ready for GGUF compilation.")

if __name__ == "__main__":
    main()
