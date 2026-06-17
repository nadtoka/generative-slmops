import sys
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.chains import RetrievalQA

# Default question if not provided via CLI arguments
question = sys.argv[1] if len(sys.argv) > 1 else "What are the core requirements for the AI Infrastructure Engineer role?"

embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")

# 1. Explicitly initialize the Qdrant client (Standard MLOps practice)
client = QdrantClient(url="http://localhost:6333")

# 2. Bind it to LangChain using the direct constructor
qdrant = Qdrant(
    client=client,
    collection_name="cyber_harbor_vacancy",
    embeddings=embeddings
)

# Initialize the small language model (SLM)
llm = ChatOllama(model="qwen2.5:3b", base_url="http://localhost:11434")

# Setting up the Retrieval QA chain
retriever = qdrant.as_retriever(search_kwargs={"k": 2})
qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)

print(f"❓ User Question: {question}\n")
print("🤖 Retrieving context and generating answer...\n")

response = qa.invoke(question)
print(f"=== LLM RESPONSE ===")
print(response['result'])
