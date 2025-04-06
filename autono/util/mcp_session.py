import dataclasses
from pathlib import Path

from mcp import StdioServerParameters, ClientSession, stdio_client
from mcp.client.sse import sse_client
from mcp.client.websocket import websocket_client
from typing_extensions import Any, Literal


@dataclasses.dataclass
class BaseMcpConfig:
    def to_dict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass
class StdioMcpConfig(BaseMcpConfig):
    command: str
    args: list[str]
    env: dict[str, str] | None = None
    cwd: str | Path | None = None
    encoding: str = "utf-8"
    encoding_error_handler: Literal["strict", "ignore", "replace"] = "strict"


@dataclasses.dataclass
class SseMcpConfig(BaseMcpConfig):
    url: str
    headers: dict[str, Any] | None = None
    timeout: float = 5
    sse_read_timeout: float = 30 * 5


@dataclasses.dataclass
class WebsocketMcpConfig(BaseMcpConfig):
    url: str


def mcp_session(mcp_config: BaseMcpConfig | str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if isinstance(mcp_config, StdioMcpConfig):
                async with stdio_client(StdioServerParameters(**mcp_config.to_dict())) as rw:
                    async with ClientSession(*rw) as session:
                        await session.initialize()
                        return await func(session, *args, **kwargs)
            elif isinstance(mcp_config, SseMcpConfig):
                async with sse_client(**mcp_config.to_dict()) as rw:
                    async with ClientSession(*rw) as session:
                        await session.initialize()
                        return await func(session, *args, **kwargs)
            elif isinstance(mcp_config, WebsocketMcpConfig):
                async with websocket_client(**mcp_config.to_dict()) as rw:
                    async with ClientSession(*rw) as session:
                        await session.initialize()
                        return await func(session, *args, **kwargs)
            else:
                if not isinstance(mcp_config, str):
                    raise TypeError('mcp_config must be instance of BaseMcpConfig or a string.')
                else:
                    match mcp_config[:2]:
                        case 'ht':
                            async with sse_client(**SseMcpConfig(url=mcp_config).to_dict()) as rw:
                                async with ClientSession(*rw) as session:
                                    await session.initialize()
                                    return await func(session, *args, **kwargs)
                        case 'ws':
                            async with websocket_client(**WebsocketMcpConfig(url=mcp_config).to_dict()) as rw:
                                async with ClientSession(*rw) as session:
                                    await session.initialize()
                                    return await func(session, *args, **kwargs)
                        case _:
                            raise ValueError(f'Invalid url "{mcp_config}".')
        return wrapper
    return decorator
