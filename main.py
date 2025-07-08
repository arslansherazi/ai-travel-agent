import os
import click
from mcp.servers.weather import WeatherMCPServer
from mcp.server import run_mcp_server_http


@click.group()
def cli():
    """OpenAI Agents SDK MCP Servers"""
    pass


@cli.command()
@click.option("--port", default=8000, help="Port to run the server on")
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
@click.option("--api-key", help="Weather API key (or set WEATHER_API_KEY env var)")
def weather(port: int, host: str, api_key: str = None):
    """Run the Weather MCP Server"""
    api_key = api_key or os.environ.get("WEATHER_API_KEY")
    if not api_key:
        raise ValueError("Weather API key not provided. Set WEATHER_API_KEY env var or pass --api-key")

    server = WeatherMCPServer(api_key=api_key)
    run_mcp_server_http(server, host=host, port=port)


if __name__ == "__main__":
    cli()