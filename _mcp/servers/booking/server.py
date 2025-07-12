from _mcp.servers.booking.tools import server

if __name__ == '__main__':
    server.run(transport="sse", port=5001)
