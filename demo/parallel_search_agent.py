"""Run an Autono agent with anonymous Parallel search and fetch abilities."""
import argparse

from autono import McpAgent, StreamableHttpMcpConfig, get_openai_model, mcp_session, sync_call


parallel_mcp_config = StreamableHttpMcpConfig(
    url='https://search.parallel.ai/mcp',
    headers={'User-Agent': 'Autono/1.1.2 (Parallel Search MCP example)'},
)


@sync_call
@mcp_session(parallel_mcp_config)
async def run(session, request: str) -> str:
    agent = await McpAgent(
        session=session, brain=get_openai_model(), name='ParallelSearchAgent'
    ).fetch_abilities()
    result = await agent.assign(request).just_do_it()
    return result.conclusion


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('request', nargs='?', default=(
        'Search for the official Model Context Protocol documentation, '
        'fetch the relevant page and explain Streamable HTTP with source URLs.'
    ))
    print(run(request=parser.parse_args().request))
