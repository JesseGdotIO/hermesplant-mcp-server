"""
CrewAI example using Hermes Plant's CashflowLens x402 endpoint.

The adapter is fail-closed: it will not spend unless HERMES_ALLOW_PAYMENT=1,
and it refuses any payment above the endpoint's fixed $0.20 USDC price.
"""
from __future__ import annotations

import os
from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.tools import BaseTool
from eth_account import Account
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
        description="Period-indexed cashflows. Index 0 is the initial outlay (usually negative).",
    )
    discount_rate: float = Field(
        default=0.10,
        description="Annual discount rate as a decimal (0.10 = 10%).",
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


class HermesCashflowLensTool(BaseTool):
    name: str = "hermes_cashflow_lens"
    description: str = (
        "Compute deterministic periodic IRR and NPV from a cashflow series. "
        "Calls the Hermes Plant CashflowLens API and settles a fixed $0.20 "
        "USDC payment on Base mainnet."
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


# Preserve the original example import while steering new users to the accurate name.
HermesDealAnalyzerTool = HermesCashflowLensTool


def build_crew() -> Crew:
    analyzer_tool = HermesCashflowLensTool()

    analyst = Agent(
        role="Investment analyst",
        goal=(
            "Evaluate the financial attractiveness of a candidate deal using "
            "deterministic finance math from Hermes Plant. Never guess IRR or NPV."
        ),
        backstory=(
            "You compute returns precisely. When a number can come from a calc "
            "API, you use the calc API. You quote results with provenance."
        ),
        tools=[analyzer_tool],
        verbose=True,
    )

    partner = Agent(
        role="Managing partner",
        goal="Approve, reject, or counter the deal based on the analyst's findings.",
        backstory="Pragmatic. Demands cited numbers. Refuses to act on vibes.",
        verbose=True,
    )

    analyze_task = Task(
        description=(
            "Evaluate this deal:\n"
            "  Initial outlay: $1,000,000\n"
            "  Year 1 cash: $250,000\n"
            "  Year 2 cash: $250,000\n"
            "  Year 3 cash: $300,000\n"
            "  Year 4 cash: $400,000\n"
            "Compute IRR and NPV at a 10% discount rate using HermesCashflowLens. "
            "Report the raw numbers with source attribution."
        ),
        agent=analyst,
        expected_output="A short paragraph with IRR, NPV, and provenance (the endpoint URL).",
    )

    decide_task = Task(
        description=(
            "Read the analyst's report. If IRR > 15% and NPV > 0, recommend ACCEPT. "
            "Otherwise PASS, with a one-line reason."
        ),
        agent=partner,
        expected_output="ACCEPT or PASS, with a one-sentence justification.",
        context=[analyze_task],
    )

    return Crew(
        agents=[analyst, partner],
        tasks=[analyze_task, decide_task],
        process=Process.sequential,
        verbose=True,
    )


if __name__ == "__main__":
    crew = build_crew()
    result = crew.kickoff()
    print("\n=== Crew result ===")
    print(result)
