from sympy import simplify
from dotenv import load_dotenv
from ceo import (
    Agent,
    Personality,
    get_openai_model,
    agentic,
    ability
)
from ceo.brain.hook import BeforeActionTaken, AfterActionTaken
from ceo.message import BeforeActionTakenMessage, AfterActionTakenMessage

from duckduckgo_search import DDGS

load_dotenv()
ddgs = DDGS()
model = get_openai_model()


@ability(model)
def calculator(expr: str) -> float:
    # this function only accepts a single math expression
    return simplify(expr)


@ability(model)
def write_file(filename: str, content: str) -> str:
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    return f'{content} written to {filename}.'


@ability
def search_on_duckduckgo(keywords: list[str], max_results_for_each_keywords: int = 3) -> dict:
    # search on duckduckgo if you don't know clearly about something
    # you can search several keywords at the same time with `search_on_duckduckgo`
    results = dict()
    for kw in keywords:
        search_results = ddgs.text(
            keywords=kw,
            region='wt-wt',
            safesearch='off',
            timelimit=None,
            backend='auto',
            max_results=max_results_for_each_keywords
        )
        for _res in search_results:
            _title = _res.get('title', 'unknown')
            _res.pop('title')
            _link = _res.get('href', 'unknown')
            _res.pop('href')
            _res['source'] = f'({_title})[{_link}]'
            _content = _res.get('body')
            _res.pop('body')
            _res['content'] = _content
        results[f'search results for "{kw}"'] = search_results
    return results


jack = Agent(abilities=[calculator], brain=model, name='Jack', personality=Personality.INQUISITIVE)
tylor = Agent(abilities=[write_file], brain=model, name='Tylor', personality=Personality.PRUDENT)


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


if __name__ == '__main__':
    ceo = Agent(abilities=[agent1, agent2], brain=model, name='CEO', personality=Personality.INQUISITIVE)
    radius = '(10.01 * 10.36 * 3.33 / 2 * 16)'  # 2762.663904
    pi = 3.14159
    output_file = 'result.txt'
    request = f"Here is a sphere with radius of {radius} cm and pi here is {pi}, find the area and volume respectively then write the results into a file called '{output_file}'."
    result = ceo.assign(request).just_do_it(BeforeActionTaken(before_action_taken), AfterActionTaken(after_action_taken))  # area = 95910378.2949379, volume = 88322713378.13666
    print(f'Result: {result}')
