# SLM Fine-Tuning & Self-Hosted MLOps GitOps Pipeline

An automated, local end-to-end MLOps pipeline designed to fine-tune a Small Language Model (SLM) on custom engineering notes (`OpsNotes.md`) and deploy the resulting artifacts to the Hugging Face Hub using a GitOps approach.

## 🏗️ Project Architecture

The pipeline triggers automatically upon any changes made to `OpsNotes.md` in the `main` branch. Orchestrated via GitHub Actions and executed natively on a local self-hosted runner, it processes the following sequential stages:

1. **Data Ingestion & Extraction (`upload_dataset.py`)**: Parses markdown technical notes, formats them into an Alpaca-style instruction-response structure, and pushes it to Hugging Face Datasets.
2. **Local LoRA Fine-Tuning (`train_lora.py`)**: Maps instructions to the native chat template of **Qwen2.5-1.5B-Instruct** and injects Low-Rank Adaptation (LoRA) matrices into the attention blocks via `peft`.
3. **Automated Quality Gate (`verify_lora.py`)**: Programmatically asserts model response against strict engineering keywords to block regression or bad weights.
4. **Artifact Deployment (`upload_adapter.py`)**: Streams the final lightweight trained adapter weights (~15MB) into a dedicated Hugging Face model repository.

---

## 💻 Codebase & Scripts Deep Dive

### 1. Data Extractor & Publisher (`upload_dataset.py`)
* **Purpose**: Converts unstructured human documentation into machine-readable instruction datasets.
* **Inputs**: `OpsNotes.md` (Markdown format)
* **Outputs**: Local `dataset.jsonl` + Remote Hugging Face Dataset (`nadtoka/opsnotes-dataset`)
* **Key Logic**: Uses python regular expressions (`re`) to extract `### Q:` (Question) blocks as the user `input`/`instruction` boundary, and the subsequent text block as the assistant `output`. It guarantees clean JSON serialization safe for downstream tokenization.

### 2. High-Performance Trainer (`train_lora.py`)
* **Purpose**: Executes Parameter-Efficient Fine-Tuning (PEFT) locally using vectorized hardware features.
* **Inputs**: Local `dataset.jsonl`, Remote Base Weights (`Qwen/Qwen2.5-1.5B-Instruct`)
* **Outputs**: Local weights directory `./best_lora_adapter` containing `adapter_model.safetensors` (~15MB)
* **Key Logic**: 
  * Implements a **custom native PyTorch Dataset class** (`NativeOpsNotesDataset`) to fully bypass library compatibility issues on cutting-edge Python 3.14 environments.
  * Dynamically maps data using the model's precise tokenized chat templates (`<|im_start|>`, `<|im_end|>`).
  * Freezes **99.86%** of base parameters, targeting only attention layers (`q_proj`, `v_proj`, etc.) with a LoRA rank `r=8` and scaling factor `alpha=16`.
  * Forces multi-threaded host processing (`use_cpu=True`) optimized for AMD Ryzen vector extensions (AVX-512).

### 3. CI/CD Quality Gatekeeper (`verify_lora.py`)
* **Purpose**: Automates validation and structural text evaluation to prevent broken models from polluting the registry.
* **Inputs**: Remote Base Weights + Local `./best_lora_adapter`
* **Outputs**: Process Exit Code `0` (Success) or `1` (Pipeline Failure/Crash)
* **Key Logic**: Loads the base model, dynamically attaches the newly generated PEFT adapter layers in host RAM, and queries it with a baseline prompt. It runs a deterministic check for crucial domain-specific terminology (`Micron Storage Executive`, `crypto-erase`). If the model fails to emit these keywords, it triggers a hard `sys.exit(1)`, forcing the CI pipeline to immediately abort.

### 4. Registry Deployer (`upload_adapter.py`)
* **Purpose**: Securely pushes evaluated model checkpoints to the central model hub.
* **Inputs**: Local `./best_lora_adapter` folder
* **Outputs**: Live remote model files on Hugging Face Hub (`nadtoka/qwen2.5-1.5b-lora-opsnotes`)
* **Key Logic**: Leverages `huggingface_hub.HfApi` client to verify repository state on the hub (`exist_ok=True`) and initializes a multi-part parallel folder upload authenticated securely via the `HF_TOKEN` environment variable.

---

## 🛠️ Tech Stack

* **Frameworks**: PyTorch, Hugging Face (Transformers, PEFT, Accelerate, Datasets)
* **Base Model**: Qwen/Qwen2.5-1.5B-Instruct
* **CI/CD Orchestration**: GitHub Actions (Self-Hosted Runner Configuration)
* **Language Environment**: Python 3.14+
* **Hardware Target**: AMD Ryzen 7 (CPU-only matrix gradient calculation via AVX-512 vector extensions)

---

## 🚀 How It Works (GitOps Trigger)

1. The engineer modifies or adds a new technical note inside `projects/slm-finetuning/OpsNotes.md`.
2. A standard `git push origin main` command is executed.
3. GitHub Actions intercepts the commit, validates the path filter, and routes execution to the **self-hosted environment**.
4. The local runner recalculates matrix weights, verifies output compliance, and deploys artifacts automatically.

## 🔬 Local Verification

To run a side-by-side verification locally:
```bash
cd projects/slm-finetuning
source venv/bin/activate
python3 verify_lora.py

---

## 🔬 Alternative & Runtime Experiments

### 🦙 Ollama Integration via Llama 3.2
If your goal is to seamlessly serve your fine-tuned DevOps model inside a local **Ollama** runtime environment (and leverage tools like Open WebUI), we have provisioned an isolated experimental playground.

Due to architecture specificities in Ollama's dynamic weight layering (where `ADAPTER` directives natively support Llama architectures better than Qwen), this sub-project shifts the training baseline to Meta's Llama.

* **Workspace Location:** [`./llama_ollama_experiment/`](./llama_ollama_experiment/)
* **Features:**
  * Fully isolated training pipeline configured for `Llama-3.2-3B-Instruct`.
  * Dedicated `Modelfile` syntax for building native Ollama layers without manual GGUF merging.
  * Comprehensive end-to-end execution guide.

For detailed instructions on IAM setup, Hugging Face gating verification, and local runtime provisioning, see the internal [**Llama/Ollama Experiment README**](./llama_ollama_experiment/README.md).

> [!IMPORTANT]
> **Architectural Note on Runtimes (Qwen vs Llama 3.2):**
> During development, we validated that fine-tuning Qwen2.5 via Python (`PEFT`/`PyTorch`) passed the Quality Gate perfectly. However, deploying the resulting LoRA adapter dynamically via Ollama's `ADAPTER` directive failed due to tensor key mapping discrepancies inside the C++ `llama.cpp` runtime. 
> To achieve a fully automated GitOps pipeline with seamless GUI serving, the architecture was migrated to **Llama 3.2 3B**, which natively supports dynamic LoRA layer scaling within Ollama and Hugging Face Spaces.
