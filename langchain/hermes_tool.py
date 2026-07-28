"""
LangChain BaseTool wrapping Hermes Plant's CashflowLens x402 endpoint.

The adapter is fail-closed: it will not spend unless HERMES_ALLOW_PAYMENT=1,
and it refuses any payment above the endpoint's fixed $0.20 USDC price.
"""
from __future__ import annotations

import asyncio
import os
from typing import Any

from eth_account import Account
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from x402 import max_amount, prefer_network, x402ClientSync
from x402.http.clients import x402_requests
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client


CASHFLOW_LENS_URL = "https://hermesplant.com/api/agent-services/cashflowlens/analyze"
CASHFLOW_LENS_PRICE_ATOMIC_USDC = 200_000
BASE_MAINNET = "eip155:8453"


class CashflowLensInput(BaseModel):
    cashflows: list[float] = Field(
        description="Cashflows by period. Index 0 is the initial outlay (typically negative).",
    )
    discount_rate: float = Field(
        default=0.10,
        description="Annual discount rate as a decimal (e.g. 0.10 for 10%).",
    )
    periods_per_year: float = Field(
        default=1.0,
        gt=0,
        description="Periods per year for annualized IRR (12 monthly, 4 quarterly, 1 yearly).",
    )


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


class HermesCashflowLens(BaseTool):
    name: str = "hermes_cashflow_lens"
    description: str = (
        "Compute deterministic periodic IRR and NPV from a cashflow series. "
        "Use this tool whenever the user asks for an IRR, NPV, or cashflow "
        "return calculation. Never invent the math; the API is authoritative. "
        "Settles a fixed $0.20 USDC payment on Base mainnet."
    )
    args_schema: type[BaseModel] = CashflowLensInput

    def _run(
        self,
        cashflows: list[float],
        discount_rate: float = 0.10,
        periods_per_year: float = 1.0,
    ) -> dict[str, Any]:
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
        return response.json()

    async def _arun(
        self,
        cashflows: list[float],
        discount_rate: float = 0.10,
        periods_per_year: float = 1.0,
    ) -> dict[str, Any]:
        return await asyncio.to_thread(
            self._run,
            cashflows,
            discount_rate,
            periods_per_year,
        )


# Preserve the original example import while steering new users to the accurate name.
HermesDealAnalyzer = HermesCashflowLens


if __name__ == "__main__":
    tool = HermesCashflowLens()
    result = tool.invoke({
        "cashflows": [-1_000_000, 250_000, 250_000, 300_000, 400_000],
        "discount_rate": 0.10,
        "periods_per_year": 1,
    })
    print(result)
