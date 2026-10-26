from __future__ import annotations

import importlib.util
from types import SimpleNamespace
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
TARGETS = {
    "python": ROOT / "python" / "01-call-endpoint.py",
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
        self.headers = {"PAYMENT-RESPONSE": "test-settlement"}

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

    def test_client_posts_documented_cashflowlens_shape(self):
        for name, module in self.modules.items():
            with self.subTest(name=name):
                session = FakeSession()
                context = FakeContext(session)
                with patch.object(module, "_paid_session", return_value=context):
                    if name == "python":
                        result, settlement = module.call_cashflow_lens(
                            [-100.0, 120.0],
                            0.15,
                            12,
                        )
                        self.assertEqual(settlement, "test-settlement")
                    else:
                        tool_class = (
                            module.HermesCashflowLens
                            if name == "langchain"
                            else module.HermesCashflowLensTool
                        )
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

    def test_source_labels_survive_sdk_payment_retry(self):
        import requests
        from requests.adapters import HTTPAdapter
        from x402 import x402ClientSync
        from x402.http.clients import x402_requests

        for name, module in self.modules.items():
            with self.subTest(name=name):
                client = x402ClientSync()
                client.create_payment_payload = Mock(return_value=object())
                session = x402_requests(client)
                adapter = session.get_adapter(module.CASHFLOW_LENS_URL)
                http = adapter._http_client
                captured = []

                def transport(request, **kwargs):
                    captured.append(request.copy())
                    response = requests.Response()
                    response.status_code = 402 if len(captured) == 1 else 200
                    response._content = b'{"ok": true}'
                    response.request = request
                    return response

                # Mock the payment contract/signature; exercise the real requests adapter.
                with patch.object(module, "_paid_session", return_value=session), \
                     patch.object(HTTPAdapter, "send", side_effect=transport), \
                     patch.object(http, "get_payment_required_response", return_value=object()), \
                     patch.object(http, "handle_payment_required", return_value=None), \
                     patch.object(http, "encode_payment_signature_header", return_value={"PAYMENT-SIGNATURE": "mock-no-wallet"}), \
                     patch.object(http, "process_payment_result", return_value=SimpleNamespace(recovered=False)):
                    if name == "python":
                        module.call_cashflow_lens([-100, 120])
                    else:
                        tool = module.HermesCashflowLens if name == "langchain" else module.HermesCashflowLensTool
                        tool()._run([-100, 120])

                self.assertEqual(len(captured), 2)
                for request in captured:
                    self.assertEqual(request.headers["x-hermes-channel"], "github-mcp-repo")
                    self.assertEqual(request.headers["x-hermes-medium"], "repository")
                    self.assertEqual(request.headers["x-hermes-campaign"], "first-workflow")
                    self.assertEqual(request.headers["x-hermes-content"], f"{name}-cashflowlens")
                self.assertNotIn("PAYMENT-SIGNATURE", captured[0].headers)
                self.assertEqual(captured[1].headers["PAYMENT-SIGNATURE"], "mock-no-wallet")
                self.assertEqual(captured[0].body, captured[1].body)

    def test_spend_cap_and_network_are_explicit(self):
        for name, module in self.modules.items():
            with self.subTest(name=name):
                self.assertEqual(module.CASHFLOW_LENS_PRICE_ATOMIC_USDC, 200_000)
                self.assertEqual(module.BASE_MAINNET, "eip155:8453")


if __name__ == "__main__":
    unittest.main()
