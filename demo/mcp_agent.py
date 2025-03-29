from ceo import (
    McpAgent,
    get_openai_model,
    ability,
    sync_call,
    StdioMcpConfig,
    __BLOG__
)
from ceo.util.mcp_session import mcp_session
from ceo.brain.hook import BeforeActionTaken, AfterActionTaken
from ceo.message import BeforeActionTakenMessage, AfterActionTakenMessage
from dotenv import load_dotenv

load_dotenv()
model = get_openai_model()
stdio_mcp_config = StdioMcpConfig(
    command='python',
    args=['./playwright-plus-python-mcp.py'],
    env=dict(),
    cwd='./mcp_server'
)


@ability(model)
def write_file(filename: str, content: str) -> str:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f'{content} written to {filename}.'


def before_action_taken(agent: McpAgent, message: BeforeActionTakenMessage):
    print(f'Agent: {agent.name}, Next move: {message.ability.name}')
    return message


def after_action_taken(agent: McpAgent, message: AfterActionTakenMessage):
    print(f'Agent: {agent.name}, Action taken: {message.summarization}')
    return message


@sync_call
@mcp_session(stdio_mcp_config)
async def run(session, request: str) -> str:
    mcp_agent = await McpAgent(session=session, brain=model).fetch_abilities()
    mcp_agent.grant_ability(write_file)
    result = await mcp_agent.assign(request).just_do_it(
        BeforeActionTaken(before_action_taken),
        AfterActionTaken(after_action_taken)
    )
    return result.conclusion


if __name__ == '__main__':
    output_file = 'result.txt'
    request = (f'What is reinforcement learning? Bing (www.bing.com) it and write down the search results into local file: {output_file}. '
               f'Then navigate to {__BLOG__}.')
    ret = run(request)
    print(ret)
