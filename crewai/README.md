# CrewAI - Hermes Plant finance agent

A CrewAI example in which an analyst uses Hermes Plant's deterministic
CashflowLens endpoint, then hands the result to a managing-partner agent.

## Safety contract

- The endpoint price is fixed at **$0.20 USDC per successful call** on Base mainnet.
- The adapter refuses payments above 200,000 atomic USDC.
- Calls fail closed unless `HERMES_ALLOW_PAYMENT=1`.
- The private key is read only from `EVM_PRIVATE_KEY`; never commit it.
- A Crew may invoke a tool more than once. Set CrewAI iteration limits appropriate
  to your total spend tolerance; the per-call cap is not a total-run budget.

## Setup

```sh
cd crewai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On PowerShell, activate with `.venv\Scripts\Activate.ps1`.

Configure your CrewAI-supported LLM provider, then enable the paid tool explicitly:

```sh
export OPENAI_API_KEY="..."
export EVM_PRIVATE_KEY="0x..."
export HERMES_ALLOW_PAYMENT="1"
```

Fund the wallet with enough USDC on Base and a small amount of ETH for gas. Leave
`HERMES_ALLOW_PAYMENT` unset during import and planning tests.

## Run

```sh
python finance_agent.py
```

The tool posts the live-verified CashflowLens request shape to
`/api/agent-services/cashflowlens/analyze`. Copy the adapter pattern only after
checking the target endpoint's current schema and price. The former
`HermesDealAnalyzerTool` import remains as a compatibility alias.
