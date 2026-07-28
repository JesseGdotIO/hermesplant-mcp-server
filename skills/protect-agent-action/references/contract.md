# Action Safety contract

Read this reference before the first network call, before following a recommended call, and before authorizing x402 payment.

## Canonical endpoints

| Purpose | Method and URL | Exact current public price |
| --- | --- | --- |
| Quick gate | `POST https://hermesplant.com/api/agent-services/action-safety/quick` | $0.01 / 10,000 USDC atomic units |
| Full DestructGuard evidence | `POST https://hermesplant.com/api/agent-services/destructguard/score` | $0.10 / 100,000 USDC atomic units |
| Complete Action Safety workflow | `POST https://hermesplant.com/api/agent-services/action-safety/run` | $0.25 / 250,000 USDC atomic units |
| Workflow status | Returned `GET https://hermesplant.com/api/agent-workflows/action-safety/status/{workflowId}` | Free |
| Receipt verification | `POST https://hermesplant.com/api/agent-services/assurance/verify` | Free |

Never follow a recommended call to another origin. Fetch current endpoint metadata from `https://hermesplant.com/.well-known/x402` and schemas from `https://hermesplant.com/openapi.json`.

## External-disclosure and request contract

Before transmitting anything, require an existing user or system policy that explicitly permits sending the necessary operational metadata to `https://hermesplant.com`. If authorization is absent or safe semantic redaction is impossible, do not call the service and leave the action unexecuted.
Length limits are: command 2,000; repo, cwd, branch, environment, and actor 500 each; intent and target 1,000 each; diffStat 1,500; and commit and diffHash 200 characters each.

Values over these limits are rejected, never truncated. The caller must hash the normalized request accepted by the API; no two over-limit values may collapse to the same binding.
Every accepted string must already equal its trimmed form, and an optional string must not be blank. Non-canonical strings are rejected rather than transformed; compute the binding from the exact accepted request fields.



`command` is required and must describe the exact proposed action. Optional execution context is `repo`, `cwd`, `branch`, `environment`, `target`, `commit`, `diffHash`, `actor`, `intent`, and `diffStat`. Skill calls set `failClosedOnUnmatched: true`.

- Remove credentials, authentication headers, private keys, seed phrases, payment signatures, personal data, and proprietary metadata not authorized for disclosure.
- Preserve destructive flags, resolved target, environment, branch, database/table, package, infrastructure resource, force/recursive behavior, and commit/diff identity.
- If any execution-relevant field changes, discard the prior decision, use a new payment identifier, and call the quick gate again.
- Send credentials only to the exact HTTPS `hermesplant.com` origin.

## Access modes

Use an already configured access mode only:

1. `X-API-Key` for an existing free tier.
2. An already authorized Bearer credential for a live pass or Assurance entitlement.
3. Direct x402 payment when an existing user/system policy authorizes the exact endpoint and price.

Do not silently mint a free key, open an account, reveal a wallet, or convert an authentication failure into paid execution.

## x402 acceptance checks

Before signing, select exactly one acceptance option and require all of the following:

- scheme equals `exact`;
- method and resource equal the canonical POST endpoint;
- network equals `eip155:8453` (Base);
- asset equals `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (native Base USDC);
- atomic `amount` equals the exact price published for that exact method/path manifest entry and the matching challenge option, and does not exceed the hard ceiling above;
- `payTo` exactly equals the value published for that endpoint in the current Hermes `/.well-known/x402` manifest;
- facilitator and timeout satisfy the payer's local allow-list and limit.

Reject a merely lower amount, decimal rounding, alternate asset, changed recipient, wildcard resource, non-POST method, unexpected network, or higher amount. Never log or persist a wallet private key, payment signature, or raw authorization header.

## Payment identifier and retry lifecycle

The payment identifier is not an acceptance-option field. It is client data in `PaymentPayload.extensions["payment-identifier"].info.id`.

Before signing:

1. Confirm the PaymentRequired response declares the `payment-identifier` extension.
2. Generate a cryptographically unique identifier for this exact action, endpoint, and request body. It must be 16-128 characters and match `^[A-Za-z0-9_-]+$`.
3. Append it to the declared extension's `info.id` while retaining the server's `info.required` value and schema.
4. Persist the identifier and canonical action hash before signing.

Reuse that identifier only for an identical retry of the same action, endpoint, and body. Never reuse it for another action. After an ambiguous timeout, reconcile the identifier and settlement state before retrying; do not issue a second payment merely because the response was lost.

## Canonical action binding

Both paid responses expose:

- `actionBindingVersion: "hermes-action-v1"`
- `actionHash`: lowercase 64-character SHA-256 hex

To recompute, create this object with every key present and missing optional values represented as `null`:

```json
{
  "version": "hermes-action-v1",
  "command": "<exact command or action>",
  "repo": null,
  "cwd": null,
  "branch": null,
  "environment": null,
  "target": null,
  "commit": null,
  "diffHash": null,
  "actor": null,
  "intent": null,
  "diffStat": null
}
```

Canonicalize recursively as compact JSON with object keys sorted lexicographically, encode as UTF-8, and SHA-256 hash the bytes. Reject a response, receipt, recommended call, or status record whose binding differs from the locally recomputed value.

## Quick-gate response

Require:

- `status: "scored"`;
- `service: "action-safety-quick-gate"`;
- the exact binding version and matching action hash;
- `risk` in `low | medium | high | critical`;
- boolean `requiresApproval`;
- array `matchedRuleIds`;
- `nextRecommendedCall` matching the routing table below or `null`.

| Result | Required route |
| --- | --- |
| low and no approval | `nextRecommendedCall: null`; local/user policy still decides execution |
| medium | exact POST to `/api/agent-services/destructguard/score`, exact price 10 cents, identical mapped input |
| high or critical | exact POST to `/api/agent-services/action-safety/run`, exact price 25 cents, identical mapped input |
| `requiresApproval: true` | pause regardless of other fields |

With `failClosedOnUnmatched: true`, an unmatched consequential action must return high risk with `action.unmatched-consequential`. Treat a low result that contradicts known destructive, monetary, privilege-changing, externally mutating, or irreversible behavior as unresolved and do not execute.

## Complete-workflow response

Recognized decisions are `allow`, `allow_with_controls`, and `needs_review`.

- The binding version and action hash must match the quick request and local recomputation.
- `needs_review`, `allowed: false`, or `requiresHumanReview: true` means do not execute.
- `boundaries.humanApprovalIncluded` must be `false`; triage is not approval.
- `statusRecord.persisted: false` means no durable status record was proven. Do not claim retention or pollability.
- A missing or invalid receipt means the result is not independently verifiable. Do not describe it as signed or audited.
- An allow result never overrides user authorization or platform safety policy.

## Failure behavior

For a consequential action, fail closed on:

- timeout, DNS/TLS failure, non-JSON response, or HTTP 5xx;
- HTTP 401/403 without an already authorized alternate access mode;
- HTTP 402 when no exact payment policy is pre-authorized;
- HTTP 429 quota exhaustion;
- schema mismatch, unknown risk/decision, missing or mismatched binding, or an untrusted recommended URL.

Report the gate as unavailable or unresolved and leave the action unexecuted.
