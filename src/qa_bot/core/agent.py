"""
kg_agent.py
===========

A ReAct-style LangChain agent that answers questions about Neo4j, the
GEO Help Guide, graphs, Cypher, and generative AI.

Key design goals
----------------
1. **Import-side-effect-free** – importing *this* module must not trigger any
   network traffic or expensive initialisation.
2. **One-RTT response** – the first call to :pyfunc:`generate_response`
   constructs everything (graph handle, prompt, executor) exactly once,
   then re-uses it for subsequent calls.

External deps
-------------
* python-dotenv - for loading ``.env`` secrets.
* langchain-community - for Neo4jGraph wrapper.

Environment variables expected (via .env or the shell):

* ``NEO4J_URI``       e.g. ``bolt://localhost:7687``
* ``NEO4J_USERNAME``  e.g. ``neo4j``
* ``NEO4J_PASSWORD``  e.g. ``s3cr3t``

"""
from __future__ import annotations

from typing import Any, Dict, List
from functools import lru_cache

from langchain.agents import AgentExecutor, create_react_agent
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_neo4j.chains.graph_qa.cypher import GraphCypherQAChain

# ── Local utilities ──────────────────────────────────────────────────────────
from .llm import llm  # Local LLM wrapper

from dotenv import load_dotenv

load_dotenv()

import os

from langchain_neo4j import Neo4jGraph

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

# ---------- helpers ---------------------------------------------------------
@lru_cache(maxsize=1)
def get_graph() -> Neo4jGraph:
    """Return a singleton Neo4jGraph (constructed on first use)."""
    return Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
    )

def get_schema_string() -> str:
    """Return a mini-DSL with *only* the labels & rel-types that exist now."""
    graph = get_graph()

    labels          = graph.query("CALL db.labels() YIELD label RETURN label")
    rels            = graph.query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
    properties      = graph.query("CALL db.propertyKeys() YIELD propertyKey RETURN propertyKey")

    schema_lines = ["# === Live Neo4j Schema Snapshot ==="]
    schema_lines += [f"LABEL: {row['label']}"               for row in labels]
    schema_lines += [f"REL:   {row['relationshipType']}"    for row in rels]
    schema_lines += [f"PROP:  {row['propertyKey']}"         for row in properties]
    return "\n".join(schema_lines)

###############################################################################
# Prompt & chain definitions                                                   #
###############################################################################

# Template for simple KG chat (no tool‑use reasoning required)
chat_prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are a chat bot providing information from the GEO Help Guide. "
            "Answer as usefully and concisely as possible."
        ),
        HumanMessagePromptTemplate.from_template("{input}"),
    ]
)

# Chain: prompt → LLM → string output (via StrOutputParser)
kg_chat = chat_prompt | llm | StrOutputParser()

###############################################################################
# Tool adapter functions                                                      #
###############################################################################

ALIASES = {
    "curve settings": "CurveSettings",
    "scales": "Scale",
    "scale type": "scale_type",
}

def resolve_aliases(question: str) -> str:
    for k, v in ALIASES.items():
        question = question.replace(k, v)
    return question

def _kg_info(question: str) -> str:
    """
    Ask any natural-language question; the chain writes & executes Cypher.
    """
    question = resolve_aliases(question)
    
    result = graph_cypher_chain.invoke({"query": question})

    # Preferred answer comes back in result['result']
    if result.get("result"):
        return result["result"]

    # Fallback: flatten row data if the chain produced only raw rows
    ctx = result.get("context", [])
    if ctx:
        vals = [v for row in ctx for v in row.values()]
        return ", ".join(map(str, vals))

    return "I couldn't find that in the knowledge graph."


###############################################################################
# Tool wiring                                                                 #
###############################################################################

# LangChain Tools exposed to the ReAct agent.
# The agent decides *which* tool (if any) to call for a given thought.

tools: List[Tool] = [
    Tool.from_function(
        name="kg_info",
        description="Answer questions by querying the GEO Help Guide knowledge graph using Cypher.",
        func=_kg_info,
    )
]

###############################################################################
# Agent definition                                                            #
###############################################################################
graph_cypher_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=get_graph(),
    cypher_kwargs={"graph_schema": get_schema_string()},
    verbose=True,         
    allow_dangerous_requests=True,   # 👈 new
)

agent_prompt: PromptTemplate = PromptTemplate.from_template(
    """
You are a helpful assistant specialised in Neo4j, knowledge graphs, Cypher queries, generative AI, and the GEO Help Guide.
Always try to use the appropriate tool to provide accurate, relevant, and concise answers.
Only answer questions that relate to Neo4j, graphs, cypher, generative AI, or the GEO Help Guide.

TOOLS:
------

You have access to the following tools:

{tools}

(The only tool name available is: {tool_names})

To use a tool, follow this two-step loop **exactly**:

```
Thought: Do I need to use a tool? Yes
Action: kg_info
Action Input: <Cypher query>
Observation: <tool result>

Thought: Do I need to use a tool? No
Final Answer: <answer to the user, based ONLY on the observations>
```

Once you give the Final Answer, you must not output any more thoughts or actions.

EXAMPLES:
---------

Example 1:
Thought: Do I need to use a tool? Yes
Action: kg_info
Action Input: MATCH (a)-[r]->(b) WHERE a.name = "ODF" AND b.name = "ODT" RETURN type(r), a.name, b.name
Observation: HAS_TEMPLATE, ODF, ODT
Final Answer: ODF is related to ODT via the "HAS_TEMPLATE" relationship.

Example 2:
Thought: Do I need to use a tool? Yes
Action: kg_info
Action Input: MATCH (s:System)<-[:HAS_FILE_TYPE]-(f:FileType) RETURN f.name
Observation: ODF, OIF, ODT
Thought: Do I need to use a tool? No
Final Answer: There are 3 types of GEO file system files: ODF, OIF, and ODT.

Begin!

New input: {input}
{agent_scratchpad}
"""
)

# Build a ReAct agent and its executor (synchronous‑only for simplicity).
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor: AgentExecutor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=False,
    verbose=True,
)

###############################################################################
# Public API                                                                  #
###############################################################################

def generate_response(user_input: str) -> str:
    """Generate a final answer for *user_input* using the configured agent.

    This is the single entry-point consumed by external callers (e.g. a REST
    endpoint or a UI). It hides all LangChain plumbing details.

    Parameters
    ----------
    user_input:
        The user's natural-language question.

    Returns
    -------
    str
        The agent's *Final Answer* (never intermediate scratchpad lines).
    """

    response: Dict[str, Any] = agent_executor.invoke({"input": user_input})
    return response["output"]

__all__: List[str] = [
    "generate_response",
]
