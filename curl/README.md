# curl / Bash examples

Both scripts are read-only and run with stock `bash`, `curl`, and `jq`.

| Script | What it shows |
|---|---|
| [`01-discover.sh`](./01-discover.sh) | Fetches Hermes Plant discovery surfaces and prints key fields. |
| [`02-call-endpoint.sh`](./02-call-endpoint.sh) | Posts to CashflowLens without credentials, decodes the 402 challenge, and verifies Base plus the $0.20 cap. |

## Run

```sh
bash curl/01-discover.sh
bash curl/02-call-endpoint.sh
```

The shell example intentionally does not implement wallet signing. Hand-rolling
EIP-712 selection and signing around `curl` is easy to make unsafe, especially
when a challenge exposes multiple networks or prices. Use the guarded Python or
TypeScript quickstart for a paid call.
