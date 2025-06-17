"""kg_agent.py
================

An augmented-language-model (LLM) agent that answers questions about Neo4j, the
GEO Help Guide, graphs, Cypher, and generative AI by orchestrating three helper
functions exposed as LangChain `Tool`s.

The public entry-point is :pyfunc:`generate_response`, which routes the user's
question through a ReAct-style agent that decides when (and how) to invoke the
underlying tools.

This module is **import-side-effect-free**: importing it does not trigger any
network calls or heavyweight operations. The LangChain agent and executor are
instantiated eagerly so that a call to :pyfunc:`generate_response` is one RTT.
"""
from __future__ import annotations

from typing import Any, Dict, List

from langchain.agents import AgentExecutor, create_react_agent
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from .llm import llm  # Local LLM wrapper
from ..tools.cypher import run_cypher
from ..tools.vector import find_chunk

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

def _kg_info(cypher: str) -> str:
    """Run a Cypher query against the knowledge graph and return the result.

    Parameters
    ----------
    cypher:
        A **read-only** Cypher statement written by the agent.

    Returns
    -------
    str
        Serialised representation of the query result.
    """

    results = run_cypher(cypher)
    if isinstance(results, list) and results and isinstance(results[0], dict):
        values = [v for row in results for v in row.values()]
        return ", ".join(values)
    return str(results)


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
