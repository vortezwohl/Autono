<div align="center">
    <p>
        <img src="https://github.com/vortezwohl/CEO/releases/download/icon/ceo-icon-inv.png" alt="CEO" height="105">
    </p>
    <p style="font-weight: 200; font-size: 19px">
        一个基于 <a href="https://arxiv.org/abs/2210.03629">ReAct</a> 范式的超轻量级智能体框架.
    </p>
</div>

<h4 align="center">
    <p>
        <a href="https://github.com/vortezwohl/CEO-Agentic-AI-Framework/blob/main/README.md">English</a> |
        <a href="https://github.com/vortezwohl/CEO-Agentic-AI-Framework/blob/main/i18n/README_zh-hant.md">繁體中文</a> |
        <a href="https://github.com/vortezwohl/CEO-Agentic-AI-Framework/blob/main/i18n/README_ja-jp.md">日本語</a> |
        <b>简体中文</b>
    </p>
</h4>

<h5></br></h5>

## 安装

- 从 [PYPI](https://pypi.org/project/ceo-py/)

    ```shell
    pip install ceo-py
    ```

- 从 [Github](https://github.com/vortezwohl/CEO/releases)

    先下载 .whl 文件，然后执行

    ```shell
    pip install ./ceo_py-x.x.x-py3-none-any.whl
    ```

## 引用

如果您正在将 `CEO` 框架整合到您的研究中，请务必正确**引用**它，以声明它对您工作的贡献.

```latex
@software{Wu_CEO-Autonomous-Agent-Framework_2024,
author = {Wu, Zihao},
license = {GPL-3.0},
month = oct,
title = {{CEO-Autonomous-Agent-Framework}},
url = {https://github.com/vortezwohl/CEO-Autonomous-Agent-Framework},
version = {0.13.1},
year = {2024}
}
```

## 快速开始

要开始搭建您自己的智能体，请按照以下步骤执行。

1. 设置环境变量 `DEEPSEEK_API_KEY`

    ```
    # .env
    DEEPSEEK_API_KEY=sk-...
    ```

2. 从 `CEO` 引入 SDKs

    - `Agent` 让您实例化一个智能体。

    - `Personality` 是一个枚举类，用于设定智能体的个性：

        - `Personality.PRUDENT` 使智能体的行为更加谨慎。

        - `Personality.INQUISITIVE` 鼓励智能体更主动尝试和探索。

    - `get_deepseek_model` 给您一个 `BaseChatModel` 作为思维引擎。

    - `@ability(brain: BaseChatModel, cache: bool = True, cache_dir: str = '')` 是一个装饰器，用来将函数声明为一个 `Ability`.

    - `@agentic(agent: Agent)` 是一个装饰器，用来将函数声明为一个  `AgenticAbility`.

    ```python
    from ceo import (
        Agent,
        Personality,
        get_deepseek_model,
        ability,
        agentic
    )
    ```

3. 声明函数作为基本能力

    ```python
    @ability
    def calculator(expr: str) -> float:
        # this function only accepts a single math expression
        return simplify(expr)

    @ability
    def write_file(filename: str, content: str) -> str:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f'{content} written to {filename}.'
    ```

4. 实例化一个智能体

    您可以在实例化智能体的时候赋予其能力。

    ```python
    model = get_deepseek_model()
    agent = Agent(abilities=[calculator, write_file], brain=model, name='CEO', personality=Personality.INQUISITIVE)
    ```

    - 您也可以稍后赋予更多能力给智能体：

        ```python
        agent.grant_ability(calculator)
        ```

        或

        ```python
        agent.grant_abilities([calculator])
        ```

    - 剥夺能力：

        ```python
        agent.deprive_ability(calculator)
        ```

        或

        ```python
        agent.deprive_abilities([calculator])
        ```
    
    您可以使用方法 `change_personality(personality: Personality)` 更改智能体的个性。

    ```python
    agent.change_personality(Personality.PRUDENT)
    ```

5. 指定请求给您的智能体

    ```python
    agent.assign("Here is a sphere with radius of (1 * 9.5 / 2 * 2) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
    ```

6. 将其余工作交给您的智能体

    ```python
    response = agent.just_do_it()
    print(response)
    ```

> `ceo` 也支持多智能体协作场景，可用 `@agentic(agent: Agent)`, 声明一个函数为智能体呼叫能力，然后赋予给另一个智能体。[查看示例](#多智能体协作)。

## 可观测性

为了使智能体的执行过程具备可观测性，我提供了两个钩子，分别是 `BeforeActionTaken` 和 `AfterActionTaken`。
它们允许你观察并介入智能体每一步动作的决策与执行结果。
你可以通过 `BeforeActionTaken` 钩子获取并修改智能体对下一步动作的决策结果，
而 `AfterActionTaken` 钩子则允许你获取并修改动作的执行结果（被篡改的执行结果会成为智能体记忆的一部分）。

要开始使用钩子，请按照以下步骤操作。

1. 从 `CEO` 中引入钩子

    ```python
    from ceo.brain.hook import BeforeActionTaken, AfterActionTaken
    from ceo.message import BeforeActionTakenMessage, AfterActionTakenMessage
    ```

2. 声明函数，并将函数封装为钩子

    ```python
    def before_action_taken(agent: Agent, message: BeforeActionTakenMessage):
        print(f'Agent: {agent.name}, Next move: {message}')
        return message

    def after_action_taken(agent: Agent, message: AfterActionTakenMessage):
        print(f'Agent: {agent.name}, Action taken: {message}')
        return message

    before_action_taken_hook = BeforeActionTaken(before_action_taken)
    after_action_taken_hook = AfterActionTaken(after_action_taken)
    ```

    > 在这两个钩子函数中，你拦截了消息并打印了消息中的信息。之后，你将消息原封不动地返回给智能体。当然，你也可以选择**修改**消息中的信息，从而实现对智能体执行过程的干预。

3. 在智能体执行过程中使用钩子

    ```python
    agent.assign(...).just_do_it(before_action_taken_hook, after_action_taken_hook)
    ```

## 范例

- ### 复合任务

    1. 计算一个球体的表面积和体积，然后将结果写入文件。

        ```python
        from ceo import (
            Agent,
            Personality,
            get_openai_model,
            ability
        )
        from ceo.brain.hook import BeforeActionTaken, AfterActionTaken
        from ceo.message import BeforeActionTakenMessage, AfterActionTakenMessage
        from sympy import simplify
        from dotenv import load_dotenv

        load_dotenv()


        @ability
        def calculator(expr: str) -> float:
            # this function only accepts a single math expression
            return simplify(expr)


        @ability
        def write_file(filename: str, content: str) -> str:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return f'{content} written to {filename}.'


        def before_action_taken(agent: Agent, message: BeforeActionTakenMessage):
            print(f'Agent: {agent.name}, Next move: {message}')
            return message


        def after_action_taken(agent: Agent, message: AfterActionTakenMessage):
            print(f'Agent: {agent.name}, Action taken: {message}')
            return message


        if __name__ == '__main__':
            ceo = Agent(abilities=[calculator, write_file], brain=get_openai_model(), name='CEO', personality=Personality.INQUISITIVE)
            radius = '(10.01 * 10.36 * 3.33 / 2 * 16)'  # 2762.663904
            pi = 3.14159
            output_file = 'result.txt'
            request = f"Here is a sphere with radius of {radius} cm and pi here is {pi}, find the area and volume respectively then write the results into a file called '{output_file}'."
            result = ceo.assign(request).just_do_it(BeforeActionTaken(before_action_taken), AfterActionTaken(after_action_taken))  # area = 95910378.2949379, volume = 88322713378.13666
            print(f'Result: {result}')
        ```

        ```
        # result.txt
        Surface Area: 95910378.2949379 cm²
        Volume: 88322713378.1367 cm³
        ```

        ```
        # stdout
        Agent: CEO, Next move: BeforeActionTakenMessage(ability={"ability_name": "calculator", "description": {"brief_description": "The `calculator` function evaluates a mathematical expression provided as a string and returns the simplified result as a float. It is designed to accept a single math expression, ensuring that the input is a valid string representation of a mathematical operation."}, "parameters_required": ["expr"], "returns": "<class 'float'>"}, arguments={'expr': '(10.01 * 10.36 * 3.33 / 2 * 16)'})
        Agent: CEO, Action taken: AfterActionTakenMessage(ability='calculator', arguments={'expr': '(10.01 * 10.36 * 3.33 / 2 * 16)'}, returns='2762.66390400000', summarization="I used the calculator ability to evaluate the expression '(10.01 * 10.36 * 3.33 / 2 * 16)', and the result is 2762.66390400000, which indicates the simplified result of the mathematical operation.")
        Agent: CEO, Next move: BeforeActionTakenMessage(ability={"ability_name": "calculator", "description": {"brief_description": "The `calculator` function evaluates a mathematical expression provided as a string and returns the simplified result as a float. It is designed to accept a single math expression, ensuring that the input is a valid string representation of a mathematical operation."}, "parameters_required": ["expr"], "returns": "<class 'float'>"}, arguments={'expr': '4 * 3.14159 * (2762.66390400000^2)'})
        Agent: CEO, Action taken: AfterActionTakenMessage(ability='calculator', arguments={'expr': '4 * 3.14159 * (2762.66390400000^2)'}, returns='95910378.2949379', summarization="I used the calculator ability to evaluate the expression '4 * 3.14159 * (2762.66390400000^2)', and the result is 95910378.2949379, which represents the simplified calculation of the given mathematical operation.")
        Agent: CEO, Next move: BeforeActionTakenMessage(ability={"ability_name": "calculator", "description": {"brief_description": "The `calculator` function evaluates a mathematical expression provided as a string and returns the simplified result as a float. It is designed to accept a single math expression, ensuring that the input is a valid string representation of a mathematical operation."}, "parameters_required": ["expr"], "returns": "<class 'float'>"}, arguments={'expr': '(4/3) * 3.14159 * (2762.66390400000^3)'})
        Agent: CEO, Action taken: AfterActionTakenMessage(ability='calculator', arguments={'expr': '(4/3) * 3.14159 * (2762.66390400000^3)'}, returns='88322713378.1367', summarization="I used the calculator ability to evaluate the expression '(4/3) * 3.14159 * (2762.66390400000^3)', and the result is 88322713378.1367, which represents the simplified value of the mathematical operation.")
        Agent: CEO, Next move: BeforeActionTakenMessage(ability={"ability_name": "write_file", "description": {"brief_description": "The `write_file` function writes the specified content to a file with the given filename. It takes two parameters: `filename`, which is the name of the file to be created or overwritten, and `content`, which is the string data to be written into the file. Upon successful writing, it returns a confirmation message indicating that the content has been written to the specified file."}, "parameters_required": ["filename", "content"], "returns": "<class 'str'>"}, arguments={'filename': 'result.txt', 'content': 'Surface Area: 95910378.2949379 cm²\nVolume: 88322713378.1367 cm³'})
        Agent: CEO, Action taken: AfterActionTakenMessage(ability='write_file', arguments={'filename': 'result.txt', 'content': 'Surface Area: 95910378.2949379 cm²\nVolume: 88322713378.1367 cm³'}, returns='Surface Area: 95910378.2949379 cm²\nVolume: 88322713378.1367 cm³ written to result.txt.', summarization="I used the write_file ability to write the specified content about surface area and volume to a file named 'result.txt'. The result confirms that the content was successfully written to the file.")
        Result: AllDoneMessage(success=True, conclusion="Your request has been fully achieved. The calculations resulted in a surface area of 95910378.2949379 cm² and a volume of 88322713378.1367 cm³, which were successfully written to 'result.txt'.", raw_response="--THOUGHT-PROCESS--  \n(Start) [Calculate radius]: I evaluated the expression '(10.01 * 10.36 * 3.33 / 2 * 16)' and obtained the radius as 2762.66390400000 cm. (--SUCCESS--)  \n(After: Calculate radius) [Calculate surface area]: I evaluated the expression '4 * 3.14159 * (2762.66390400000^2)' and obtained the surface area as 95910378.2949379 cm². (--SUCCESS--)  \n(After: Calculate surface area) [Calculate volume]: I evaluated the expression '(4/3) * 3.14159 * (2762.66390400000^3)' and obtained the volume as 88322713378.1367 cm³. (--SUCCESS--)  \n(After: Calculate volume) [Write results to file]: I wrote the surface area and volume to 'result.txt'. The content was successfully written. (--SUCCESS--)  \n\nBased on above assessments, here is my conclusion:  \n--CONCLUSION--  \nYour request has been fully achieved. The calculations resulted in a surface area of 95910378.2949379 cm² and a volume of 88322713378.1367 cm³, which were successfully written to 'result.txt'.  \n--END--", time_used=62.49354759999551, step_count=4)
        ```

- ### 多智能体协作
    
    1. 请合适的智能体计算球体的表面积和体积，将结果并写入文件。
  
        ```python
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
        ```

        > 在多智能体协作场景下，您可以为不同的智能体分配不同的个性。例如，在上述脚本中，Jack 的能力是执行计算。我希望他能多尝试和探索，所以將 Jack 的个性设置为 `Personality.INQUISITIVE`。另一方面，Taylor 的能力是创建和写入文件。对于涉及外部文件系统的操作，我希望他能够更加谨慎，所以将 Taylor 的个性设置为 `Personality.PRUDENT`。

        ```
        # result.txt
        Surface Area: 95910378.2949379 cm²
        Volume: 88322713378.1367 cm³
        ```

        ```
        # stdout
        Agent: CEO, Next move: BeforeActionTakenMessage(ability={"ability_name": "__AgenticAbility__talk_to_Jack", "description": {"brief_description": "Initiates a conversation with \"Jack\" to use its abilities.", "detailed_description": "First, carefully consider and explore Jack's potential abilities in solving your tasks, then, if you need Jack's help, you must tell comprehensively, precisely and exactly what you need Jack to do.", "self_introduction_from_Jack": "My name is Jack. What can I do: I can evaluate mathematical expressions as a calculator and provide the result as a float. Additionally, I have the ability to retrieve my personal information, but this can only be done once.", "hint": "By reading <self_introduction_from_Jack>, you can learn what Jack can do, and then decide whether to initiates a conversation with Jack according to its abilities."}, "parameters_required": [], "returns": "<class 'str'>"}, arguments={'expression': '(10.01 * 10.36 * 3.33 / 2 * 16)'})
        Agent: Jack, Next move: BeforeActionTakenMessage(ability={"ability_name": "calculator", "description": {"brief_description": "The `calculator` function evaluates a mathematical expression provided as a string and returns the result as a float. It uses the `simplify` function to process the expression and ensure it is correctly computed."}, "parameters_required": ["expr"], "returns": "<class 'float'>"}, arguments={'expr': '(10.01 * 10.36 * 3.33 / 2 * 16)'})
        Agent: Jack, Action taken: AfterActionTakenMessage(ability='calculator', arguments={'expr': '(10.01 * 10.36 * 3.33 / 2 * 16)'}, returns='2762.66390400000', summarization="I used the calculator ability to evaluate the expression '(10.01 * 10.36 * 3.33 / 2 * 16)', and the result is '2762.66390400000', which indicates the computed value of the mathematical expression.")
        Agent: Jack, Next move: BeforeActionTakenMessage(ability={"ability_name": "calculator", "description": {"brief_description": "The `calculator` function evaluates a mathematical expression provided as a string and returns the result as a float. It uses the `simplify` function to process the expression and ensure it is correctly computed."}, "parameters_required": ["expr"], "returns": "<class 'float'>"}, arguments={'expr': '4 * 3.14159 * (2762.66390400000^2)'})
        Agent: Jack, Action taken: AfterActionTakenMessage(ability='calculator', arguments={'expr': '4 * 3.14159 * (2762.66390400000^2)'}, returns='95910378.2949379', summarization="I used the calculator ability to evaluate the expression '4 * 3.14159 * (2762.66390400000^2)', resulting in the value '95910378.2949379'.")
        Agent: Jack, Next move: BeforeActionTakenMessage(ability={"ability_name": "calculator", "description": {"brief_description": "The `calculator` function evaluates a mathematical expression provided as a string and returns the result as a float. It uses the `simplify` function to process the expression and ensure it is correctly computed."}, "parameters_required": ["expr"], "returns": "<class 'float'>"}, arguments={'expr': '(4/3) * 3.14159 * (2762.66390400000^3)'})
        Agent: Jack, Action taken: AfterActionTakenMessage(ability='calculator', arguments={'expr': '(4/3) * 3.14159 * (2762.66390400000^3)'}, returns='88322713378.1367', summarization="I used the calculator ability to evaluate the expression '(4/3) * 3.14159 * (2762.66390400000^3)', and the result is 88322713378.1367, which represents the computed volume of a sphere with a radius of approximately 2762.66.")
        Agent: CEO, Action taken: AfterActionTakenMessage(ability='__AgenticAbility__talk_to_Jack', arguments={'arguments': 'Ask for a favor.'}, returns='{"success": false, "response": "--THOUGHT-PROCESS--  \\n(Initial calculation) [Calculate radius]: I calculated the radius as \'2762.66390400000\' cm. (--SUCCESS--)  \\n(After: Calculate radius) [Calculate surface area]: I calculated the surface area using the formula \'4 * 3.14159 * (2762.66390400000^2)\', resulting in \'95910378.2949379\'. (--SUCCESS--)  \\n(After: Calculate surface area) [Calculate volume]: I calculated the volume using the formula \'(4/3) * 3.14159 * (2762.66390400000^3)\', resulting in \'88322713378.1367\'. (--SUCCESS--)  \\n(After: Calculate volume) [Write results to file]: There is no record in <history> indicating that the results were written to \'result.txt\'. (--FAILED--)  \\n\\nBased on above assessments, here is my conclusion:  \\n--CONCLUSION--  \\nYour request has not been fully achieved. I calculated the radius as \'2762.66390400000\' cm, the surface area as \'95910378.2949379\', and the volume as \'88322713378.1367\', but the results were not written to \'result.txt\'.  \\n--END--"}', summarization="I used the __AgenticAbility__talk_to_Jack ability to ask Jack for a favor. Jack calculated the radius, surface area, and volume of a sphere, but failed to write the results to 'result.txt'.")
        Agent: CEO, Next move: BeforeActionTakenMessage(ability={"ability_name": "__AgenticAbility__talk_to_Tylor", "description": {"brief_description": "Initiates a conversation with \"Tylor\" to use its abilities.", "detailed_description": "First, carefully consider and explore Tylor's potential abilities in solving your tasks, then, if you need Tylor's help, you must tell comprehensively, precisely and exactly what you need Tylor to do.", "self_introduction_from_Tylor": "My name is Tylor. What can I do: I can write content to a file and provide my personal information upon request, but the latter can only be used once.", "hint": "By reading <self_introduction_from_Tylor>, you can learn what Tylor can do, and then decide whether to initiates a conversation with Tylor according to its abilities."}, "parameters_required": [], "returns": "<class 'str'>"}, arguments={'file_name': 'result.txt', 'content': 'Surface Area: 95910378.2949379 cm²\nVolume: 88322713378.1367 cm³'})
        Agent: Tylor, Next move: BeforeActionTakenMessage(ability={"ability_name": "write_file", "description": {"brief_description": "The `write_file` function writes the specified content to a file with the given filename. It opens the file in write mode, encodes the content in UTF-8, and returns a confirmation message indicating that the content has been successfully written to the file."}, "parameters_required": ["filename", "content"], "returns": "<class 'str'>"}, arguments={'filename': 'result.txt', 'content': 'Surface Area: 95910378.2949379 cm²\nVolume: 88322713378.1367 cm³'})
        Agent: Tylor, Action taken: AfterActionTakenMessage(ability='write_file', arguments={'filename': 'result.txt', 'content': 'Surface Area: 95910378.2949379 cm²\nVolume: 88322713378.1367 cm³'}, returns='Surface Area: 95910378.2949379 cm²\nVolume: 88322713378.1367 cm³ written to result.txt.', summarization="I used the write_file ability to write the specified content about surface area and volume to a file named 'result.txt'. The result confirms that the content was successfully written to the file.")
        Agent: CEO, Action taken: AfterActionTakenMessage(ability='__AgenticAbility__talk_to_Tylor', arguments={'arguments': 'Ask for a favor.'}, returns='{"success": true, "response": "--THOUGHT-PROCESS--  \\n(Initial calculation) [Calculate radius]: The radius was calculated as \'2762.66390400000\' cm. (--SUCCESS--)  \\n(After: Calculate radius) [Calculate surface area]: The surface area was calculated using the formula \'4 * 3.14159 * (2762.66390400000^2)\', resulting in \'95910378.2949379\'. (--SUCCESS--)  \\n(After: Calculate surface area) [Calculate volume]: The volume was calculated using the formula \'(4/3) * 3.14159 * (2762.66390400000^3)\', resulting in \'88322713378.1367\'. (--SUCCESS--)  \\n(After: Calculate volume) [Write results to file]: The results were successfully written to \'result.txt\'. (--SUCCESS--)  \\n\\nBased on above assessments, here is my conclusion:  \\n--CONCLUSION--  \\nYour request has been fully achieved. The radius was calculated as \'2762.66390400000\' cm, the surface area as \'95910378.2949379\' cm², and the volume as \'88322713378.1367\' cm³. The results were successfully written to \'result.txt\'.  \\n--END--  "}', summarization="I used the __AgenticAbility__talk_to_Tylor ability to ask Tylor for a favor, which involved calculating the radius, surface area, and volume of a sphere. The results were successfully computed and written to 'result.txt'.")
        Result: AllDoneMessage(success=True, conclusion="Your request has been fully achieved. The radius was calculated as '2762.66390400000' cm, the surface area as '95910378.2949379' cm², and the volume as '88322713378.1367' cm³. The results were successfully written to 'result.txt'.", raw_response="--THOUGHT-PROCESS--  \n(Initial calculation) [Calculate radius]: The radius was calculated as '2762.66390400000' cm. (--SUCCESS--)  \n(After: Calculate radius) [Calculate surface area]: The surface area was calculated using the formula '4 * 3.14159 * (2762.66390400000^2)', resulting in '95910378.2949379' cm². (--SUCCESS--)  \n(After: Calculate surface area) [Calculate volume]: The volume was calculated using the formula '(4/3) * 3.14159 * (2762.66390400000^3)', resulting in '88322713378.1367' cm³. (--SUCCESS--)  \n(After: Calculate volume) [Write results to file]: The results were successfully written to 'result.txt'. (--SUCCESS--)  \n\nBased on above assessments, here is my conclusion:  \n--CONCLUSION--  \nYour request has been fully achieved. The radius was calculated as '2762.66390400000' cm, the surface area as '95910378.2949379' cm², and the volume as '88322713378.1367' cm³. The results were successfully written to 'result.txt'.  \n--END--  ", time_used=123.79718699998921, step_count=2)
        ```
