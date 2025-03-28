import json

from mcp.types import Tool
from typing_extensions import override

from ceo.ability.base_ability import BaseAbility
from ceo.exception.invalid_mcp_tool_exception import InvalidMcpToolException

UNKNOWN = 'Unknown'
NONE = '/'


# todo 封装 Mcp tool
class McpAbility(BaseAbility):
    def __init__(self, mcp_tool: Tool):
        self.__name__ = mcp_tool.name
        _input_schema_dict = mcp_tool.inputSchema
        if 'properties' not in _input_schema_dict.keys() or not isinstance(_input_schema_dict.get('properties'), dict):
            raise InvalidMcpToolException(mcp_tool=mcp_tool)
        self.__doc__ = json.dumps({'brief_description': mcp_tool.description, 'parameters': [
            {'name': k, 'type': 'str', 'description': v.get('description', NONE)}
            for k, v in _input_schema_dict['properties'].items()
        ]}, ensure_ascii=False)
        _params_dict = dict()
        for para in _input_schema_dict.get('required', list()):
            _params_dict[para] = str()
        super().__init__(
            name=self.__name__,
            description=self.__doc__,
            parameters=_params_dict,
            returns=f'A string feedback of {self.__name__}'
        )

    @override
    def __call__(self, *args, **kwargs):
        ...

    @override
    def to_dict(self) -> dict: ...

if __name__ == '__main__':
    tool = Tool(
        name="playwright_screenshot",
        description="Take a screenshot of the current page or a specific element",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "selector": {"type": "string", "description": "CSS selector for element to screenshot,null is full page"},
            },
            "required": ["name"]
        }
    )
    McpAbility(tool)
