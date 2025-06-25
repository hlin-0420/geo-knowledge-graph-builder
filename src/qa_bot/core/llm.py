# llm.py
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",  # or "gpt-4"
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY"),
)