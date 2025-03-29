from sympy import simplify
from dotenv import load_dotenv
from ceo import (
    Agent,
    McpAgent,
    Personality,
    get_openai_model,
    agentic,
    ability,
    StdioMcpConfig,
    mcp_session,
    sync_call
)
from ceo.brain.hook import BeforeActionTaken, AfterActionTaken
from ceo.message import BeforeActionTakenMessage, AfterActionTakenMessage

load_dotenv()
model = get_openai_model()
stdio_mcp_config = StdioMcpConfig(
    command='python',
    args=['./playwright-plus-python-mcp.py'],
    env=dict(),
    cwd='./mcp_server'
)


@ability(model)
def calculator(expr: str) -> float:
    # this function only accepts a single math expression
    return simplify(expr)


@ability(model)
def write_file(filename: str, content: str) -> str:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f'{content} written to {filename}.'


jack = Agent(abilities=[calculator], brain=model, name='Jack', personality=Personality.INQUISITIVE)
tylor = Agent(abilities=[write_file], brain=model, name='Tylor', personality=Personality.PRUDENT)


@sync_call
@mcp_session(stdio_mcp_config)
async def run(session, request: str):
    @agentic(jack)
    def agent1():
        return

    @agentic(tylor)
    def agent2():
        return

    def before_action_taken(agent: Agent, message: BeforeActionTakenMessage):
        print(f'Agent: {agent.name}, Next move: {message}')
        return message

    def after_action_taken(agent: Agent, message: AfterActionTakenMessage):
        print(f'Agent: {agent.name}, Action taken: {message}')
        return message

    mcp_agent = await McpAgent(session, model, 'mcp_agent').fetch_abilities()
    mcp_agent.grant_abilities([agent1, agent2])
    return (await mcp_agent.assign(request).just_do_it(
        BeforeActionTaken(before_action_taken),
        AfterActionTaken(after_action_taken)
    )).conclusion


if __name__ == '__main__':
    radius = '(10.01 * 10.36 * 3.33 / 2 * 16)'  # 2762.663904
    pi = 3.14159
    output_file = 'result.txt'  # area = 95910378.2949379, volume = 88322713378.13666
    request = f"Here is a sphere with radius of {radius} cm and pi here is {pi}, find the area and volume respectively then write the results into a file called '{output_file}'."
    ret = run(request)
    print(ret)
    ret = run('Search on bing for album MAYHEM by lady gaga')
    print(ret)
