# CrewAI - Hermes Plant finance agent

A minimal [CrewAI](https://www.crewai.com/) crew where one analyst agent uses Hermes Plant's DealAnalyzer endpoint to evaluate a deal, then passes the IRR/NPV back to a partner agent who decides whether to proceed.

The point is not this specific scenario. It is the tool-wrapping pattern: a CrewAI `tool` whose `_run` method makes an x402-paid HTTP call, returning structured output the LLM can reason over.

## Setup

```sh
cd crewai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

```sh
export OPENAI_API_KEY="sk-..."          # or another CrewAI-supported LLM provider
export WALLET_PRIVATE_KEY="0x..."       # Base mainnet EOA
```

## Run

```sh
python finance_agent.py
```

## What it shows

- A single CrewAI `Tool` that wraps a Hermes Plant endpoint.
- One paid call per LLM tool invocation. Cost is bounded by the price tier on the endpoint, not by token count.
- Deterministic output the LLM can cite by name, such as "IRR was 18.2% per Hermes DealAnalyzer", instead of asking the LLM to guess the math.

For other Hermes endpoints, such as Black-Scholes Greeks, bond analytics, or AML screening, copy `HermesDealAnalyzerTool` and change the endpoint path plus input schema.
