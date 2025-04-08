<div align="center">
    <p>
        <img src="https://github.com/vortezwohl/Autono/releases/download/autono_icon/autono_logo.png" alt="Autono" height="125">
    </p>
    <p style="font-weight: 200; font-size: 19px">
        基于 <a href="https://arxiv.org/abs/2210.03629">ReAct</a> パラダイムの非常に強靭な自律型エージェントAIフレームワーク.
    </p>
</div>

<h4 align="center">
    <p>
        <a href="https://github.com/vortezwohl/Autono/blob/main/README.md">English</a> |
        <a href="https://github.com/vortezwohl/Autono/blob/main/i18n/README_zh-hant.md">繁體中文</a> |
        <a href="https://github.com/vortezwohl/Autono/blob/main/i18n/README_zh-hans.md">简体中文</a> |
        <b>日本語</b>
    </p>
</h4>

<h5></br></h5>

## インストール

- [PYPI](https://pypi.org/project/autono/)から

    ```shell
    pip install -U autono
    ```

- [Github](https://github.com/vortezwohl/Autono/releases)から

    ```shell
    pip install git+https://github.com/vortezwohl/Autono.git
    ```

## 引用

`autono`フレームワークを研究に組み込む場合は、その貢献を認めるために適切に**引用**することを忘れないでください.

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

## クイックスタート

独自のエージェントを構築するには、以下の手順に従ってください。

1. 環境変数`OPENAI_API_KEY`を設定

    ```
    # .env
    OPENAI_API_KEY=sk-...
    ```

2. `autono`からSDKを導入

    - `Agent`はエージェントをインスタンス化します。

    - `Personality`はエージェントの個性をカスタマイズするための列挙クラスです。

        - `Personality.PRUDENT`はエージェントの行動をより慎重にします。

        - `Personality.INQUISITIVE`はエージェントがより積極的に試行錯誤し、探索することを奨励します。

    - `get_openai_model`は思考エンジンとして`BaseChatModel`を提供します。

    - `@ability(brain: BaseChatModel, cache: bool = True, cache_dir: str = '')`は関数を`Ability`として宣言するためのデコレータです。

    - `@agentic(agent: Agent)`は関数を`AgenticAbility`として宣言するためのデコレータです。

    ```python
    from autono import (
        Agent,
        Personality,
        get_openai_model,
        ability,
        agentic
    )
    ```

3. 基本的な能力として関数を宣言

    ```python
    @ability
    def calculator(expr: str) -> float:
        # この関数は単一の数学式のみを受け付けます
        return simplify(expr)

    @ability
    def write_file(filename: str, content: str) -> str:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f'{content}が{filename}に書き込まれました。'
    ```

4. エージェントをインスタンス化

    エージェントに能力を付与しながらインスタンス化できます。

    ```python
    model = get_openai_model()
    agent = Agent(abilities=[calculator, write_file], brain=model, name='autono', personality=Personality.INQUISITIVE)
    ```

    - 後でエージェントにさらに能力を付与することもできます：

        ```python
        agent.grant_ability(calculator)
        ```

        または

        ```python
        agent.grant_abilities([calculator])
        ```

    - 能力を剥奪するには：

        ```python
        agent.deprive_ability(calculator)
        ```

        または

        ```python
        agent.deprive_abilities([calculator])
        ```
    
    メソッド`change_personality(personality: Personality)`を使用してエージェントの個性を変更できます。

    ```python
    agent.change_personality(Personality.PRUDENT)
    ```

5. エージェントにリクエストを割り当てる

    ```python
    agent.assign("Here is a sphere with radius of 9.5 cm and pi here is 3.14159, find the area and volume respectively then write the results into a file called 'result.txt'.")
    ```

6. 残りの作業をエージェントに任せる

    ```python
    response = agent.just_do_it()
    print(response)
    ```

> `autono`はマルチエージェント協力シナリオもサポートしています。`@agentic(agent: Agent)`を使用して関数をエージェント呼び出し能力として宣言し、それをエージェントに付与します。[例を参照](https://github.com/vortezwohl/Autono/blob/main/demo/multi_agent.py).

## 観測可能性

エージェントの作業プロセスを観測可能にするために、`BeforeActionTaken`と`AfterActionTaken`という2つのフックを提供します。 
これらは、エージェントの各ステップのアクションの意思決定と実行結果を観察し、介入することを可能にします。 
`BeforeActionTaken`フックを使用して、エージェントの次のアクションの意思決定結果を取得および変更でき、 
`AfterActionTaken`フックを使用して、アクションの実行結果を取得および変更できます（改ざんされた実行結果はエージェントの記憶の一部になります）。

フックの使用を開始するには、以下の手順に従ってください。

1. `autono`からフックとメッセージを導入

    ```python
    from autono.brain.hook import BeforeActionTaken, AfterActionTaken
    from autono.message import BeforeActionTakenMessage, AfterActionTakenMessage
    ```

2. 関数を宣言し、それらをフックとしてカプセル化

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

    > これらの2つのフック関数では、メッセージをインターセプトし、メッセージ内の情報を印刷しました。 
    その後、メッセージを変更せずにエージェントに返しました。 
    もちろん、メッセージ内の情報を**変更**するオプションもあり、 
    これによりエージェントの作業プロセスに介入することができます。

3. エージェントの作業プロセス中にフックを使用

    ```python
    agent.assign(...).just_do_it(before_action_taken_hook, after_action_taken_hook)
    ```
