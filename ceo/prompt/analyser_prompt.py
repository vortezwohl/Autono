import json

from langchain_core.language_models import BaseChatModel

from ceo.action.action import Action
from ceo.prompt.prompt import Prompt


class AnalyserPrompt(Prompt):
    def __init__(self, query: str, prev_results: list, action: Action):
        self.action = action
        prev_results_str = str()
        prompt = str()
        for i, result in enumerate(prev_results):
            prev_results_str += f'step{i}:{result};'
        prompt += ('Precondition: Below is the tool you can use (you can only use this tool). '
                   f'Now there is a user query: "{query}"\n'
                   'Task: What you need to do is to generate values of parameters of the function\n'
                   'Output format: {param1_name:param1_value, param2_name:param2_value, ...} '
                   '(params are given below, values are gonna be generated by you)\n'
                   'Example output: {"param1": "value1", "param2": "value2"}\n"}'
                   f'Tool: {action}\n')
        if len(prev_results_str) != 0:
            prompt += (f'Generate response according to previous actions performed by you.\n'
                       f'Previous actions: {prev_results_str}\n')
        super().__init__(prompt)


    def invoke(self, model: BaseChatModel) -> tuple[Action, dict]:
        result = model.invoke(self.prompt).content
        param = json.loads(result)
        return self.action, param
