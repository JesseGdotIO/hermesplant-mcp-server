# Python examples

| File | What it shows |
|---|---|
| [`01-call-endpoint.py`](./01-call-endpoint.py) | Direct x402 call using the official `x402` package. It wraps the 402/sign/retry handshake. |
| [`02-mcp-client.py`](./02-mcp-client.py) | MCP client connecting to `hermesplant.com/mcp`, listing tools, and invoking a free one. |

## Setup

```sh
cd python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

```sh
export WALLET_PRIVATE_KEY="0x..."   # EOA private key, Base mainnet
```

## Run

```sh
python 01-call-endpoint.py
python 02-mcp-client.py
```
