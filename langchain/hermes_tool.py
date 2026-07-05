"""
hermes_tool.py

LangChain BaseTool wrapping Hermes Plant's DealAnalyzer endpoint. Demonstrates
the pattern: copy and rename for other Hermes endpoints.
"""
from __future__ import annotations

import os
from typing import Any

from eth_account import Account
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field
from x402.client import X402Client


class DealAnalyzerInput(BaseModel):
    cashflows: list[float] = Field(
        description="Cashflows by period. Index 0 is the initial outlay (typically negative).",
    )
    discount_rate: float = Field(
        default=0.10,
        description="Discount rate as a decimal (e.g. 0.10 for 10%).",
    )


class HermesDealAnalyzer(BaseTool):
    name: str = "hermes_deal_analyzer"
    description: str = (
        "Compute deterministic IRR, XIRR, and NPV from a cashflow series. "
        "Use this tool whenever the user asks for an IRR, NPV, or DCF "
        "calculation. Never compute these yourself; the math API is "
        "authoritative. Settles one USDC payment per call on Base mainnet."
    )
    args_schema: type[BaseModel] = DealAnalyzerInput

    def _run(self, cashflows: list[float], discount_rate: float = 0.10) -> dict[str, Any]:
        pk = os.environ["WALLET_PRIVATE_KEY"]
        account = Account.from_key(pk)
        client = X402Client(account=account)
        response = client.request(
            "POST",
            "https://hermesplant.com/agent-services/dealanalyzer",
            json={"cashflows": cashflows, "discountRate": discount_rate},
        )
        response.raise_for_status()
        return response.json()

    async def _arun(self, cashflows: list[float], discount_rate: float = 0.10) -> dict[str, Any]:
        # Sync path keeps the example readable; for production use httpx.AsyncClient
        # plus the x402 async client.
        return self._run(cashflows, discount_rate)


if __name__ == "__main__":
    tool = HermesDealAnalyzer()
    result = tool.invoke({
        "cashflows": [-1_000_000, 250_000, 250_000, 300_000, 400_000],
        "discount_rate": 0.10,
    })
    print(result)
