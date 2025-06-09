from .llm import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent

from .tools.vector import find_chunk
from .tools.cypher import run_cypher

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
        name="General Chat",
        description="For general knowledge graph chat not covered by other tools",
        func=kg_chat.invoke,
    ), 
    Tool.from_function(
        name="Lesson content search",
        description="For when you need to find information in the lesson content",
        func=find_chunk, 
    ),
    Tool.from_function(
        name="Knowledge Graph information",
        description="For when you need to find information about the entities and relationship in the knowledge graph",
        func = run_cypher,
    )
]

agent_prompt = PromptTemplate.from_template("""
You are a Neo4j, Knowledge graph, and generative AI expert.
Be as helpful as possible and return as much information as possible.
Only answer questions that relate to Neo4j, graphs, cypher, generative AI, or associated subjects.
        
Always use a tool and only use the information provided in the context.

TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

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
    handle_parsing_errors=True,
    verbose=True
    )

def generate_response(user_input):
    response = agent_executor.invoke({"input": user_input})
    return response['output']