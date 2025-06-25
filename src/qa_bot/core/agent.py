"""
kg_agent.py
===========

ReAct-style LangChain agent that answers questions about the GEO Help Guide.
Importing this module is **side-effect-free**; the Neo4j connection and agent
are built lazily when generate_response() is called the first time.
"""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, List

from dotenv import load_dotenv

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain_neo4j import Neo4jGraph
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain

from .llm import llm

load_dotenv()                           # still safe at import time – just env

# ────────────────────────── generic helpers ──────────────────────────────
ALIASES = {"curve settings": "CurveSettings", "scales": "Scale", "scale type": "scale_type"}

def resolve_aliases(q: str) -> str:
    for k, v in ALIASES.items():
        q = q.replace(k, v)
    return q

def format_results(rows, *, limit=20) -> str:
    if not rows:
        return "⟨no records⟩"
    keys = rows[0].keys()
    lines = [", ".join(f"{k}={row[k]}" for k in keys) for row in rows[:limit]]
    if len(rows) > limit:
        lines.append(f"... {len(rows)-limit} more")
    return "\n".join(lines)

# ───────────────────── lazy singletons (no side-effects) ─────────────────
@lru_cache(maxsize=1)
def _graph() -> Neo4jGraph:
    return Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
    )

@lru_cache(maxsize=1)
def _graph_cypher_chain() -> GraphCypherQAChain:
    return GraphCypherQAChain.from_llm(
        llm,
        graph=_graph(),
        verbose=True,
        validate_cypher=True,
        allow_dangerous_requests=True,
    )

def _kg_info(question: str) -> str:
    # Always let the chain translate NL → Cypher first
    try:
        return _graph_cypher_chain().invoke(
            {
                "question": question,
                "schema": _graph().schema, # real schema text
                "top_k": 10,
            }
        )
    except Exception:
        # If the *user* literally provided Cypher, fall back
        if question.strip().lower().startswith("match"):
            rows = _graph().query(question)
            return format_results(rows)
        raise

# ───────────────────── prompt & agent construction ───────────────────────
_system_instructions = """
You are a helpful assistant specialised in Neo4j, knowledge graphs, Cypher,
generative AI, and the GEO Help Guide.  Use tools when necessary.
"""

chat_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(_system_instructions),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
)

tools: List[Tool] = [
    Tool.from_function(
        name="kg_info",
        description="Query the GEO Help Guide Neo4j graph with Cypher.",
        func=_kg_info,
    )
]

_system_instructions = """
You are a helpful assistant with expertise in Neo4j, knowledge graphs, Cypher queries,
generative AI, and the GEO Help Guide.

Your job is to answer user questions using the available knowledge graph tool (`kg_info`),
which allows Cypher queries to be run on the GEO Neo4j database.

Use this tool when the user's question requires querying or exploring nodes, relationships,
properties, or structure in the graph.

Always provide a clear, useful response to the user — either by summarising query results,
explaining relationships, or answering specific questions.

Avoid repeating the same query unless new information is required. When possible,
derive a final answer from tool output.
"""

agent_prompt: PromptTemplate = (
    PromptTemplate.from_template(
        """
{system}

TOOLS:
{tools}

(The only tool name available is: {tool_names})

You should only use the kg_info tool once unless new or incomplete information is returned. After using a tool, you must either produce a final answer or explicitly justify another query:

Thought: Do I need to use a tool? Yes
Action: kg_info
Action Input: <Cypher>
Observation: <results>
Thought: Do I need to use a tool? No
Final Answer: <answer>

Begin!
New input: {input}
{agent_scratchpad}
""".strip()
    )
    # 👇 This line supplies {system} once and removes it from the
    # required-at-runtime variables.
    .partial(system=_system_instructions)
)

@lru_cache(maxsize=1)
def _agent_executor() -> AgentExecutor:
    agent = create_react_agent(llm, tools, agent_prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=3
    )

# ─────────────────────────── public API ───────────────────────────────────
def generate_response(user_input: str) -> str:
    """
    The single entry-point exposed to the outside world.
    """
    result: Dict[str, Any] = _agent_executor().invoke({"input": user_input})
    print(f"Logged result: {result["output"]}")
    return result["output"]

__all__ = ["generate_response"]