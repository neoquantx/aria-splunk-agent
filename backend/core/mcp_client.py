import httpx
import logging
from core.config import settings

logger = logging.getLogger(__name__)

class MCPClient:
    def __init__(self):
        self.base_url = settings.SPLUNK_MCP_URL
        self.token = settings.SPLUNK_MCP_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def call_tool(self, tool_name: str, params: dict) -> dict:
        """Call a Splunk MCP tool by name with parameters."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    f"{self.base_url}/tools/{tool_name}",
                    headers=self.headers,
                    json=params
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"MCP tool {tool_name} returned {response.status_code}")
                    return {"error": response.text, "status": response.status_code}
        except Exception as e:
            logger.error(f"MCP call failed for {tool_name}: {e}")
            return {"error": str(e)}

    async def search_events(self, query: str, time_range: str = "-1h") -> dict:
        """Search Splunk events via MCP Server."""
        return await self.call_tool("splunk_search", {
            "query": query,
            "earliest_time": time_range,
            "latest_time": "now"
        })

    async def get_alerts(self) -> dict:
        """Get active Splunk alerts via MCP Server."""
        return await self.call_tool("splunk_alerts", {})

    async def run_investigation(self, indicator: str) -> dict:
        """Run an automated investigation via MCP Server."""
        return await self.call_tool("splunk_investigate", {
            "indicator": indicator,
            "scope": "full"
        })

    async def test_connection(self) -> bool:
        """Test MCP Server connectivity."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    headers=self.headers
                )
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"MCP Server not reachable: {e}")
            return False

# Singleton instance
default_mcp_client = MCPClient()
