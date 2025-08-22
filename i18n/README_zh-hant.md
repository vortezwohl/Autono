<div align="center">
    <p>
        <img src="https://github.com/vortezwohl/Autono/releases/download/autono_icon/autono_logo.png" alt="Autono" height="125">
        <div align="center">
            <span>
                <a href="https://deepwiki.com/vortezwohl/Autono" rel="nofollow">
                    <img src="https://camo.githubusercontent.com/e7d4bb1a32530e373bb53fbe8eea825440ad27c7531d8f144d561acdd20c093a/68747470733a2f2f6465657077696b692e636f6d2f62616467652e737667" alt="Ask DeepWiki" data-canonical-src="https://deepwiki.com/badge.svg" style="max-width: 100%;">
                </a>
            </span>
        </div>
    </p>
    <p style="font-weight: 200; font-size: 19px">
        <a href="https://doi.org/10.48550/arXiv.2504.04650" rel="nofollow">
            <img src="https://arxiv.org/static/browse/0.3.4/images/icons/favicon-32x32.png" alt="Paper", style="max-width: 100%;height: 20px">
        </a>
        一個基於 <a href="https://arxiv.org/abs/2210.03629">ReAct</a> 範式的超輕量高穩健智能體框架.
    </p>
</div>

<h4 align="center">
    <p>
        <a href="https://github.com/vortezwohl/Autono/blob/main/README.md">English</a> |
        <b>繁體中文</b> |
        <a href="https://github.com/vortezwohl/Autono/blob/main/i18n/README_zh-hans.md">简体中文</a> |
        <a href="https://github.com/vortezwohl/Autono/blob/main/i18n/README_ja-jp.md">日本語</a>
    </p>
</h4>

<h5></br></h5>

## 安裝

- 從 [PYPI](https://pypi.org/project/autono/)

    ```shell
    pip install -U autono
    ```

- 從 [Github](https://github.com/vortezwohl/Autono/releases)

    先下載 .whl 檔案，然後執行

    ```shell
    pip install git+https://github.com/vortezwohl/Autono.git
    ```

## 引用

如果您正在將 `autono` 框架整合到您的研究中，請務必正確**引用**它，以聲明它對您工作的貢獻.

```bibtex
@article{wu2025autono,
author = {Zihao Wu},
title = {Autono: A ReAct-Based Highly Robust Autonomous Agent Framework},
journal = {arXiv preprint},
year = {2025},
eprint = {2504.04650},
archivePrefix = {arXiv},
primaryClass = {cs.MA},
url = {https://arxiv.org/abs/2504.04650}
}
```
```bibtex
@software{Wu_Autono_2025,
author = {Wu, Zihao},
license = {GPL-3.0},
month = apr,
title = {{Autono}},
url = {https://github.com/vortezwohl/Autono},
version = {1.0.0},
year = {2025}
}
```

## 快速開始

要開始構建您自己的智能體，請按照以下步驟執行。

1. 設置環境變數 `OPENAI_API_KEY`

    ```
    # .env
    OPENAI_API_KEY=sk-...
    ```

2. 從 `autono` 引入 SDKs

    - `Agent` 讓您實例化一個智能體

    - `Personality` 是一個列舉類，用於自訂智能體的個性：

        - `Personality.PRUDENT` 使智能體的行為更謹慎。

        - `Personality.INQUISITIVE` 鼓勵智能體更主動嘗試和探索。

    - `get_openai_model` 給您一個 `BaseChatModel` 作為思考引擎。

    - `@ability(brain: BaseChatModel, cache: bool = True, cache_dir: str = '')` 是一個裝飾器，用來將函數聲明為一個 `Ability`.

    - `@agentic(agent: Agent)` 是一個裝飾器，用來將函數聲明為一個  `AgenticAbility`.

    ```python
    from autono import (
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
    agent = Agent(abilities=[calculator, write_file], brain=model, name='Autono', personality=Personality.INQUISITIVE)
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

> `autono` 也支援多智能體協作場景，可用 `@agentic(agent: Agent)`, 宣告一個函數為智能體呼叫能力，然後賦予給一個智能體。[查看示例](https://github.com/vortezwohl/Autono/blob/main/demo/multi_agent.py)。

## 可觀測性

為了使智能體的執行過程具備可觀測性，我提供了兩個鉤子，分別是 `BeforeActionTaken` 與 `AfterActionTaken`。
它們允許你觀察並介入智能體每一步動作的決策與執行結果。
你可以透過 `BeforeActionTaken` 鉤子獲取並修改智能體對下一步動作的決策結果，
而 `AfterActionTaken` 鉤子則允許你獲取並修改動作的執行結果（被竄改的執行結果會成為智能體記憶的一部分）。

要開始使用鉤子，請按照以下步驟操作。

1. 從 `autono` 中引入鉤子

    ```python
    from autono.brain.hook import BeforeActionTaken, AfterActionTaken
    from autono.message import BeforeActionTakenMessage, AfterActionTakenMessage
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
