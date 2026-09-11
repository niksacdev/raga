"""Run the self-contained local simulation demo."""

import asyncio

from src.mcp_client.client import main

if __name__ == "__main__":
    asyncio.run(main())
