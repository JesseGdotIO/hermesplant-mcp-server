# LangChain - Hermes Plant tool

A LangChain `BaseTool` that wraps a Hermes Plant x402-paid endpoint. Drop into any LangChain or LangGraph agent.

## Setup

```sh
cd langchain
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

```sh
export OPENAI_API_KEY="sk-..."          # or another LangChain-supported LLM
export WALLET_PRIVATE_KEY="0x..."       # Base mainnet EOA
```

## Run

```sh
python hermes_tool.py
```

## Use in your own agent

```python
from hermes_tool import HermesDealAnalyzer
from langchain.agents import create_react_agent
from langchain_openai import ChatOpenAI

tools = [HermesDealAnalyzer()]
llm = ChatOpenAI(model="gpt-4o-mini")
agent = create_react_agent(llm, tools)
```

The tool description is intentionally specific so the LLM picks it for cashflow-IRR-NPV questions and does not try to invent the math itself. Copy the pattern for other Hermes endpoints (`/agent-services/options`, `/agent-services/walletguard`, etc.): same shape, different schema.
