from .llm import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent

from ..tools.vector import find_chunk
from ..tools.cypher import run_cypher

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a chat bot providing information for answering the user's questions about the GEO Help Guide."),
        ("human", "{input}"),
    ]
)

kg_chat = chat_prompt | llm | StrOutputParser()

# Tools list
tools = [
    Tool.from_function(
        name="general_chat",
        description="General queries about the knowledge graph",
        func=kg_chat.invoke,
    ), 
    Tool.from_function(
        name="lesson_content_search",
        description="For retrieving lesson content",
        func=find_chunk, 
    ),
    Tool.from_function(
        name="kg_info",
        description="For retrieving entities and relationships from the knowledge graph",
        func = run_cypher,
    )
]

agent_prompt = PromptTemplate.from_template("""
You are a Neo4j, Knowledge graph, and generative AI expert.
Be as helpful as possible using only the provided tools. 
Only answer questions that relate to Neo4j, graphs, cypher, generative AI, or the GEO Help Guide.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: general_chat
Action Input: What types of files are used for curve data?
Observation: Curve data is usually stored in ODF, OIF, or ODT formats in the GEO system.

Action: one of [{tool_names}]
Action Input: <input to the tool>
Observation: <tool result>
```

When you have a response to say to the user, or do not need a tool, use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Begin!

New input: {input}
{agent_scratchpad}
""")

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    handle_parsing_errors=False,
    verbose=True
    )

def generate_response(user_input):
    response = agent_executor.invoke({"input": user_input})
    return response['output']