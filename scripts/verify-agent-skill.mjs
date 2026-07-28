import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("..", import.meta.url));
const skillRoot = path.join(root, "skills", "protect-agent-action");
const requiredFiles = [
  "SKILL.md",
  "agents/openai.yaml",
  "references/contract.md",
];

const contents = new Map(
  await Promise.all(
    requiredFiles.map(async (relative) => [
      relative,
      await readFile(path.join(skillRoot, ...relative.split("/")), "utf8"),
    ]),
  ),
);
const skill = contents.get("SKILL.md");
const contract = contents.get("references/contract.md");
const openai = contents.get("agents/openai.yaml");

assert.match(skill, /^---\r?\nname: protect-agent-action\r?\n/m);
assert.match(skill, /^description: .+/m);
assert.match(skill, /https:\/\/hermesplant\.com\/api\/agent-services\/action-safety\/quick/);
assert.match(skill, /hard ceiling is \$0\.01 USDC/);
assert.match(skill, /complete workflow only when its exact \$0\.25 maximum is authorized/);
assert.match(skill, /review triage alone never authorizes execution/i);
assert.match(skill, /fail closed/i);
assert.match(skill, /\[references\/contract\.md\]\(references\/contract\.md\)/);
assert.doesNotMatch(skill, /JesseGdotIO\/HermesPlant/);

assert.match(contract, /hermes-action-v1/);
assert.match(contract, /PaymentRequired/);
assert.match(contract, /payment signature/i);
assert.match(contract, /0\.01/);
assert.match(contract, /0\.25/);
assert.match(openai, /display_name: "Hermes Action Safety"/);

console.log(JSON.stringify({
  valid: true,
  skill: "protect-agent-action",
  files: requiredFiles,
  publicSource: "https://github.com/JesseGdotIO/hermesplant-mcp-server/tree/main/skills/protect-agent-action",
}, null, 2));
