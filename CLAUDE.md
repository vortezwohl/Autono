# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Autono is a ReAct-based highly robust autonomous agent framework designed for complex task solving through adaptive decision making and multi-agent collaboration. The framework dynamically generates next actions during agent execution based on prior trajectories, enhancing robustness with a timely abandonment strategy incorporating probabilistic penalty mechanisms.

## Architecture

### Core Components

1. **Agents** (`autono/brain/`):
   - `Agent`: Main agent class with personality traits (PRUDENT/INQUISITIVE)
   - `BaseAgent`: Base class providing core agent functionality
   - `McpAgent`: Agent supporting MCP (Model Context Protocol) tool calls
   - `MemoryAugment`: Memory management for agent state persistence

2. **Abilities** (`autono/ability/`):
   - `Ability`: Regular function abilities decorated with `@ability`
   - `AgenticAbility`: Abilities that can call other agents (multi-agent collaboration)
   - `McpAbility`: MCP-based tool abilities
   - `McpAgenticAbility`: MCP-based agentic abilities

3. **Language Models** (`autono/brain/lm/`):
   - `openai.py`: OpenAI model integration
   - `dashscope.py`: Alibaba DashScope model integration
   - `deepseek.py`: DeepSeek model integration
   - All return `BaseChatModel` instances for consistent interface

4. **Prompt System** (`autono/prompt/`):
   - Modular prompt templates for different agent operations
   - `NextMovePrompt`: Determines next action based on memory
   - `ExecutorPrompt`: Executes selected abilities
   - `IntrospectionPrompt`: Agent self-reflection
   - `RequestResolverPrompt`: Parses and breaks down user requests

5. **Hooks** (`autono/brain/hook/`):
   - `BeforeActionTaken`: Intercept agent decisions before execution
   - `AfterActionTaken`: Intercept and modify execution results
   - Enables observability and intervention in agent workflow

### Key Design Patterns

- **ReAct Paradigm**: Thought-Action-Observation loop with memory
- **Probabilistic Abandonment**: Dynamic task abandonment based on personality parameters
- **Memory Transfer**: Shared memory between agents in multi-agent scenarios
- **Decorator-based Abilities**: `@ability` and `@agentic` decorators for easy ability creation
- **MCP Integration**: First-class support for Model Context Protocol tools

## Development Setup

### Environment
- Python >= 3.10 required
- Uses `uv` for package management (see `pyproject.toml` and `uv.lock`)
- Virtual environment in `.venv/`
- Environment variables in `.env`:
  - `OPENAI_API_KEY`, `DASHSCOPE_API_KEY`, `DEEPSEEK_API_KEY`
  - `HF_API_TOKEN`, `HF_ENDPOINT` (optional)

### Installation
```bash
# Install with uv (recommended)
uv sync

# Or install from PyPI
pip install autono

# Or install from GitHub for unreleased features
pip install git+https://github.com/vortezwohl/Autono.git
```

### Common Development Tasks

**Run demo examples:**
```bash
cd demo
python single_agent.py
python multi_agent.py
python mcp_agent.py
```

**Test MCP integration:**
```bash
cd demo/mcp_server
python playwright-plus-python-mcp.py
```

**Build and publish:**
```bash
# Build package
uv build

# Publish to PyPI
uv publish
```

## API Usage Patterns

### Basic Agent Creation
```python
from autono import Agent, Personality, get_openai_model, ability

@ability
def calculator(expr: str) -> float:
    return eval(expr)

agent = Agent(
    abilities=[calculator],
    brain=get_openai_model(),
    name='Autono',
    personality=Personality.INQUISITIVE
)
```

### Multi-Agent Collaboration
```python
from autono import agentic

@agentic(other_agent)
def delegate_task(request: str) -> str:
    """Delegate task to another agent"""
    return other_agent.assign(request).just_do_it()
```

### MCP Agent Usage
```python
from autono import McpAgent, StdioMcpConfig, mcp_session, sync_call

@sync_call
@mcp_session(StdioMcpConfig(command='python', args=['./server.py']))
async def run(session, request: str):
    mcp_agent = await McpAgent(session=session, brain=get_openai_model()).fetch_abilities()
    return await mcp_agent.assign(request).just_do_it()
```

### Hooks for Observability
```python
from autono.brain.hook import BeforeActionTaken, AfterActionTaken

def before_hook(agent, message):
    print(f"Next action: {message}")
    return message

agent.assign(task).just_do_it(BeforeActionTaken(before_hook))
```

## Code Organization

- `autono/`: Main package
  - `brain/`: Core agent logic and models
  - `ability/`: Ability definitions and decorators
  - `prompt/`: LLM prompt templates
  - `message/`: Message classes for agent communication
  - `enum/`: Enumerations (Personality)
  - `exception/`: Custom exceptions
  - `util/`: Utility functions and decorators
- `demo/`: Example scripts
  - `single_agent.py`: Basic agent usage
  - `multi_agent.py`: Multi-agent collaboration
  - `mcp_agent.py`: MCP integration example
  - `mcp_server/`: Example MCP server
- `i18n/`: Internationalized README files

## Key Files to Understand

1. `autono/brain/agent.py`: Main Agent class with personality-based decision making
2. `autono/brain/base_agent.py`: Base agent functionality
3. `autono/util/ability.py`: `@ability` decorator implementation
4. `autono/util/agentic.py`: `@agentic` decorator for multi-agent
5. `autono/prompt/next_move_prompt.py`: Core ReAct decision logic
6. `autono/brain/memory_augment.py`: Memory management system

## Testing

- No formal test suite in repository
- Demo scripts serve as functional examples
- Run demo scripts to verify functionality
- Check agent outputs in `demo/result.txt` after running examples

## Notes for Contributors

- Follow existing decorator patterns for new abilities
- Maintain personality parameter consistency (PRUDENT_P=0.25, INQUISITIVE_P=0.05)
- Use `BaseChatModel` from langchain for LLM integration
- Preserve memory transfer mechanism for multi-agent scenarios
- Document new abilities with clear docstrings (auto-generated by `@ability`)
- Update demo scripts when adding new features