import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.mcp import MCPServerStdio
import asyncio
from datetime import datetime
from pydantic_ai import Tool    

@Tool
def get_current_date() -> str:
    """Return the current date/time as an ISO-formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def run_async(prompt: str) -> str:
    async with agent.run_mcp_servers():
        result = await agent.run(prompt)
        return result.output

BASE_URL = f"http://localhost:8000/v1"

os.environ["BASE_URL"] = BASE_URL
os.environ["OPENAI_API_KEY"] = "abc-123" 

agent_model = OpenAIModel(
    'Qwen3-30B-A3B',
    provider=OpenAIProvider(
        base_url=os.environ["BASE_URL"], api_key=os.environ["OPENAI_API_KEY"]
    ),
)

agent = Agent(
    model=agent_model,
    tools=[get_current_date],
    system_prompt = (
        "You have access to:\n"
        "   1. get_current_time(params: dict)\n"
        "Use this tool for date/time questions.")
)

print(await run_async("what is the time?"))