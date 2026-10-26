import assert from "node:assert/strict";
import test from "node:test";
import { wrapFetchWithPayment, x402Client } from "@x402/fetch";

import {
  BASE_MAINNET,
  CASHFLOW_LENS_PRICE_ATOMIC_USDC,
  CASHFLOW_LENS_URL,
  buildPaidFetch,
  callCashflowLens,
} from "./01-call-endpoint.js";

test("paid fetch is disabled by default", () => {
  assert.throws(
    () => buildPaidFetch({ EVM_PRIVATE_KEY: "not-used" }),
    /Paid calls are disabled/,
  );
});

test("client posts the documented CashflowLens request without spending", async () => {
  let capturedUrl = "";
  let capturedInit: RequestInit | undefined;
  const fakeFetch: typeof fetch = async (input, init) => {
    capturedUrl = String(input);
    capturedInit = init;
    return new Response(JSON.stringify({ ok: true }), {
      status: 200,
      headers: { "PAYMENT-RESPONSE": "dGVzdA==" },
    });
  };

  const output = await callCashflowLens(fakeFetch);

  assert.deepEqual(output.result, { ok: true });
  assert.equal(output.settlement, "dGVzdA==");
  assert.equal(capturedUrl, CASHFLOW_LENS_URL);
  assert.equal(capturedInit?.method, "POST");
  assert.deepEqual(JSON.parse(String(capturedInit?.body)), {
    cashflows: [-1_000_000, 250_000, 250_000, 300_000, 400_000],
    discountRate: 0.1,
    periodsPerYear: 1,
  });
  assert.equal(BASE_MAINNET, "eip155:8453");
  assert.equal(CASHFLOW_LENS_PRICE_ATOMIC_USDC, 200_000n);
});

test("source labels survive the real SDK's 402 payment retry without signing or spending", async () => {
  const requests: Request[] = [];
  const requirement = {
    scheme: "exact",
    network: BASE_MAINNET,
    amount: "200000",
    asset: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    payTo: "0x1111111111111111111111111111111111111111",
    maxTimeoutSeconds: 60,
    extra: {},
  };
  const resource = { url: CASHFLOW_LENS_URL, description: "Mock only", mimeType: "application/json" };
  const client = new x402Client();
  // Stub signing only; use the installed SDK's real request parsing and retry.
  client.createPaymentPayload = async () => ({
    x402Version: 2,
    accepted: requirement,
    resource,
    payload: { signature: "mock-no-wallet-no-settlement" },
  });
  const transport: typeof fetch = async (input, init) => {
    const request = new Request(input, init);
    requests.push(request.clone());
    if (requests.length === 1) {
      return new Response("{}", {
        status: 402,
        headers: { "PAYMENT-REQUIRED": Buffer.from(JSON.stringify({
          x402Version: 2, resource, accepts: [requirement],
        })).toString("base64") },
      });
    }
    return Response.json({ ok: true });
  };
  await callCashflowLens(wrapFetchWithPayment(transport, client));
  assert.equal(requests.length, 2);
  for (const request of requests) {
    assert.equal(request.headers.get("x-hermes-channel"), "github-mcp-repo");
    assert.equal(request.headers.get("x-hermes-medium"), "repository");
    assert.equal(request.headers.get("x-hermes-campaign"), "first-workflow");
    assert.equal(request.headers.get("x-hermes-content"), "typescript-cashflowlens");
  }
  assert.equal(requests[0].headers.has("PAYMENT-SIGNATURE"), false);
  assert.equal(requests[1].headers.has("PAYMENT-SIGNATURE"), true);
  assert.equal(await requests[0].text(), await requests[1].text());
});
