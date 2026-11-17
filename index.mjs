/**
 * Tokenomics — DSH (DeepSeek Harness) plugin entry point.
 *
 * Exports the cordis plugin shape DSH expects:
 *   - name        : module identity
 *   - inject      : declared services (none required)
 *   - apply(ctx)  : mounts the plugin
 *
 * The tokenomics CLI is the source of truth for compression; this bundle
 * registers optional tools when the DSH tools service is available.
 */

import { execSync } from "node:child_process";

export const name = "tokenomics";
export const inject = [];

function runCli(args) {
  try {
    return execSync(["tokenomics", ...args].join(" "), {
      encoding: "utf8",
      timeout: 10000,
      stdio: ["pipe", "pipe", "pipe"],
    }).trim();
  } catch {
    return "tokenomics CLI not available. Install it with: pip install tokenomics";
  }
}

export function apply(ctx) {
  ctx.effect(() => {
    console.log("[tokenomics] mounted — agentic efficiency layer active.");
    return () => console.log("[tokenomics] unmounted");
  });

  const register = ctx?.tools?.register;
  if (typeof register !== "function") {
    console.log("[tokenomics] DSH tools service not available — mounting without tools.");
    return;
  }

  register({
    name: "tokenomics_status",
    description: "Show tokenomics status: savings, level, streak, achievements.",
    parameters: { type: "object", properties: {}, required: [] },
    async execute() {
      return { content: runCli(["status"]) };
    },
  });

  register({
    name: "tokenomics_estimate",
    description: "Estimate token savings for a text.",
    parameters: {
      type: "object",
      properties: {
        text: { type: "string", description: "Text to estimate" },
      },
      required: ["text"],
    },
    async execute({ text } = {}) {
      return { content: runCli(["estimate", String(text ?? "")]) };
    },
  });

  register({
    name: "tokenomics_review",
    description: "Ponytail-style over-engineering review of a code snippet.",
    parameters: {
      type: "object",
      properties: {
        code: { type: "string", description: "Code to review" },
      },
      required: ["code"],
    },
    async execute({ code } = {}) {
      return { content: runCli(["review", "--code", String(code ?? "")]) };
    },
  });
}
