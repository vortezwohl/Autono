from typing_extensions import override
from mcp import ClientSession, StdioServerParameters, stdio_client
from mcp.types import Tool, CallToolResult

from ceo.ability.base_mcp_ability import BaseMcpAbility
from ceo.util.synchronized_call import synchronized_call


class StdioMcpAbility(BaseMcpAbility):
    def __init__(self, mcp_tool: Tool, mcp_config: StdioServerParameters):
        super().__init__(
            mcp_tool=mcp_tool,
            mcp_config=mcp_config
        )

    @override
    async def __create_session_and_call_tool(self, *args, **kwargs) -> CallToolResult:
        async with stdio_client(self.mcp_config) as rw:
            async with ClientSession(*rw) as session:
                await session.initialize()
                _res = await session.call_tool(name=self.name, arguments=kwargs)
        return _res

    @override
    def __call__(self, *args, **kwargs):
        _res = synchronized_call(self.__create_session_and_call_tool, *args, **kwargs)
        _status = 'SUCCESSFUL' if not _res.isError else 'FAILED'
        return (f'McpAbility(mcp_tool="{self.name}") was {_status}.\n'
                f'Result: "{_res.content}"')
