# LangChain - Hermes Plant tool

A LangChain `BaseTool` for Hermes Plant's deterministic CashflowLens x402 endpoint.

## Safety contract

- The endpoint price is fixed at **$0.20 USDC per successful call** on Base mainnet.
- The adapter refuses payments above 200,000 atomic USDC.
- Calls fail closed unless `HERMES_ALLOW_PAYMENT=1`.
- The private key is read only from `EVM_PRIVATE_KEY`; never commit it.

## Setup

```sh
cd langchain
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On PowerShell, activate with `.venv\Scripts\Activate.ps1`.

```sh
export EVM_PRIVATE_KEY="0x..."
export HERMES_ALLOW_PAYMENT="1"
```

Fund the wallet with enough USDC on Base and a small amount of ETH for gas. Leave
`HERMES_ALLOW_PAYMENT` unset while testing imports or agent planning.

## Run

```sh
python hermes_tool.py
```

## Use in an agent

```python
from hermes_tool import HermesCashflowLens

tools = [HermesCashflowLens()]
```

Pass `tools` to the LangChain or LangGraph agent constructor you already use. The
tool posts the live-verified request shape to
`/api/agent-services/cashflowlens/analyze` and returns the structured JSON
response. Its async path moves the synchronous x402 request off the event loop.
The former `HermesDealAnalyzer` import remains as a compatibility alias.
