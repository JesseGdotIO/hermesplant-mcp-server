from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "langchain": ROOT / "langchain" / "hermes_tool.py",
    "crewai": ROOT / "crewai" / "finance_agent.py",
}


def load_target(name: str):
    path = TARGETS[name]
    spec = importlib.util.spec_from_file_location(f"hermes_{name}_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeResponse:
    def __init__(self):
        self.raise_called = False

    def raise_for_status(self):
        self.raise_called = True

    def json(self):
        return {"ok": True}


class FakeSession:
    def __init__(self):
        self.calls = []
        self.response = FakeResponse()

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.response


class FakeContext:
    def __init__(self, session):
        self.session = session

    def __enter__(self):
        return self.session

    def __exit__(self, exc_type, exc, tb):
        return False


class FrameworkAdapterContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        selected = os.getenv("FRAMEWORK_TARGET")
        names = [selected] if selected else list(TARGETS)
        cls.modules = {name: load_target(name) for name in names}

    def test_payment_is_disabled_by_default(self):
        for name, module in self.modules.items():
            with self.subTest(name=name), patch.dict(
                os.environ,
                {"EVM_PRIVATE_KEY": "not-used-while-disabled"},
                clear=True,
            ):
                with self.assertRaisesRegex(RuntimeError, "Paid calls are disabled"):
                    module._paid_session()

    def test_tool_posts_documented_cashflowlens_shape(self):
        for name, module in self.modules.items():
            with self.subTest(name=name):
                session = FakeSession()
                context = FakeContext(session)
                tool_class = (
                    module.HermesCashflowLens
                    if name == "langchain"
                    else module.HermesCashflowLensTool
                )
                with patch.object(module, "_paid_session", return_value=context):
                    result = tool_class()._run([-100.0, 120.0], 0.15, 12)

                self.assertEqual(result, {"ok": True})
                self.assertTrue(session.response.raise_called)
                self.assertEqual(len(session.calls), 1)
                url, kwargs = session.calls[0]
                self.assertEqual(url, module.CASHFLOW_LENS_URL)
                self.assertEqual(kwargs["timeout"], 30)
                self.assertEqual(
                    kwargs["json"],
                    {
                        "cashflows": [-100.0, 120.0],
                        "discountRate": 0.15,
                        "periodsPerYear": 12,
                    },
                )

    def test_spend_cap_and_network_are_explicit(self):
        for name, module in self.modules.items():
            with self.subTest(name=name):
                self.assertEqual(module.CASHFLOW_LENS_PRICE_ATOMIC_USDC, 200_000)
                self.assertEqual(module.BASE_MAINNET, "eip155:8453")


if __name__ == "__main__":
    unittest.main()
