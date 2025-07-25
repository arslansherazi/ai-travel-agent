from _mcp.servers.places.tools import server

if __name__ == '__main__':
    server.run(transport="sse", port=5002, host="0.0.0.0")
