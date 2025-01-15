<div align="center">
    <p>
        <img src="https://github.com/vortezwohl/CEO/releases/download/icon/ceo-icon-inv.png" alt="CEO" height="105">
    </p>
    <p style="font-weight: 200; font-size: 19px">
        一個基於 <a href="https://arxiv.org/abs/2210.03629">ReAct</a> 範式的超輕量智能體框架.
    </p>
</div>

<h4 align="center">
    <p>
        <a href="https://github.com/vortezwohl/CEO-Agentic-AI-Framework/blob/main/README.md">English</a> |
        <b>繁體中文</b> |
        <a href="https://github.com/vortezwohl/CEO-Agentic-AI-Framework/blob/main/i18n/README_zh-hans.md">简体中文</a>
    </p>
</h4>

<h5></br></h5>

## 安裝

- 從 [PYPI](https://pypi.org/project/ceo-py/)

    ```shell
    pip install ceo-py
    ```

- 從 [Github](https://github.com/vortezwohl/CEO/releases)

    先下載 .whl 檔案，然後執行

    ```shell
    pip install ./ceo_py-x.x.x-py3-none-any.whl
    ```

## 引用

如果您正在將 `CEO` 框架整合到您的研究中，請務必正確**引用**它，以聲明它對您工作的貢獻.

```latex
@software {CEO,
author = {Zihao Wu},
title = {CEO: An ultra-lightweight agentic AI framework based on the ReAct paradigm},
publisher = {Github},
howpublished = {\url{https://github.com/vortezwohl/CEO-Agentic-AI-Framework}},
year = {2024},
date = {2024-10-25}
}
```

## 快速開始

要開始構建您自己的智能體，請按照以下步驟執行。

1. 設置環境變數 `OPENAI_API_KEY`

    ```
    # .env
    OPENAI_API_KEY=sk-...
    ```

2. 從 `CEO` 引入 SDKs

    - `Agent` 讓您實例化一個智能體

    - `Personality` 是一個列舉類，用於自訂智能體的個性：

        - `Personality.PRUDENT` 使智能體的行為更謹慎。

        - `Personality.INQUISITIVE` 鼓勵智能體更主動嘗試和探索。

    - `get_openai_model` 給您一個 `BaseChatModel` 作為思考引擎。

    - `@ability(brain: BaseChatModel, cache: bool = True, cache_dir: str = '')` 是一個裝飾器，用來將函數聲明為一個 `Ability`.

    - `@agentic(agent: Agent)` 是一個裝飾器，用來將函數聲明為一個  `AgenticAbility`.

    ```python
    from ceo import (
        Agent,
        Personality,
        get_openai_model,
        ability,
        agentic
    )
    ```

3. 聲明函數作為基本能力

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

4. 實例化一個智能体

    您可以在實例化智能體時賦予能力。

    ```python
    model = get_openai_model()
    agent = Agent(abilities=[calculator, write_file], brain=model, name='CEO', personality=Personality.INQUISITIVE)
    ```

    - 您也可以稍後賦予更多能力給智能體：

        ```python
        agent.grant_ability(calculator)
        ```

        或

        ```python
        agent.grant_abilities([calculator])
        ```

    - 剝奪能力：

        ```python
        agent.deprive_ability(calculator)
        ```

        或

        ```python
        agent.deprive_abilities([calculator])
        ```
    
    您可以使用方法 `change_personality(personality: Personality)` 更改智能體的個性。

    ```python
    agent.change_personality(Personality.PRUDENT)
    ```

5. 指定请求給您的智能體

    ```python
    agent.assign("Here is a sphere with radius of (1 * 9.5 / 2 * 2) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
    ```

6. 將其餘工作交給您的智能體

    ```python
    response = agent.just_do_it()
    print(response)
    ```

> `ceo` 也支援多智能體協作場景，可用 `@agentic(agent: Agent)`, 宣告一個函數為智能體呼叫能力，然後賦予給一個智能體。[查看示例](#多智能體協作)。

## 可觀測性

為了使智能體的執行過程具備可觀測性，我提供了兩個鉤子，分別是 `BeforeActionTaken` 與 `AfterActionTaken`。
它們允許你觀察並介入智能體每一步動作的決策與執行結果。
你可以透過 `BeforeActionTaken` 鉤子獲取並修改智能體對下一步動作的決策結果，
而 `AfterActionTaken` 鉤子則允許你獲取並修改動作的執行結果（被竄改的執行結果會成為智能體記憶的一部分）。

要開始使用鉤子，請按照以下步驟操作。

1. 從 `CEO` 中引入鉤子

    ```python
    from ceo.brain.hook import BeforeActionTaken, AfterActionTaken
    from ceo.message import BeforeActionTakenMessage, AfterActionTakenMessage
    ```

2. 聲明函數，並將函數封裝為鉤子

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

    > 在這兩個鉤子函數中，你攔截了訊息並列印了訊息中的資訊。之後，你將訊息原封不動地回傳給智能體。當然，你也可以選擇**修改**訊息中的資訊，從而實現對智能體執行過程的干預。

3. 在智能體的工作過程中使用鉤子

    ```python
    agent.assign(...).just_do_it(before_action_taken_hook, after_action_taken_hook)
    ```

## 範例

- ### 複合任務

    1. 計算一個球體的表面積和體積，並將結果寫入一個文檔。

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

- ### 多智能體協作
    
    1. 請合適的智能體計算球體的表面積和體積，並將結果寫入一個文檔中。
  
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

        > 在多智能體協作的情境下，您可以為每個不同的智能體分配不同的個性。例如，在上述腳本中，Jack 的能力是進行計算。我希望他能多嘗試和探索，所以將 Jack 的個性設置為 `Personality.INQUISITIVE`。另一方面，Taylor 的能力是創建和寫入文檔。對於涉及與外部文檔系統交互的操作，我希望他能夠更加謹慎，所以將 Taylor 的個性設置為 `Personality.PRUDENT`。

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
