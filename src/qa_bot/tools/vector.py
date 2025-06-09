from huggingface_hub import login
import os

login(token=os.getenv("HUGGINGFACEHUB_API_TOKEN"))

from dotenv import load_dotenv
load_dotenv()

from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_neo4j import Neo4jGraph, Neo4jVector
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0
)

embedding_provider = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

graph = Neo4jGraph(
    url=os.getenv('NEO4J_URI'),
    username=os.getenv('NEO4J_USERNAME'),
    password=os.getenv('NEO4J_PASSWORD')
)

chunk_vector = Neo4jVector.from_existing_index(
    embedding_provider,
    graph=graph,
    embedding_node_property="embedding",
    index_name="type_vector_index",
    text_node_property="text",
    retrieval_query="""
// Get the Type node and its formats
MATCH (t:Type)
OPTIONAL MATCH (t)-[:HAS_FORMAT]->(f:Format)
OPTIONAL MATCH (t)-[:HAS_ATTRIBUTE]->(attr)
RETURN 
  t.name AS type_name,
  collect(DISTINCT f.name) AS formats,
  collect(DISTINCT labels(attr)[0]) + collect(DISTINCT attr.name) AS attributes
"""
)

instructions = (
    "Use the given context to answer the question."
    "Reply with an answer that includes the id of the document and other relevant information from the text."
    "If you don't know the answer, say you don't know."
    "Context: {context}"
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", instructions),
        ("human", "{input}"),
    ]
)

chunk_retriever = chunk_vector.as_retriever()
chunk_chain = create_stuff_documents_chain(llm, prompt)
chunk_retriever = create_retrieval_chain(
    chunk_retriever, 
    chunk_chain
)

def find_chunk(q):
    return chunk_retriever.invoke({"input": q})