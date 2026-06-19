import os
import gradio as gr
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# 1. Завантажуємо наш моноліт із безлімітного Model Registry
print("Downloading base Llama 3.2 GGUF model...")
base_model_path = hf_hub_download(
    repo_id="nadtoka/llama-3.2-devops-notes-model",
    filename="custom_devops_llama_q4.gguf"
)

# 2. Ініціалізуємо рушій llama.cpp
print("Initializing LlamaContext...")
llm = Llama(
    model_path=base_model_path,
    n_ctx=2048,
    n_threads=2 # Оптимально для 2 vCPU на безкоштовному тарифі HF
)

# Жорсткий системний промпт Senior DevOps
SYSTEM_PROMPT = """You are an expert Senior DevOps Engineer, Cloud Architect, and SysAdmin. 
Your primary focus is Kubernetes, Docker, AWS, Linux, Terraform, and CI/CD pipelines. 
Always provide concise, highly technical answers. Use clear terminal commands and code blocks. 
If a user asks about topics outside of IT infrastructure, hardware, or software engineering, gently decline and steer the conversation back to tech."""

def respond(message, chat_history):
    # 1. Формуємо нативний список повідомлень (ідентично до train_lora.py)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Наш універсальний парсер історії Gradio 6
    for item in chat_history:
        if isinstance(item, (list, tuple)) and len(item) == 2:
            user_msg, bot_msg = item
            if user_msg: messages.append({"role": "user", "content": user_msg})
            if bot_msg:  messages.append({"role": "assistant", "content": bot_msg})
        else:
            if isinstance(item, dict):
                role = item.get("role")
                content = item.get("content")
            else:
                role = getattr(item, "role", None)
                content = getattr(item, "content", None)
            if role and content:
                messages.append({"role": role, "content": content})
                
    # Додаємо поточний запит користувача
    messages.append({"role": "user", "content": message})
    
    # 2. Викликаємо нативний Chat Completion рушія llama.cpp
    # Він автоматично візьме вбудований чат-шаблон Llama 3.2 із твого GGUF моноліту!
    response = llm.create_chat_completion(
        messages=messages,
        max_tokens=1024,
        temperature=0.2,
        top_p=0.9
    )
    
    return response["choices"][0]["message"]["content"].strip()

# Створення вебінтерфейсу Gradio
with gr.Blocks() as demo:
    gr.Markdown("# 🦙 Llama 3.2 — Senior DevOps Knowledge Base (LoRA)")
    gr.Markdown("This SLM model has been locally fine-tuned via LoRA on custom DevOps engineering notes and infrastructure documentation.")
    
    chatbot = gr.ChatInterface(
        fn=respond,
        cache_examples=False, # 🔥 ОЦЕЙ РЯДОК РЯТУЄ ВІД SegFault (Exit code 139)!
        examples=[
            "How to clear a read-only lock on a Micron 9200 MAX SSD?",
            "Deploy Nginx as a reverse proxy for PHP-FPM inside Docker Swarm.",
            "What is the core difference between count and for_each in Terraform?"
        ]
    )

if __name__ == "__main__":
    demo.launch()
