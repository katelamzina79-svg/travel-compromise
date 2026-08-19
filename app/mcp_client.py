import os
import json
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

MCP_URL = os.getenv("MCP_SERVER_URL")


@asynccontextmanager
async def get_mcp_session():
    """Открывает сессию MCP на время одного запроса."""
    async with streamable_http_client(MCP_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

async def call_tool(tool_name: str, arguments: dict) -> dict:
    """Вызывает инструмент MCP с подробным логированием ошибки."""
    try:
        print(f"[MCP] URL configured: {bool(MCP_URL)}")
        print(f"[MCP] Calling tool: {tool_name}")
        print(f"[MCP] Arguments: {arguments}")

        async with get_mcp_session() as session:
            print("[MCP] Session initialized")

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            print(f"[MCP] Tool result received: {result}")

            for content in result.content:
                if hasattr(content, "text"):
                    print(f"[MCP] Raw content: {content.text}")
                    return json.loads(content.text)

        return {}

    except Exception as e:
        import traceback

        print(f"[MCP ERROR] {type(e).__name__}: {e}")
        print("[MCP ERROR] Full traceback:")
        traceback.print_exc()

        raise

async def search_multitransport(origin: str, destination: str, departure_date: str) -> dict:
    return await call_tool(
        "search_multitransport",
        {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
        },
    )


async def search_hotels(city_name: str, check_in: str, check_out: str, price_max: float | None = None) -> dict:
    args = {
        "city_name": city_name,
        "check_in": check_in,
        "check_out": check_out,
    }
    if price_max:
        args["price_max"] = price_max
    return await call_tool("search_hotels", args)
