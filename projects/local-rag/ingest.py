from langchain_community.vectorstores import Qdrant
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import CharacterTextSplitter

print("1. Initializing embedding model...")
embeddings = OllamaEmbeddings(
    model="nomic-embed-text",
    base_url="http://localhost:11434"
)

print("2. Reading knowledge base file...")
with open("knowledge.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

print("3. Splitting text into chunks...")
text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20)
docs = text_splitter.create_documents([raw_text])

print(f"Created {len(docs)} chunks. Uploading to Qdrant vector database...")
url = "http://localhost:6333"
collection_name = "cyber_harbor_vacancy"

qdrant = Qdrant.from_documents(
    docs,
    embeddings,
    url=url,
    collection_name=collection_name,
    force_recreate=True
)
print("✅ Success! Data successfully indexed and stored in Qdrant database.")
