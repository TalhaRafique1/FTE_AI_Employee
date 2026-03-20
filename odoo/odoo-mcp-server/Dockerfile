FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY odoo_mcp_server.py .

# Expose port for MCP server
EXPOSE 8810

# Run the server
CMD ["python", "odoo_mcp_server.py"]
