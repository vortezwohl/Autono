from mcp.types import Tool, CallToolResult

from ceo.ability.base_ability import BaseAbility

DEFAULT_RETURNS = "<class 'str'>"
NONE = '/'


class BaseMcpAbility(BaseAbility):
    def __init__(self, mcp_tool: Tool, mcp_config: any):
        self._mcp_config = mcp_config
        _descr = {
            'brief_description': mcp_tool.description,
            'parameters': [
                {'parameter_name': k, 'type': v.get("type", DEFAULT_RETURNS),
                 'description': v.get('description', NONE)}
                for k, v in mcp_tool.inputSchema.get('properties', dict()).items()
            ]
        }
        super().__init__(
            name=mcp_tool.name,
            description=_descr,
            parameters=mcp_tool.inputSchema.get('properties', dict()),
            returns=DEFAULT_RETURNS
        )

    async def __create_session_and_call_tool(self, *args, **kwargs) -> CallToolResult: ...

    def __call__(self, *args, **kwargs): ...

    @property
    def mcp_config(self) -> any:
        return self._mcp_config
