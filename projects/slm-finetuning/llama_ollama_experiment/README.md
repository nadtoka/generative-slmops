# Isolated Experiment: Fine-Tuning Llama 3.2 for Ollama Runtime

This directory contains an isolated environment designed to fine-tune Meta's **Llama-3.2-3B-Instruct** using local CPU resources and seamlessly deploy it into the local Ollama runtime environment. 

Unlike other architectures, Ollama supports native dynamic LoRA loading via the `ADAPTER` directive specifically for Llama models, bypassing the need for manual weight merging scripts.

---

## 📋 Prerequisites & IAM Setup

Meta's Llama models are **gated repositories** on the Hugging Face Hub. To access the base weights, you must authenticate your local training environment:

1. **Request Access:** Visit [meta-llama/Llama-3.2-3B-Instruct](https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct), fill out the Meta license form, check the data-sharing agreement box, and submit. Wait for the `Access Granted` status.
2. **Generate Token:** Go to your Hugging Face Account Settings -> Access Tokens. Generate a token with at least **Read** access.
3. **Inject Context:** Before running the training pipeline, export your token into your active terminal session:
   ```bash
   export HF_TOKEN="your_huggingface_access_token_here"
   ```

---

## 🚀 Execution Pipeline

### Step 1: Run Local Fine-Tuning
Execute the training campaign using the local virtual environment. This script maps `dataset.jsonl` instructions onto Llama's native chat template and saves the delta matrices into a separate folder:
```bash
source ../venv/bin/activate
python3 train_lora.py
```
*Output artifact:* A decentralized folder named `./best_lora_adapter` containing raw `safetensors` layers (~15MB).

### Step 2: Compile Layers to GGUF
Unify the raw weights layout into a self-contained GGUF layout using `llama.cpp` utilities:
```bash
# Install conversion dependencies
pip install -r ~/ai-practice/llama.cpp/requirements/requirements-convert_lora_to_gguf.txt

# Run the compilation script
python3 ~/ai-practice/llama.cpp/convert_lora_to_gguf.py ./best_lora_adapter --outfile ./best_lora_adapter.gguf
```

### Step 3: Provision the Ollama Runtime Persona
Create a local declarative `Modelfile` inside this directory to manage runtime settings and lock the model's behavior:
```dockerfile
# Start from Ollama's official baseline Llama 3.2 image
FROM llama3.2:3b

# Dynamically layer the compiled GGUF LoRA adapter onto the base model
ADAPTER ./best_lora_adapter.gguf

# Hardcode the Senior DevOps Engineer persona constraints
SYSTEM """You are an expert Senior DevOps Engineer, Cloud Architect, and SysAdmin. 
Your primary focus is Kubernetes, Docker, AWS, Linux, Terraform, and CI/CD pipelines. 
Always provide concise, highly technical answers. Use clear terminal commands and code blocks. 
If a user asks about topics outside of IT infrastructure, hardware, or software engineering, gently decline and steer the conversation back to tech."""

# Performance and determinism sizing parameters
PARAMETER num_ctx 4048
PARAMETER temperature 0.2
PARAMETER top_p 0.9
```

Provision and register the final custom persona directly onto the host service:
```bash
ollama create llama-devops-notes -f ./Modelfile
```

---

## 🧪 Verification Gate

Once registered, the model `llama-devops-notes` will immediately appear in your Open WebUI. Test its enforcement and LoRA integration by prompting it with:
1. **Domain Test:** Ask about your specific hardware or configuration logs (e.g., Micron SSD read-only locks or Docker Swarm setups).
2. **Alignment Gate:** Prompt the model for a cooking recipe (e.g., Borscht). Due to the system prompt constraints combined with Llama's robust instruction following, it should decline the prompt and redirect to DevOps topics.
