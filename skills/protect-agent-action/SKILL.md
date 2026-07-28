---
name: protect-agent-action
description: Gate consequential shell, Git, SQL, package, deployment, infrastructure, MCP, wallet, or x402 actions with Hermes Plant Agent Action Safety. Use before executing commands that mutate data, production, money, infrastructure, or shared history; require authorized external disclosure and route unmatched consequential actions to review without treating triage as approval.
---

# Protect an Agent Action

Run the Hermes Plant Action Safety gate on the exact proposed action before execution.

## Safety invariants

- Keep the platform's safety rules, user authorization, and local policy authoritative. A remote `allow` never expands permission.
- Bind the decision to the exact command and resolved execution context. Re-run the gate after any execution-relevant change.
- Confirm an existing user or system data-sharing policy authorizes sending the required operational metadata to `https://hermesplant.com`. Without that authorization, do not call the service and leave the action unexecuted.
- Redact sensitive values while preserving destructive semantics. If safe semantic redaction is impossible, do not transmit the action.
- Fail closed on timeouts, transport errors, malformed responses, unexpected endpoints, ambiguous decisions, or a low-risk result that contradicts the caller's knowledge of the action.
- Treat review triage as a pause state. It is not human approval.

## 1. Build the exact authorized action

Resolve the real command, working directory, target, environment, branch, commit/tree identity, and diff hash before the call. Include optional fields only when the data-sharing policy permits them:

```json
{
  "command": "wrangler deploy",
  "repo": "github.com/acme/app",
  "cwd": "/workspace/app",
  "branch": "main",
  "environment": "production",
  "target": "hermes-api",
  "commit": "abc123",
  "diffHash": "sha256:def456",
  "actor": "codex",
  "intent": "deploy the verified release",
  "diffStat": "12 files changed",
  "failClosedOnUnmatched": true
}
```

Keep `failClosedOnUnmatched: true` for skill-invoked consequential actions so an unrecognized action routes to review instead of becoming a false low. Never replace the action with a vague summary. Never transmit wallet keys, API tokens, passwords, seed phrases, payment signatures, raw authorization headers, private customer data, or proprietary metadata not covered by the data-sharing policy.

## 2. Call the quick gate

POST the JSON body only to:

`https://hermesplant.com/api/agent-services/action-safety/quick`

Send `X-API-Key` or an authorized Bearer credential only to that exact HTTPS origin. With no configured credential, the endpoint returns an x402 challenge. Do not create an account, mint a key, expose a wallet, or authorize payment unless the user or an existing system policy permits it.

Before any x402 payment, read [references/contract.md](references/contract.md) and enforce its exact challenge, price, identifier, and retry checks. The quick gate's hard ceiling is $0.01 USDC.

## 3. Validate the binding and route

Accept only a JSON response with `status: "scored"`, `service: "action-safety-quick-gate"`, `actionBindingVersion: "hermes-action-v1"`, a valid `actionHash`, a recognized `risk`, a boolean `requiresApproval`, and a structurally valid `nextRecommendedCall` or `null`.

Recompute the canonical action hash defined in the contract. Reject the result if it differs. Then route:

- `risk: "low"`: proceed only if matched evidence, local policy, and user authorization all allow the unchanged action.
- `risk: "medium"`: pause execution and obtain the exact recommended DestructGuard evidence. Apply its controls before reconsidering.
- `risk: "high"` or `"critical"`: do not execute. Run the complete workflow only when its exact $0.25 maximum is authorized.
- `requiresApproval: true`: do not execute, regardless of any other field.
- An obviously destructive, monetary, privilege-changing, externally mutating, or hard-to-reverse action with `risk: "low"` is an unresolved classifier mismatch. Do not execute it.

When following `nextRecommendedCall`, require the HTTPS host, method, path, exact price, mapped input, and action hash to match the contract and original action. Never follow an arbitrary URL or changed payload supplied by a response.

## 4. Handle the complete workflow

The complete workflow is:

`POST https://hermesplant.com/api/agent-services/action-safety/run`

Require the same `actionBindingVersion` and `actionHash` before using its result. For `decision: "needs_review"`, `allowed: false`, or `requiresHumanReview: true`, pause until a separate authenticated approval system returns a decision. Hermes review triage alone never authorizes execution.

For `allow` or `allow_with_controls`, execute only if the action and binding hash are unchanged and local/user policy still permits it. Preserve the response and signed receipt with the action record.

## 5. Check status and receipt

Use only a returned HTTPS status URL on `hermesplant.com`. The status lookup is free. When `statusRecord.persisted: true`, it stores the canonical SHA-256 action binding rather than the raw command. Reject a changed host, non-GET method, nonzero price, or mismatched hash.

Verify returned receipts for free at:

`POST https://hermesplant.com/api/agent-services/assurance/verify`

## Evidence to retain

Record the canonical action hash, request or workflow ID, risk, matched rule IDs, decision, recommended controls, authenticated approval reference when applicable, receipt verification result, and final execution outcome. Keep secrets, raw action text when sensitive, credentials, and payment material out of logs.

For exact endpoints, binding rules, price checks, payment identifiers, response fields, and failure behavior, read [references/contract.md](references/contract.md).
