from mcp.types import Tool


class InvalidMcpToolException(TypeError):
    def __init__(self, mcp_tool: Tool):
        super().__init__(f'"{mcp_tool.name}" is not an invalid MCP tool.')
