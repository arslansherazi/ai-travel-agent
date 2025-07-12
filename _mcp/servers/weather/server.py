from _mcp.servers.weather.tools import server

if __name__ == '__main__':
    server.run(transport="sse", port=5004)
