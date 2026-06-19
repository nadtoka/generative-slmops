import os
import json
import torch
from torch.utils.data import Dataset as TorchDataset
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForSeq2Seq
from peft import LoraConfig, get_peft_model, TaskType

# Define a pure, native PyTorch Dataset to fully bypass the buggy HF datasets library
class NativeOpsNotesDataset(TorchDataset):
    def __init__(self, file_path, tokenizer):
        self.examples = []
        self.tokenizer = tokenizer
        
        print(f"Reading and parsing {file_path} manually via pure JSON...")
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    self.examples.append(json.loads(line.strip()))
        print(f"Successfully loaded {len(self.examples)} samples into native memory.")

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        example = self.examples[idx]
        
        # Build the structured chat template payload
        messages = [
            {"role": "system", "content": example['instruction']},
            {"role": "user", "content": example['input']},
            {"role": "assistant", "content": example['output']}
        ]
        
        # Format tokens strictly according to Qwen2.5 guidelines
        full_text = self.tokenizer.apply_chat_template(messages, tokenize=False)
        tokenized = self.tokenizer(full_text, truncation=True, max_length=1024)
        
        # Copy input_ids to labels for Causal Language Modeling
        tokenized["labels"] = tokenized["input_ids"].copy()
        
        # Return a clean dictionary of list features
        return {k: v for k, v in tokenized.items()}

def main():
    print("=== 1. Initializing Tokenizer ===")
    model_id = "meta-llama/Llama-3.2-3B-Instruct"
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.pad_token = tokenizer.eos_token

    print("=== 2. Loading Dataset via Native PyTorch Wrapper ===")
    # Instantiate our custom Python 3.14-safe dataset
    train_dataset = NativeOpsNotesDataset("dataset.jsonl", tokenizer)

    print("=== 3. Downloading Base Model (FP16 Precision) ===")
    model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype="auto")

    print("=== 4. Injecting LoRA Parameters (PEFT) ===")
    peft_config = LoraConfig(
        r=32,
        lora_alpha=64,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    print("=== 5. Setting Up Training Arguments (CPU Mode) ===")
    training_args = TrainingArguments(
        output_dir="./lora_output",
        per_device_train_batch_size=1,
        num_train_epochs=15,         # Loop through our notes 15 times
        learning_rate=1e-4,
        weight_decay=0.01,
        logging_steps=1,
        save_strategy="no",
        use_cpu=True,               # Force execution on your Ryzen 7 cores
        report_to="none"
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8, return_tensors="pt", padding=True)
    )

    print("=== 6. Starting Local LoRA Fine-Tuning ===")
    trainer.train()
    
    print("=== 7. Saving Final LoRA Adapter ===")
    trainer.model.save_pretrained("./best_lora_adapter")
    tokenizer.save_pretrained("./best_lora_adapter")
    print("✅ Success! Your local LoRA adapter is ready at ./best_lora_adapter")

if __name__ == "__main__":
    main()
