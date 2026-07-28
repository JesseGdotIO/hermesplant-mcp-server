"""
Direct x402 call to Hermes Plant's CashflowLens endpoint.

The quickstart is fail-closed: it will not spend unless
HERMES_ALLOW_PAYMENT=1, and it refuses any payment above $0.20 USDC.
"""
from __future__ import annotations

import json
import os
from typing import Any

from eth_account import Account
from x402 import max_amount, prefer_network, x402ClientSync
from x402.http.clients import x402_requests
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client


BASE_URL = os.environ.get("HERMES_BASE_URL", "https://hermesplant.com").rstrip("/")
CASHFLOW_LENS_PATH = "/api/agent-services/cashflowlens/analyze"
CASHFLOW_LENS_URL = f"{BASE_URL}{CASHFLOW_LENS_PATH}"
CASHFLOW_LENS_PRICE_ATOMIC_USDC = 200_000
BASE_MAINNET = "eip155:8453"


def _paid_session():
    if os.getenv("HERMES_ALLOW_PAYMENT") != "1":
        raise RuntimeError(
            "Paid calls are disabled. Set HERMES_ALLOW_PAYMENT=1 after "
            "reviewing the fixed $0.20 USDC price."
        )

    account = Account.from_key(os.environ["EVM_PRIVATE_KEY"])
    client = x402ClientSync()
    client.register_policy(prefer_network(BASE_MAINNET))
    client.register_policy(max_amount(CASHFLOW_LENS_PRICE_ATOMIC_USDC))
    register_exact_evm_client(client, EthAccountSigner(account), networks=BASE_MAINNET)
    return x402_requests(client)


def call_cashflow_lens(
    cashflows: list[float],
    discount_rate: float = 0.10,
    periods_per_year: float = 1.0,
) -> tuple[dict[str, Any], str | None]:
    with _paid_session() as session:
        response = session.post(
            CASHFLOW_LENS_URL,
            json={
                "cashflows": cashflows,
                "discountRate": discount_rate,
                "periodsPerYear": periods_per_year,
            },
            timeout=30,
        )
    response.raise_for_status()
    return response.json(), response.headers.get("PAYMENT-RESPONSE")


def main() -> None:
    result, settlement = call_cashflow_lens(
        [-1_000_000, 250_000, 250_000, 300_000, 400_000],
        discount_rate=0.10,
        periods_per_year=1,
    )
    print("CashflowLens result:")
    print(json.dumps(result, indent=2))

    if settlement:
        print("\nSettlement (PAYMENT-RESPONSE header):")
        print(settlement)


if __name__ == "__main__":
    main()
