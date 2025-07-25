FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the necessary files for booking service
COPY _mcp/servers/base_service.py _mcp/servers/
COPY _mcp/servers/constants.py _mcp/servers/
COPY _mcp/servers/__init__.py _mcp/servers/
COPY _mcp/servers/booking/ _mcp/servers/booking/
COPY _mcp/__init__.py _mcp/

EXPOSE 5001

CMD ["python", "-m", "_mcp.servers.booking.server"]
