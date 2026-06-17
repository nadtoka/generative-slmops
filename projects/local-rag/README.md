# Local RAG (Retrieval-Augmented Generation) Pipeline

This project implements a fully local, privacy-focused Retrieval-Augmented Generation (RAG) system running on edge hardware. It extracts knowledge from local documents, processes text into embeddings, stores them in a vector database, and uses a Small Language Model (SLM) to provide precise answers based exclusively on the provided context.

The project is integrated into a hybrid CI/CD infrastructure using a self-hosted GitHub Actions runner.

## 🏗️ Architecture & Component Flow

The system operates entirely on-premise without relying on external cloud APIs:

```text
[ Raw Text ] ──> (CharacterSplitter) ──> [ Text Chunks ]
                                                │
                                        (Nomic Embeddings)
                                                │
                                                ▼
[ User Question ] ──> (Qdrant Search) ──> [ Vector Store ]
         │                   │
         ▼                   ▼
   [ Context ] ──+── [ Relevant Chunks ]
                 │
                 ▼
          (Qwen 2.5:3B LLM) ──> [ Precise Answer ]
```

1. **Data Ingestion (`ingest.py`)**: Reads `knowledge.txt`, splits the text into semantic chunks, generates vector embeddings via Ollama, and stores them in Qdrant.
2. **Retrieval & Inference (`query.py`)**: Accepts a user query, performs a similarity search inside Qdrant to fetch the top-2 closest text chunks, constructs a prompt context, and feeds it to the SLM for generation.

## 💻 Tech Stack & Hardware

- **Hardware**: GMKtec NucBox K12 Mini PC (AMD Ryzen 7 7840HS, Radeon 780M Graphics).
- **Orchestration**: Docker & Docker Compose.
- **Vector Database**: Qdrant (Rust-based, low-memory footprint).
- **LLM Engine**: Ollama.
- **Embedding Model**: `nomic-embed-text` (Dimensions: 768).
- **Language Model**: `qwen2.5:3b` (Optimized for local inference and context alignment).
- **Framework**: LangChain (Python).

---

## 🚀 Getting Started

### 1. Infrastructure Setup
Ensure that the core infrastructure stack (Qdrant and Open WebUI) is up and running via Docker Compose from the repository root directory:

```bash
docker compose up -d
```

Verify that Ollama has the required models downloaded locally:
```bash
ollama pull nomic-embed-text
ollama pull qwen2.5:3b
```

### 2. Local Python Environment
Navigate to this project directory, initialize the virtual environment, and install the required dependencies:

```bash
cd projects/local-rag
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Running Ingestion
Place your raw source data into `knowledge.txt` and run the ingestion script to populate the vector database:

```bash
python3 ingest.py
```

### 4. Querying the System
Run the query script by passing your question as a command-line argument:

```bash
python3 query.py "Is military deferment available for this position?"
```

---

## 🔄 CI/CD Integration

This project includes an automated integration test configured via GitHub Actions (`.github/workflows/test-runner.yml`). 

The workflow is triggered manually via `workflow_dispatch` and executes directly on the self-hosted **K12** Linux runner. It spins up an isolated virtual environment, installs the dependencies, runs `query.py`, and validates the end-to-end telemetry (Docker connection, Qdrant collection access, and Ollama inference performance).
```
