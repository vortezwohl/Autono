import asyncio
import importlib
import unittest
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, patch

from autono import StreamableHttpMcpConfig, SseMcpConfig, StdioMcpConfig, WebsocketMcpConfig, mcp_session

module = importlib.import_module('autono.util.mcp_session')


class McpSessionTests(unittest.IsolatedAsyncioTestCase):
    async def exercise(self, config, transport_name, expected, failure=None):
        events = []
        session = AsyncMock()

        @asynccontextmanager
        async def transport(*args, **kwargs):
            events.append(('transport', args, kwargs))
            try:
                yield ('read', 'write', lambda: 'session-id') if transport_name == 'streamablehttp_client' else ('read', 'write')
            finally:
                events.append('transport closed')

        @asynccontextmanager
        async def client(*streams):
            self.assertEqual(streams, ('read', 'write'))
            try:
                yield session
            finally:
                events.append('session closed')

        @mcp_session(config)
        async def caller(actual, value, *, suffix):
            self.assertIs(actual, session)
            session.initialize.assert_awaited_once()
            if failure:
                raise failure
            return value + suffix

        with patch.object(module, transport_name, transport), patch.object(module, 'ClientSession', client):
            if failure:
                with self.assertRaises(type(failure)):
                    await caller('hello', suffix=' world')
            else:
                self.assertEqual(await caller('hello', suffix=' world'), 'hello world')
        self.assertEqual(events[0][2], expected)
        self.assertEqual(events[-2:], ['session closed', 'transport closed'])

    async def test_streamable_http_options_and_cleanup(self):
        config = StreamableHttpMcpConfig('https://example.com/mcp', {'User-Agent': 'Autono'}, 12, 34, False)
        await self.exercise(config, 'streamablehttp_client', config.to_dict())

    async def test_exception_and_cancellation_cleanup(self):
        config = StreamableHttpMcpConfig('https://example.com/mcp')
        for failure in (RuntimeError('tool failed'), asyncio.CancelledError()):
            await self.exercise(config, 'streamablehttp_client', config.to_dict(), failure)

    async def test_existing_transports_and_url_defaults(self):
        for config, name, expected in (
            (StdioMcpConfig('python', ['server.py']), 'stdio_client', {}),
            (SseMcpConfig('https://example.com/sse'), 'sse_client', SseMcpConfig('https://example.com/sse').to_dict()),
            (WebsocketMcpConfig('ws://example.com'), 'websocket_client', {'url': 'ws://example.com'}),
            ('https://example.com/sse', 'sse_client', SseMcpConfig('https://example.com/sse').to_dict()),
            ('ws://example.com', 'websocket_client', {'url': 'ws://example.com'}),
        ):
            with self.subTest(config=config):
                await self.exercise(config, name, expected)


if __name__ == '__main__':
    unittest.main()
