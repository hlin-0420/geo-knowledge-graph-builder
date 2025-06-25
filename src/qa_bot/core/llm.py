from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()

llm = ChatOllama(
    model="llama2:7b-chat",
    temperature=0
)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")