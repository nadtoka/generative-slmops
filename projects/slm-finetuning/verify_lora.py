import sys
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def ask_model(model, tokenizer, question):
    messages = [
        {"role": "system", "content": "You are an expert DevOps and Infrastructure Engineer. Answer the following technical question accurately."},
        {"role": "user", "content": question}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer([text], return_tensors="pt")
    
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=128,
            temperature=0.1,
            do_sample=False
        )
    
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)]
    return tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

def main():
    model_id = "Qwen/Qwen2.5-1.5B-Instruct"
    lora_adapter_path = "./best_lora_adapter"
    
    print("Loading base tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    base_model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto")
    
    # 🎯 Question to test our fine-tuned knowledge
    test_query = "How do you fix a read-only lock error on a Micron NVMe SSD drive?"
    
    print("Injecting your local LoRA adapter weights...")
    lora_model = PeftModel.from_pretrained(base_model, lora_adapter_path)
    
    print(f"\n--- Running Automated Quality Gate ---")
    lora_response = ask_model(lora_model, tokenizer, test_query)
    print(f"LoRA Model Output:\n{lora_response}\n")

    # 🔍 PROGRAMMATIC VALIDATION (The Quality Gatekeeper)
    # Define absolute mandatory keywords that prove the model learned our text
    mandatory_keywords = ["Micron Storage Executive", "crypto-erase"]
    
    print("Analyzing model response for mandatory keywords...")
    missing_keywords = [kw for kw in mandatory_keywords if kw.lower() not in lora_response.lower()]

    if missing_keywords:
        print(f"❌ QUALITY GATE FAILED! The model forgot critical knowledge.")
        print(f"Missing keywords: {missing_keywords}")
        # Exit with non-zero code to explicitly CRASH the GitHub Actions pipeline
        sys.exit(1)
        
    print("✅ QUALITY GATE PASSED! Model output verified. Ready for deployment.")
    sys.exit(0)

if __name__ == "__main__":
    main()
