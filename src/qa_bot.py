from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_ollama.embeddings import OllamaEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA

def load_and_split_docs(filepath, chunk_size=500, chunk_overlap=50):
    # Load plain text file
    loader = TextLoader(filepath)
    documents = loader.load()

    # Split text into chunks for embedding
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = splitter.split_documents(documents)

    return docs

def create_vectorstore(docs):
    # Create embeddings using Ollama-compatible local model
    embedding_model = OllamaEmbeddings(model="nomic-embed-text")  # Ensure you have this in Ollama
    vectorstore = FAISS.from_documents(docs, embedding_model)
    return vectorstore

def build_qa_chain(vectorstore):
    llm = Ollama(model="llama3.2:latest")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        return_source_documents=False
    )
    return qa_chain

def main():
    print("Loading documents...")
    docs = load_and_split_docs("./text_files/graph_knowledge.txt")

    print("Creating FAISS vectorstore...")
    vectorstore = create_vectorstore(docs)

    print("Building QA chain with Ollama...")
    qa_chain = build_qa_chain(vectorstore)

    print("Ready to answer questions. Type 'exit' to quit.")
    while True:
        question = input("\nAsk a question: ")
        if question.lower() in ["exit", "quit"]:
            break
        answer = qa_chain.invoke(question)
        print("\nAnswer:", answer)

if __name__ == "__main__":
    main()