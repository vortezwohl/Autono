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


## 範例

- ### 複合任務

    1. 計算一個球體的表面積和體積，並將結果寫入一個文檔。

        ```python
        import logging

        from ceo import (
            Agent,
            Personality,
            get_openai_model,
            ability
        )
        from sympy import simplify
        from dotenv import load_dotenv

        load_dotenv()
        logging.getLogger('ceo').setLevel(logging.DEBUG)


        @ability
        def calculator(expr: str) -> float:
            # this function only accepts a single math expression
            return simplify(expr)


        @ability
        def write_file(filename: str, content: str) -> str:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            return f'{content} written to {filename}.'


        if __name__ == '__main__':
            ceo = Agent(abilities=[calculator, write_file], brain=get_openai_model(), name='CEO', personality=Personality.INQUISITIVE)
            radius = '(10.01 * 10.36 * 3.33 / 2 * 16)'  # 2762.663904
            pi = 3.14159
            output_file = 'result.txt'
            request = f"Here is a sphere with radius of {radius} cm and pi here is {pi}, find the area and volume respectively then write the results into a file called '{output_file}'."
            result = ceo.assign(request).just_do_it()  # area = 95910378.2949379, volume = 88322713378.13666
            print(result)
        ```

        ```
        # result.txt
        Surface Area: 95910378.29 cm², Volume: 88322713378.14 cm³
        ```

        ```
        # stdout
        [DEBUG] 2025-01-12 01:33:50,780 ceo : Agent: CEO; Expected steps: 4; Request: "Here is a sphere with radius of (10.01 * 10.36 * 3.33 / 2 * 16) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.";
        [DEBUG] 2025-01-12 01:34:05,491 ceo : Agent: CEO; Memory size: 1; Memory update: I used the calculator ability to evaluate the mathematical expression '(10.01 * 10.36 * 3.33 / 2 * 16)', and the result is 2762.66390400000, which indicates the computed value of the expression.;
        [DEBUG] 2025-01-12 01:34:12,953 ceo : Agent: CEO; Memory size: 2; Memory update: I used the calculator ability to evaluate the expression '4 * 3.14159 * (2762.66390400000^2)', and the result is 95910378.2949379, which represents the calculated value of the mathematical expression.;
        [DEBUG] 2025-01-12 01:34:22,476 ceo : Agent: CEO; Memory size: 3; Memory update: I used the calculator ability to evaluate the expression '(4/3) * 3.14159 * (2762.66390400000^3)', and the result shows '88322713378.1367', which indicates the computed volume of a sphere with the given radius.;
        [DEBUG] 2025-01-12 01:34:34,233 ceo : Agent: CEO; Memory size: 4; Memory update: I used the write_file ability to create or overwrite a file named 'result.txt' with the specified content detailing the surface area and volume. The result confirms that the content was successfully written to the file.;
        [DEBUG] 2025-01-12 01:34:47,573 ceo : Agent: CEO; Conclusion: Your request has been fully achieved. The calculations for the surface area and volume were performed correctly, and the results were successfully written to the file 'result.txt'.;
        [DEBUG] 2025-01-12 01:34:47,573 ceo : Agent: CEO; Step count: 4; Time used: 59.79923509992659 seconds;
        {'success': True, 'conclusion': "Your request has been fully achieved. The calculations for the surface area and volume were performed correctly, and the results were successfully written to the file 'result.txt'.", 'raw_response': "--THOUGHT-PROCESS--  \n(Initial calculation) [Calculate radius]: The radius was calculated as (10.01 * 10.36 * 3.33 / 2 * 16) resulting in 2762.66390400000 cm. (--SUCCESS--)  \n(After: Calculate radius) [Calculate surface area]: The surface area was calculated using the formula '4 * π * r²', yielding 95910378.2949379 cm². (--SUCCESS--)  \n(After: Calculate surface area) [Calculate volume]: The volume was calculated using the formula '(4/3) * π * r³', resulting in 88322713378.1367 cm³. (--SUCCESS--)  \n(After: Calculate volume) [Write results to file]: The results were successfully written to 'result.txt' with the correct surface area and volume. (--SUCCESS--)  \n\nBased on above assessments, here is my conclusion:  \n--CONCLUSION--  \nYour request has been fully achieved. The calculations for the surface area and volume were performed correctly, and the results were successfully written to the file 'result.txt'.  \n--END--", 'misc': {'time_used': 59.79923509992659, 'step_count': 4}}
        ```

- ### 多智能體協作
    
    1. 請合適的智能體計算球體的表面積和體積，並將結果寫入一個文檔中。
  
        ```python
        import logging

        from sympy import simplify
        from dotenv import load_dotenv
        from ceo import (
            Agent,
            Personality,
            get_openai_model,
            agentic,
            ability
        )

        load_dotenv()
        logging.getLogger('ceo').setLevel(logging.DEBUG)
        model = get_openai_model()


        @ability
        def calculator(expr: str) -> float:
            # this function only accepts a single math expression
            return simplify(expr)


        @ability
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


        if __name__ == '__main__':
            ceo = Agent(abilities=[agent1, agent2], brain=model, name='CEO', personality=Personality.INQUISITIVE)
            radius = '(10.01 * 10.36 * 3.33 / 2 * 16)'  # 2762.663904
            pi = 3.14159
            output_file = 'result.txt'
            request = f"Here is a sphere with radius of {radius} cm and pi here is {pi}, find the area and volume respectively then write the results into a file called '{output_file}'."
            result = ceo.assign(request).just_do_it()  # area = 95910378.2949379, volume = 88322713378.13666
            print(result)
        ```

        > 在多智能體協作的情境下，您可以為每個不同的智能體分配不同的個性。例如，在上述腳本中，Jack 的能力是進行計算。我希望他能多嘗試和探索，所以將 Jack 的個性設置為 `Personality.INQUISITIVE`。另一方面，Taylor 的能力是創建和寫入文檔。對於涉及與外部文檔系統交互的操作，我希望他能夠更加謹慎，所以將 Taylor 的個性設置為 `Personality.PRUDENT`。

        ```
        # result.txt
        Surface Area: 95910378.2949379 cm²
        Volume: 88322713378.1367 cm³
        ```

        ```
        # stdout
        [DEBUG] 2025-01-12 01:41:36,139 ceo : Agent: CEO; Expected steps: 4; Request: "Here is a sphere with radius of (10.01 * 10.36 * 3.33 / 2 * 16) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.";
        [DEBUG] 2025-01-12 01:41:41,870 ceo : Agent: Jack; Memory brought in: 0;
        [DEBUG] 2025-01-12 01:41:45,642 ceo : Agent: Jack; Expected steps: 3; Request: "Here is a sphere with radius of (10.01 * 10.36 * 3.33 / 2 * 16) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.";
        [DEBUG] 2025-01-12 01:41:52,758 ceo : Agent: Jack; Memory size: 1; Memory update: I used the calculator ability to evaluate the expression '(10.01 * 10.36 * 3.33 / 2 * 16)', and the result is '2762.66390400000', which indicates the computed value of the mathematical expression.;
        [DEBUG] 2025-01-12 01:42:03,734 ceo : Agent: Jack; Memory size: 2; Memory update: I used the calculator ability to evaluate the expression '4 * 3.14159 * (2762.66390400000^2)', and the result shows '95910378.2949379', which indicates the computed value of the mathematical expression.;
        [DEBUG] 2025-01-12 01:42:10,908 ceo : Agent: Jack; Memory size: 3; Memory update: I used the calculator ability to evaluate the expression '(4/3) * 3.14159 * (2762.66390400000^3)', and the result shows '88322713378.1367', which indicates the computed volume of a sphere with a radius of approximately 2762.66.;
        [DEBUG] 2025-01-12 01:42:22,210 ceo : Agent: Jack; Conclusion: Your request has not been fully achieved. I successfully calculated the radius, surface area, and volume of the sphere, but there is no record of writing these results into the file 'result.txt'.;
        [DEBUG] 2025-01-12 01:42:22,210 ceo : Agent: Jack; Step count: 3; Time used: 40.33986619999632 seconds;
        [DEBUG] 2025-01-12 01:42:29,049 ceo : Agent: CEO; Memory size: 1; Memory update: I used the __AgenticAbility__talk_to_Jack ability to ask Jack for a favor. Jack successfully calculated the radius, surface area, and volume of a sphere based on the given expression, but failed to write the results to 'result.txt', resulting in an incomplete request.;
        [DEBUG] 2025-01-12 01:42:44,713 ceo : Agent: Tylor; Memory brought in: 1;
        [DEBUG] 2025-01-12 01:42:47,498 ceo : Agent: Tylor; Expected steps: 1; Request: "Here is a sphere with radius of (10.01 * 10.36 * 3.33 / 2 * 16) cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.";
        [DEBUG] 2025-01-12 01:42:56,955 ceo : Agent: Tylor; Memory size: 2; Memory update: I used the write_file ability to write the specified content about surface area and volume to a file named 'result.txt'. The result confirms that the content was successfully written to the file.;
        [DEBUG] 2025-01-12 01:43:06,851 ceo : Agent: Tylor; Conclusion: Your request has been fully achieved. The surface area and volume of the sphere were calculated successfully, and the results were written to 'result.txt'.  
        Results:  
        Surface Area: 95910378.2949379 cm²  
        Volume: 88322713378.1367 cm³;
        [DEBUG] 2025-01-12 01:43:06,851 ceo : Agent: Tylor; Step count: 1; Time used: 22.138400600058958 seconds;
        [DEBUG] 2025-01-12 01:43:12,070 ceo : Agent: CEO; Memory size: 2; Memory update: I used the __AgenticAbility__talk_to_Tylor ability to ask Tylor for a favor, which involved calculating the surface area and volume of a sphere based on given dimensions. The result indicates success, confirming that the calculations were performed accurately and the results were saved to 'result.txt'.;
        [DEBUG] 2025-01-12 01:43:20,457 ceo : Agent: CEO; Conclusion: Your request has been fully achieved. The surface area and volume of the sphere were calculated successfully, and the results were written to 'result.txt'.  
        Results:  
        Surface Area: 95910378.2949379 cm²  
        Volume: 88322713378.1367 cm³;
        [DEBUG] 2025-01-12 01:43:20,457 ceo : Agent: CEO; Step count: 2; Time used: 108.47770960000344 seconds;
        {'success': True, 'conclusion': "Your request has been fully achieved. The surface area and volume of the sphere were calculated successfully, and the results were written to 'result.txt'.  \nResults:  \nSurface Area: 95910378.2949379 cm²  \nVolume: 88322713378.1367 cm³", 'raw_response': "--THOUGHT-PROCESS--  \n(Initial calculation) [Calculating radius]: I evaluated the expression '(10.01 * 10.36 * 3.33 / 2 * 16)' and obtained '2762.66390400000'. (--SUCCESS--)  \n(Area calculation) [Calculating surface area]: I evaluated the expression '4 * 3.14159 * (2762.66390400000^2)' and obtained '95910378.2949379'. (--SUCCESS--)  \n(Volume calculation) [Calculating volume]: I evaluated the expression '(4/3) * 3.14159 * (2762.66390400000^3)' and obtained '88322713378.1367'. (--SUCCESS--)  \n(Write results) [Writing to file]: Tylor successfully wrote the results to 'result.txt'. (--SUCCESS--)  \n\nBased on above assessments, here is my conclusion:  \n--CONCLUSION--  \nYour request has been fully achieved. The surface area and volume of the sphere were calculated successfully, and the results were written to 'result.txt'.  \nResults:  \nSurface Area: 95910378.2949379 cm²  \nVolume: 88322713378.1367 cm³  \n--END--  ", 'misc': {'time_used': 108.47770960000344, 'step_count': 2}}
        ```
