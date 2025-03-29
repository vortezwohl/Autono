from mcp import StdioServerParameters

from ceo import (
    StdioMcpAgent,
    get_openai_model,
    ability
)
from ceo.brain.hook import BeforeActionTaken, AfterActionTaken
from ceo.message import BeforeActionTakenMessage, AfterActionTakenMessage
from dotenv import load_dotenv

load_dotenv()
model = get_openai_model()


@ability(model)
def write_file(filename: str, content: str) -> str:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f'{content} written to {filename}.'


def before_action_taken(agent: StdioMcpAgent, message: BeforeActionTakenMessage):
    print(f'Agent: {agent.name}, Next move: {message.ability.name}')
    return message


def after_action_taken(agent: StdioMcpAgent, message: AfterActionTakenMessage):
    print(f'Agent: {agent.name}, Action taken: {message.summarization}')
    return message


if __name__ == '__main__':
    mcp_config = StdioServerParameters(
        command='python',
        args=['./playwright-plus-python-mcp.py'],
        env=dict(),
        cwd='./mcp_server'
    )
    mcp_agent = StdioMcpAgent(mcp_config=mcp_config, brain=model)
    mcp_agent.grant_ability(write_file)
    output_file = 'result.txt'
    request = f'Navigate to https://www.google.com. Then write down what you see here: {output_file}.'
    result = mcp_agent.assign(request).just_do_it(
        BeforeActionTaken(before_action_taken),
        AfterActionTaken(after_action_taken)
    )
    print(result.conclusion)
