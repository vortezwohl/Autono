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
        一个基于 <a href="https://arxiv.org/abs/2210.03629">ReAct</a> 范式的超轻量高鲁棒智能体框架.
    </p>
</div>

<h4 align="center">
    <p>
        <a href="https://github.com/vortezwohl/Autono/blob/main/README.md">English</a> |
        <a href="https://github.com/vortezwohl/Autono/blob/main/i18n/README_zh-hant.md">繁體中文</a> |
        <b>简体中文</b> |
         <a href="https://github.com/vortezwohl/Autono/blob/main/i18n/README_ja-jp.md">日本語</a>
    </p>
</h4>

<h5></br></h5>

## 摘要

本文提出了一种基于ReAct范式的高鲁棒性自主智能体框架，旨在通过适应性决策和多智能体协作解决复杂任务。与依赖大型语言模型（LLM）生成固定工作流的传统框架不同，本框架在智能体执行过程中基于先前轨迹动态生成下一步行动，从而增强了其鲁棒性。为了解决由适应性执行路径可能导致的潜在终止问题，本文提出了一种及时放弃策略，该策略结合了概率惩罚机制。在多智能体协作方面，本文引入了一种记忆传递机制，使智能体之间能够共享并动态更新记忆。框架的创新性及时放弃策略通过概率惩罚动态调整任务放弃的概率，使开发者能够通过调整超参数在智能体执行策略的保守性和探索性之间取得平衡，从而显著提高了复杂环境中的适应性和任务执行效率。此外，智能体可以通过外部工具集成进行扩展，这得益于模块化设计和MCP协议的兼容性，从而实现了灵活的动作空间扩展。通过明确的分工，多智能体协作机制使智能体能够专注于特定任务组件，从而显著提高了执行效率和质量。

## 安装

- 从 [PYPI](https://pypi.org/project/autono/)

    ```shell
    pip install -U autono
    ```

- 从 [Github](https://github.com/vortezwohl/Autono/releases)

    先下载 .whl 文件，然后执行

    ```shell
    pip install git+https://github.com/vortezwohl/Autono.git
    ```

## 引用

如果您正在将 `autono` 框架整合到您的研究中，请务必正确**引用**它，以声明它对您工作的贡献.

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

## 快速开始

要开始搭建您自己的智能体，请按照以下步骤执行。

1. 设置环境变量 `DEEPSEEK_API_KEY`

    ```
    # .env
    DEEPSEEK_API_KEY=sk-...
    ```

2. 从 `autono` 引入 SDKs

    - `Agent` 让您实例化一个智能体。

    - `Personality` 是一个枚举类，用于设定智能体的个性：

        - `Personality.PRUDENT` 使智能体的行为更加谨慎。

        - `Personality.INQUISITIVE` 鼓励智能体更主动尝试和探索。

    - `get_deepseek_model` 给您一个 `BaseChatModel` 作为思维引擎。

    - `@ability(brain: BaseChatModel, cache: bool = True, cache_dir: str = '')` 是一个装饰器，用来将函数声明为一个 `Ability`.

    - `@agentic(agent: Agent)` 是一个装饰器，用来将函数声明为一个  `AgenticAbility`.

    ```python
    from autono import (
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
    agent = Agent(abilities=[calculator, write_file], brain=model, name='Autono', personality=Personality.INQUISITIVE)
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

> `autono` 也支持多智能体协作场景，可用 `@agentic(agent: Agent)`, 声明一个函数为智能体呼叫能力，然后赋予给另一个智能体。[查看示例](https://github.com/vortezwohl/Autono/blob/main/demo/multi_agent.py)。

## 可观测性

为了使智能体的执行过程具备可观测性，我提供了两个钩子，分别是 `BeforeActionTaken` 和 `AfterActionTaken`。
它们允许你观察并介入智能体每一步动作的决策与执行结果。
你可以通过 `BeforeActionTaken` 钩子获取并修改智能体对下一步动作的决策结果，
而 `AfterActionTaken` 钩子则允许你获取并修改动作的执行结果（被篡改的执行结果会成为智能体记忆的一部分）。

要开始使用钩子，请按照以下步骤操作。

1. 从 `autono` 中引入钩子

    ```python
    from autono.brain.hook import BeforeActionTaken, AfterActionTaken
    from autono.message import BeforeActionTakenMessage, AfterActionTakenMessage
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
