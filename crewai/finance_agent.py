"""
finance_agent.py

Two CrewAI agents:
  1. An *analyst* who uses HermesDealAnalyzerTool to compute IRR/NPV from
     a deal's cashflows.
  2. A *partner* who reads the analyst's findings and recommends accept or pass.

The tool wraps a Hermes Plant x402-paid endpoint. Every tool call settles
one USDC payment on Base mainnet. Pricing is bounded by the endpoint's
fixed price, not token count.
"""
from __future__ import annotations

import os
from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.tools import BaseTool
from eth_account import Account
from pydantic import BaseModel, Field
from x402.client import X402Client


class DealAnalyzerInput(BaseModel):
    cashflows: list[float] = Field(
        description="Period-indexed cashflows. Index 0 is the initial outlay (usually negative).",
    )
    discount_rate: float = Field(
        default=0.10,
        description="Discount rate as a decimal (0.10 = 10%).",
    )


class HermesDealAnalyzerTool(BaseTool):
    name: str = "hermes_deal_analyzer"
    description: str = (
        "Compute deterministic IRR, XIRR, and NPV from a cashflow series. "
        "Calls hermesplant.com/agent-services/dealanalyzer. Settles one USDC "
        "payment per call on Base mainnet."
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


def build_crew() -> Crew:
    analyzer_tool = HermesDealAnalyzerTool()

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
            "Compute IRR and NPV at a 10% discount rate using HermesDealAnalyzer. "
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
