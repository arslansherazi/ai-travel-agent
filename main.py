import click
from mcp.servers.weather.tools import server as weather_server
from mcp.servers.booking.tools import server as booking_server
from mcp.servers.places.tools import server as places_server
from mcp.servers.trip_planner.tools import server as trip_planner_server


@click.group()
def cli():
    """AI Travel Agent MCP Servers"""
    pass


@cli.command()
@click.option("--port", default=8000, help="Port to run the server on")
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
def weather(port: int, host: str):
    """Run the Weather MCP Server"""
    weather_server.run(port=port, host=host)


@cli.command()
@click.option("--port", default=8001, help="Port to run the server on")
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
def booking(port: int, host: str):
    """Run the Booking MCP Server (requires BOOKING_API_KEY env var)"""
    booking_server.run(port=port, host=host)


@cli.command()
@click.option("--port", default=8002, help="Port to run the server on")
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
def places(port: int, host: str):
    """Run the Places MCP Server (requires GOOGLE_PLACES_API_KEY env var)"""
    places_server.run(port=port, host=host)


@cli.command()
@click.option("--port", default=8003, help="Port to run the server on")
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
def trip_planner(port: int, host: str):
    """Run the Trip Planner MCP Server (requires GOOGLE_PLACES_API_KEY and optionally BOOKING_API_KEY env vars)"""
    trip_planner_server.run(port=port, host=host)


@cli.command()
def all_servers():
    """Run all MCP servers on different ports"""
    import threading
    import time
    
    def run_server(server, port):
        server.run(port=port)
    
    servers = [
        (weather_server, 8000),
        (booking_server, 8001),
        (places_server, 8002),
        (trip_planner_server, 8003)
    ]
    
    threads = []
    for server, port in servers:
        thread = threading.Thread(target=run_server, args=(server, port))
        thread.daemon = True
        thread.start()
        threads.append(thread)
        time.sleep(1)  # Stagger startup
    
    print("All servers started:")
    print("- Weather Server: http://127.0.0.1:8000")
    print("- Booking Server: http://127.0.0.1:8001")  
    print("- Places Server: http://127.0.0.1:8002")
    print("- Trip Planner Server: http://127.0.0.1:8003")
    print("Press Ctrl+C to stop all servers")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down all servers...")


if __name__ == "__main__":
    cli()