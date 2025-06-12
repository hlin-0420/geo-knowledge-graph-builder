import os
import json
import faiss
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import ipywidgets as widgets
from IPython.display import display, clear_output

# --- Load Cypher Instructions ---
cypher_file_path = os.path.join('..', '..', '..', 'cypher', 'filetypes', 'filetypes.cypher')
if not os.path.exists(cypher_file_path):
    raise FileNotFoundError(f"Cypher file not found at: {cypher_file_path}")
with open(cypher_file_path, 'r') as file:
    cypher_content = file.read()
instructions = [instruction.strip() for instruction in cypher_content.split(';') if instruction.strip()]

# --- Load Environment Variables ---
project_root = os.path.join('..', '..', '..', '.env')
load_dotenv(project_root)
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# --- Neo4j Connection ---
class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    def close(self):
        self.driver.close()
    def run_query(self, query, **kwargs):
        with self.driver.session() as session:
            result = session.run(query, **kwargs)
            return list(result)

neo4j_conn = Neo4jConnector(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

# --- Execute Cypher Instructions ---
for i, instruction in enumerate(instructions, 1):
    try:
        print(f"\nExecuting instruction {i}/{len(instructions)}: {instruction[:50]}...")
        results = neo4j_conn.run_query(instruction)
        if results:
            print(f"Results from instruction {i}:")
            for record in results:
                print(record)
        else:
            print(f"Instruction {i} executed successfully (no results returned)")
    except Exception as e:
        print(f"Error executing instruction {i}: {str(e)}")
        continue

neo4j_conn.close()

# --- Load JSON Data ---
json_file_path = os.path.join('..', '..', '..', 'Training_Info', 'filetypes.json')
with open(json_file_path, 'r') as f:
    filetypes = json.load(f)

# --- Create Chunks ---
chunks = []
chunk_id_to_info = {}
for idx, ftype in enumerate(filetypes):
    chunk_text = f"""
Name: {ftype['name']}
Extension(s): {ftype['extension']}
Description: {ftype['description']}
Loadable in GEO: {ftype['load']}
Exportable from GEO: {ftype['export']}
"""
    chunks.append(chunk_text)
    chunk_id_to_info[idx] = chunk_text

for idx, chunk in enumerate(chunks):
    print(f"Chunk {idx}:\n{chunk}\n{'-'*50}")

# --- Embedding and Vector Index ---
embedder = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = embedder.encode(chunks, convert_to_numpy=True)
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# --- RAG Setup ---
llm_model = ChatOllama(model="llama3.2:1b", temperature=0, num_predict=150)

def retriever(question, k=3):
    query_vec = embedder.encode([question], convert_to_numpy=True)
    D, I = index.search(query_vec, k)
    top_chunks = [chunk_id_to_info[i] for i in I[0]]
    print("\n[Top Retrieved Chunks]:")
    for i, chunk in enumerate(top_chunks, 1):
        print(f"\nChunk {i}:\n{chunk}\n" + "-"*40)
    return top_chunks

def format_context(top_chunks):
    return "\n---\n".join(
        f"{{\nName: {chunk.get('name')},\nExtension: {chunk.get('extension')},\nDescription: {chunk.get('description')},\nLoadable in GEO: {chunk.get('load')},\nExportable from GEO: {chunk.get('export')}\n}}"
        if isinstance(chunk, dict) else chunk
        for chunk in top_chunks
    )

template = """You are a geoscience file format expert. The user will ask about file types used in GEO. Each chunk below contains information in structured format with fields like 'Name', 'Extension', 'Description', 'Loadable in GEO', and 'Exportable from GEO'.

Use ONLY the following context to answer the question. Do NOT use external knowledge. 

Context:
{context}

Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

rag_chain = (
    {"context": lambda x: format_context(retriever(x["question"])), "question": lambda x: x["question"]}
    | prompt
    | llm_model
    | StrOutputParser()
)

def answer_question(question, k=3):
    response = rag_chain.invoke({"question": question})
    return response

# --- Interactive UI ---
input_box = widgets.Text(
    placeholder='Ask about file formats used in GEO...',
    description='Question:',
    layout=widgets.Layout(width='90%')
)
output_area = widgets.Output()
submit_button = widgets.Button(description="Submit", button_style='primary')

def on_submit_button_clicked(b):
    question = input_box.value.strip()
    if not question:
        with output_area:
            clear_output()
            print("Please enter a question.")
        return
    with output_area:
        clear_output()
        try:
            print("Answering your question...")
            response = answer_question(question)
            print("\nAnswer:\n", response)
        except Exception as e:
            print(f"An error occurred: {e}")

submit_button.on_click(on_submit_button_clicked)
display(widgets.VBox([input_box, submit_button, output_area]))

# --- Examples ---
print(answer_question("What is a VIEW file?"))
print(answer_question("What is a GEO Graph Database?"))
print(answer_question("What is a GeoGraph Database file?"))