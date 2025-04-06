from autono import (
    Agent,
    Personality,
    get_openai_model,
    ability
)
from autono.brain.hook import BeforeActionTaken, AfterActionTaken
from autono.message import BeforeActionTakenMessage, AfterActionTakenMessage
from sympy import simplify
from dotenv import load_dotenv
import pyttsx3

# config tts model
tts_engine = pyttsx3.init()
tts_engine.setProperty('rate', 150)
tts_engine.setProperty('volume', 1.0)
# noinspection PyUnresolvedReferences
tts_engine.setProperty('voice', tts_engine.getProperty('voices')[3].id)

load_dotenv()
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


def before_action_taken(agent: Agent, message: BeforeActionTakenMessage):
    print(f'Agent: {agent.name}, Next move: {message.ability.name}')
    tts_engine.say(f"I'm going to use {message.ability.name}.")
    tts_engine.runAndWait()
    return message


def after_action_taken(agent: Agent, message: AfterActionTakenMessage):
    print(f'Agent: {agent.name}, Action taken: {message.summarization}')
    tts_engine.say(message.summarization)
    tts_engine.runAndWait()
    return message


if __name__ == '__main__':
    vortezwohl = Agent(abilities=[calculator, write_file], brain=model, name='vortezwohl', personality=Personality.INQUISITIVE)
    radius = '(10.01 * 10.36 * 3.33 / 2 * 16)'  # 2762.663904
    pi = 3.14159
    output_file = 'result.txt'
    request = f"Here is a sphere with radius of {radius} cm and pi here is {pi}, find the area and volume respectively then write the results into a file called '{output_file}'."
    result = vortezwohl.assign(request).just_do_it(
        BeforeActionTaken(before_action_taken),
        AfterActionTaken(after_action_taken)
    )  # area = 95910378.2949379, volume = 88322713378.13666
    tts_engine.say(result.conclusion)
    tts_engine.runAndWait()
    tts_engine.stop()
