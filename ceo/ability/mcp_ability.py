from mcp.types import Tool
from typing_extensions import override

from ceo.ability.base_ability import BaseAbility
from ceo.exception.invalid_mcp_tool_exception import InvalidMcpToolException

UNKNOWN = 'Unknown'
NONE = 'None'


# todo 封装 Mcp tool
class McpAbility(BaseAbility):
    def __init__(self, mcp_tool: Tool):
        self.__name__ = mcp_tool.name
        _input_schema_dict = mcp_tool.inputSchema
        if 'properties' not in _input_schema_dict.keys() or not isinstance(_input_schema_dict.get('properties'), dict):
            raise InvalidMcpToolException(mcp_tool=mcp_tool)
        _params = [
            {
                'name': k,
                'type': 'str',
                'description': v.get('description', NONE)
            } for k, v in _input_schema_dict['properties'].items()
        ]
        _tmp_doc = {
            'brief_description': mcp_tool.description,
            'parameters': mcp_tool.inputSchema
        }

    @override
    def __call__(self, *args, **kwargs):
        ...
