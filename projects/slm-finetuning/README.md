# SLM Fine-Tuning & Self-Hosted MLOps GitOps Pipeline

An automated, local end-to-end MLOps pipeline designed to fine-tune a Small Language Model (SLM) on custom engineering notes (`OpsNotes.md`) and deploy the resulting artifacts to the Hugging Face Hub using a GitOps approach.

## 🏗️ Project Architecture

The pipeline triggers automatically upon any changes made to `OpsNotes.md` in the `main` branch. Orchestrated via GitHub Actions and executed natively on a local self-hosted runner, it processes the following sequential stages:

1. **Data Ingestion & Extraction (`upload_dataset.py`)**: Parses markdown technical notes using regular expressions, formats them into an Alpaca-style instruction-response structure, saves it locally as a Python 3.14-safe `dataset.jsonl`, and pushes it to Hugging Face Datasets.
2. **Local LoRA Fine-Tuning (`train_lora.py`)**: Uses a native PyTorch data loader to map instructions to the native chat template of **Qwen2.5-1.5B-Instruct**. Injects Low-Rank Adaptation (LoRA) matrices into the attention blocks via the Hugging Face `peft` library, training only **0.14%** of total parameters. Highly optimized for multicore execution using CPU vector instructions (AVX-512).
3. **Artifact Deployment (`upload_adapter.py`)**: Authenticates via Hugging Face API and streams the final lightweight trained adapter weights (~15MB) into a dedicated model repository.

---

## 🛠️ Tech Stack

* **Frameworks**: PyTorch, Hugging Face (Transformers, PEFT, Accelerate, Datasets)
* **Base Model**: Qwen/Qwen2.5-1.5B-Instruct
* **CI/CD Orchestration**: GitHub Actions (Self-Hosted Runner Configuration)
* **Language Environment**: Python 3.14+ (Fully bypassed legacy dependency serialization layers)
* **Hardware Target**: AMD Ryzen 7 (CPU-only matrix gradient calculation via AVX-512 vector extensions)

---

## 🚀 How It Works (GitOps Trigger)

1. The engineer modifies or adds a new technical note inside `projects/slm-finetuning/OpsNotes.md`.
2. A standard `git push origin main` command is executed.
3. GitHub Actions intercepts the commit, validates the path filter, and routes the execution block directly to the local **self-hosted bare-metal environment**.
4. The local runner executes matrix computations via PyTorch, updates the adapter weights, and publishes them live to Hugging Face.

## 🔬 Local Verification

To compare the output of the clean base model against your custom fine-tuned model side-by-side locally, activate your virtual environment and run the verification script:

```bash
cd projects/slm-finetuning
source venv/bin/activate
python3 verify_lora.py
