from _mcp.servers.trip_planner.tools import server

if __name__ == '__main__':
    server.run(transport="sse", port=5003, host="0.0.0.0")
