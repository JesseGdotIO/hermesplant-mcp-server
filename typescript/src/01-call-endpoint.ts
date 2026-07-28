/**
 * Fail-closed x402 call to Hermes Plant's CashflowLens endpoint.
 */
import { wrapFetchWithPayment, x402Client } from "@x402/fetch";
import { ExactEvmScheme, toClientEvmSigner } from "@x402/evm";
import { pathToFileURL } from "node:url";
import { privateKeyToAccount } from "viem/accounts";

export const BASE_URL = (process.env.HERMES_BASE_URL ?? "https://hermesplant.com").replace(
  /\/$/,
  "",
);
export const CASHFLOW_LENS_PATH = "/api/agent-services/cashflowlens/analyze";
export const CASHFLOW_LENS_URL = `${BASE_URL}${CASHFLOW_LENS_PATH}`;
export const CASHFLOW_LENS_PRICE_ATOMIC_USDC = 200_000n;
export const BASE_MAINNET = "eip155:8453" as const;

export function buildPaidFetch(env: NodeJS.ProcessEnv = process.env): typeof fetch {
  if (env.HERMES_ALLOW_PAYMENT !== "1") {
    throw new Error(
      "Paid calls are disabled. Set HERMES_ALLOW_PAYMENT=1 after reviewing the fixed $0.20 USDC price.",
    );
  }

  const privateKey = env.EVM_PRIVATE_KEY as `0x${string}` | undefined;
  if (!privateKey) {
    throw new Error("Set EVM_PRIVATE_KEY to a 0x-prefixed Base mainnet EOA key.");
  }

  const signer = toClientEvmSigner(privateKeyToAccount(privateKey));
  const client = new x402Client()
    .register(BASE_MAINNET, new ExactEvmScheme(signer))
    .registerPolicy((_version, requirements) =>
      requirements.filter(
        (requirement) =>
          requirement.network === BASE_MAINNET &&
          BigInt(requirement.amount) <= CASHFLOW_LENS_PRICE_ATOMIC_USDC,
      ),
    );

  return wrapFetchWithPayment(fetch, client);
}

export async function callCashflowLens(fetchImpl: typeof fetch = buildPaidFetch()) {
  const response = await fetchImpl(CASHFLOW_LENS_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      cashflows: [-1_000_000, 250_000, 250_000, 300_000, 400_000],
      discountRate: 0.1,
      periodsPerYear: 1,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP ${response.status} ${response.statusText}: ${await response.text()}`);
  }

  return {
    result: await response.json(),
    settlement: response.headers.get("PAYMENT-RESPONSE"),
  };
}

async function main() {
  const { result, settlement } = await callCashflowLens();
  console.log("CashflowLens result:", JSON.stringify(result, null, 2));

  if (settlement) {
    const decoded = Buffer.from(settlement, "base64").toString("utf-8");
    console.log("Settlement:", decoded);
  }
}

const isDirectRun =
  process.argv[1] !== undefined && import.meta.url === pathToFileURL(process.argv[1]).href;

if (isDirectRun) {
  main().catch((error: unknown) => {
    console.error(error);
    process.exitCode = 1;
  });
}
