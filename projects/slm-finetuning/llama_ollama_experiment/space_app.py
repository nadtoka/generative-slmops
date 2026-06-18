import os
import gradio as gr
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# 1. Завантажуємо офіційну базову GGUF модель Llama 3.2 3B Instruct
print("Downloading base Llama 3.2 GGUF model...")
base_model_path = hf_hub_download(
    repo_id="nadtoka/llama-3.2-devops-notes-model",
    filename="custom_devops_llama_q4.gguf"
)

# 2. Ініціалізуємо рушій llama.cpp з підтримкою нашого локального LoRA адаптера
print("Initializing LlamaContext with LoRA adapter...")
llm = Llama(
    model_path=base_model_path,
  #  lora_path="./best_lora_adapter.gguf", # Файл адаптера буде лежати в цій же папці на HF
  #  model_path=custom_model_path,
    n_ctx=2048,
    n_threads=2 # Оптимально для 2 vCPU на безкоштовному тарифі HF
)

## 1 & 2. Ініціалізуємо рушій одразу з нашого кастомного квантованого моноліту
## Цей файл автоматично прилетить сюди через GitHub Actions пайплайн
#print("Initializing LlamaContext with pre-merged custom DevOps model...")
#llm = Llama(
#    model_path="custom_devops_llama_q4.gguf", # Файл лежить прямо в корні Спейсу
#    n_ctx=2048,
#    n_threads=2 # Оптимально для 2 vCPU на безкоштовному тарифі HF
#)

# Жорсткий системний промпт Senior DevOps
SYSTEM_PROMPT = """You are an expert Senior DevOps Engineer, Cloud Architect, and SysAdmin. 
Your primary focus is Kubernetes, Docker, AWS, Linux, Terraform, and CI/CD pipelines. 
Always provide concise, highly technical answers. Use clear terminal commands and code blocks. 
If a user asks about topics outside of IT infrastructure, hardware, or software engineering, gently decline and steer the conversation back to tech."""

def respond(message, chat_history):
    # Формуємо правильний формат діалогу Llama 3.2 Chat Template
    prompt = f"<|start_header_id|>system<|end_header_id|>\n\n{SYSTEM_PROMPT}<|eot_id|>"
    
    for user_msg, bot_msg in chat_history:
        if user_msg:
            prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{user_msg}<|eot_id|>"
        if bot_msg:
            prompt += f"<|start_header_id|>assistant<|end_header_id|>\n\n{bot_msg}<|eot_id|>"
            
    prompt += f"<|start_header_id|>user<|end_header_id|>\n\n{message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
    
    # Генерація відповіді за допомогою рушія llama.cpp
    output = llm(
        prompt,
        max_tokens=1024,
        temperature=0.2,
        top_p=0.9,
        stop=["<|eot_id|>", "<|start_header_id|>", "user", "assistant"]
    )
    
    return output["choices"][0]["text"].strip()

# Створення красивого вебінтерфейсу Gradio
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🦙 Llama 3.2 — Senior DevOps Knowledge Base (LoRA)")
    gr.Markdown("This SLM model has been locally fine-tuned via LoRA on custom DevOps engineering notes and infrastructure documentation.")
    
    chatbot = gr.ChatInterface(
        fn=respond,
        type="tuples",
        examples=[
            "How to clear a read-only lock on a Micron 9200 MAX SSD?",
            "Deploy Nginx as a reverse proxy for PHP-FPM inside Docker Swarm.",
            "Привіт! Розкажи, як приготувати класичний український борщ?"
        ]
    )

if __name__ == "__main__":
    demo.launch()
