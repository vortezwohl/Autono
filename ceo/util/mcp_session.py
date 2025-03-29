from mcp import StdioServerParameters as StdioMcpConfig, ClientSession, stdio_client


def mcp_session(mcp_config: StdioMcpConfig | None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if isinstance(mcp_config, StdioMcpConfig):
                async with stdio_client(mcp_config) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        return await func(session, *args, **kwargs)
            else:
                ...
        return wrapper
    return decorator
