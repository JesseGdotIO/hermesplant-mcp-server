# Python examples

| File | What it shows |
|---|---|
| [`01-call-endpoint.py`](./01-call-endpoint.py) | A fail-closed x402 2.x call to the $0.20 CashflowLens endpoint. |
| [`02-mcp-client.py`](./02-mcp-client.py) | An MCP client listing tools and invoking a free tool. |

## Setup

```sh
cd python
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Paid-call safety

The paid quickstart is restricted to Base mainnet and refuses payment requirements
above 200,000 atomic USDC. It will not spend until explicitly enabled:

```sh
export EVM_PRIVATE_KEY="0x..."
export HERMES_ALLOW_PAYMENT="1"
```

Fund the wallet with enough USDC on Base and a small amount of ETH for gas. Never
commit the private key. Leave `HERMES_ALLOW_PAYMENT` unset for import and CI
checks.

## Run

```sh
python 01-call-endpoint.py
python 02-mcp-client.py
```
