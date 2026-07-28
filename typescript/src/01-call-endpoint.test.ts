import assert from "node:assert/strict";
import test from "node:test";

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
