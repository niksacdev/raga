#!/usr/bin/env python3
"""
MCP Client for RAGA Robotic Arm Telemetry

This client demonstrates how to connect to the RAGA MCP server and interact with the
robotic telemetry interface.
"""

import asyncio
import json
import logging
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

# Try to import mcp client modules
try:
    from mcp.client import MCPClient as BaseMCPClient
except ImportError:
    print("MCP client library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp"])
    from mcp.client import MCPClient as BaseMCPClient

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("mcp_client")


class RAGAMCPClient:
    """Client for interacting with the RAGA MCP Server"""

    def __init__(self, host: str = "localhost", port: int = 8000):
        """Initialize the MCP client

        Args:
            host: MCP server hostname
            port: MCP server port
        """
        self.host = host
        self.port = port
        self.client = None
        self.server_url = f"http://{host}:{port}"
        logger.info(
            f"Initializing RAGA MCP client for server at {self.server_url}")

    async def connect(self):
        """Connect to the MCP server"""
        logger.info(f"Connecting to MCP server at {self.server_url}")
        # In a real implementation, this would use the MCP client library
        # For now, we'll simulate the connection
        self.client = BaseMCPClient(self.server_url)
        await self.client.initialize()
        logger.info("Connected to MCP server successfully")

    async def get_server_info(self) -> Dict[str, Any]:
        """Get information about the MCP server

        Returns:
            Server information data
        """
        logger.info("Requesting server information")
        response = await self.client.get_resource("server://info")
        return response

    async def get_robot_telemetry(self, factory_id: str, robot_id: str) -> Dict[str, Any]:
        """Get telemetry for a specific robot

        Args:
            factory_id: Factory identifier
            robot_id: Robot identifier

        Returns:
            Robot telemetry data
        """
        logger.info(
            f"Requesting telemetry for robot {robot_id} in factory {factory_id}")
        response = await self.client.get_resource(f"robots://{factory_id}/{robot_id}")
        return response

    async def update_robot_state(self, factory_id: str, robot_id: str, **updates) -> Dict[str, Any]:
        """Update state for a specific robot

        Args:
            factory_id: Factory identifier
            robot_id: Robot identifier
            **updates: Robot state updates (joint_angles, end_effector_pose, etc.)

        Returns:
            Updated robot state
        """
        logger.info(
            f"Updating state for robot {robot_id} in factory {factory_id}")
        params = {
            "factory_id": factory_id,
            "robot_id": robot_id,
            **updates
        }
        response = await self.client.call_tool("update_robot_state", **params)
        return response

    async def list_robots(self) -> Dict[str, Any]:
        """List all available robots

        Returns:
            Robots grouped by factory
        """
        logger.info("Requesting list of available robots")
        response = await self.client.call_tool("list_available_robots")
        return response

    async def get_calibration_prompt(self) -> Dict[str, Any]:
        """Get the robot calibration instructions prompt

        Returns:
            Calibration procedure instructions
        """
        logger.info("Requesting calibration prompt")
        response = await self.client.get_prompt("robot_calibration_instructions")
        return response


async def main():
    """Example usage of the RAGA MCP Client"""
    client = RAGAMCPClient()
    try:
        await client.connect()

        # Get server information
        server_info = await client.get_server_info()
        print("\n==== SERVER INFO ====")
        print(json.dumps(server_info, indent=2))

        # Create some example robots
        factory_id = "warehouse7"
        robot_id = "arm3"

        # Get robot telemetry
        telemetry = await client.get_robot_telemetry(factory_id, robot_id)
        print(f"\n==== TELEMETRY FOR {factory_id}/{robot_id} ====")
        print(json.dumps(telemetry, indent=2))

        # Update robot state - set position
        new_pose = {
            "end_effector_pose": {
                "x": 500,
                "y": 0,
                "z": 1000,
                "roll": 0,
                "pitch": 90,
                "yaw": 0
            }
        }
        updated_state = await client.update_robot_state(factory_id, robot_id, **new_pose)
        print(f"\n==== UPDATED STATE FOR {factory_id}/{robot_id} ====")
        print(json.dumps(updated_state, indent=2))

        # Get a list of all robots
        robots = await client.list_robots()
        print("\n==== AVAILABLE ROBOTS ====")
        print(json.dumps(robots, indent=2))

        # Get calibration instructions
        calibration = await client.get_calibration_prompt()
        print("\n==== CALIBRATION INSTRUCTIONS ====")
        print(json.dumps(calibration, indent=2))

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
    finally:
        if client.client:
            await client.client.close()


if __name__ == "__main__":
    asyncio.run(main())
