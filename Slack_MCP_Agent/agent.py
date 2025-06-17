import json
import os

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

from .prompt import SLACK_PROMPT
from dotenv import load_dotenv


load_dotenv()

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_TEAM_ID = os.getenv("SLACK_TEAM_ID")
SLACK_CHANNEL_IDS  = os.getenv("SLACK_CHANNEL_IDS")

if SLACK_BOT_TOKEN is None:
    raise ValueError("SLACK_BOT_TOKEN is not set")
if SLACK_TEAM_ID is None:
    raise ValueError("SLACK_TEAM_ID is not set")
if SLACK_CHANNEL_IDS is None:
    raise ValueError("SLACK_CHANNEL_IDS is not set")


SLACK_MCP_HEADERS = ({
    "SLACK_BOT_TOKEN": f"{SLACK_BOT_TOKEN}", 
    "SLACK_TEAM_ID": f"{SLACK_TEAM_ID}",
    "SLACK_CHANNEL_IDS": f"{SLACK_CHANNEL_IDS}"
})

root_agent = Agent(
    model="gemini-2.0-flash",
    name="Slack_MCP_Agent",
    instruction=SLACK_PROMPT,
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command="npx",
                args=["-y",  "@modelcontextprotocol/server-slack"],
                env= SLACK_MCP_HEADERS
            )
        ),
    ],
)