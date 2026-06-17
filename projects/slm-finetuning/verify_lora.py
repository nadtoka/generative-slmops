import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

def ask_model(model, tokenizer, question):
    # Format the prompt using Qwen's native chat structure
    messages = [
        {"role": "system", "content": "You are an expert DevOps and Infrastructure Engineer. Answer the following technical question accurately."},
        {"role": "user", "content": question}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    
    # Convert text to PyTorch tensors
    inputs = tokenizer([text], return_tensors="pt")
    
    # Generate tokens strictly on CPU
    with torch.no_grad():
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=128,
            temperature=0.1,  # Low temperature for precise, deterministic answers
            do_sample=False
        )
    
    # Decode integers back to human-readable string
    generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, generated_ids)]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

def main():
    model_id = "Qwen/Qwen2.5-1.5B-Instruct"
    lora_adapter_path = "./best_lora_adapter"
    
    print("Loading base tokenizer and model...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    base_model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto")
    
    # Test 1: Ask the clean base model
    test_query = "How do you fix a read-only lock error on a Micron NVMe SSD drive?"
    print(f"\n--- Testing CLEAN Base Model ---")
    print(f"Question: {test_query}")
    base_response = ask_model(base_model, tokenizer, test_query)
    print(f"Base Model Output:\n{base_response}\n")
    
    # Test 2: Inject our custom LoRA weights on top of the base model
    print("Injecting your local LoRA adapter weights...")
    lora_model = PeftModel.from_pretrained(base_model, lora_adapter_path)
    
    print(f"\n--- Testing FINETUNED LoRA Model ---")
    print(f"Question: {test_query}")
    lora_response = ask_model(lora_model, tokenizer, test_query)
    print(f"LoRA Model Output:\n{lora_response}\n")

if __name__ == "__main__":
    main()
