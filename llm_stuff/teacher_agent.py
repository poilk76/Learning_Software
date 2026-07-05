from pydantic import BaseModel
from langchain.agents import create_agent
from datetime import datetime


agent = create_agent(
    model='ollama:gemma4:e2b',
    tools=[],
)

res = agent.invoke(
    {"messages": [{"role":"user","content":"What\'s time is now"}]},
)

print(res)