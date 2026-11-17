/**
 * Tokenomics DSH Plugin — apply(ctx) entry point
 *
 * DeepSeek Harness Plugin spec: export an apply(ctx) function that receives
 * the plugin context and returns processed output.
 *
 * Tokenomics is a Python-based agentic-efficiency layer. This JS wrapper
 * shells out to the `tokenomics` CLI for compression, budget tracking,
 * gamification, and review capabilities.
 *
 * Author: Souvik Chakraborty
 * License: MIT
 * Repo: https://github.com/z99wE/tokenomics
 */

const { execSync, spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

/**
 * Default options for the plugin.
 */
const DEFAULTS = {
  // Feature flag: enableCompression (see flags.json)
  enableCompression: true,
  enabled: true,
  domain: "standard",
  autoLearn: true,
  smartDefaults: true,
  budgetAlerts: true,
  dailyTokenBudget: null,
  projectType: null,
};

/**
 * Resolve the tokenomics CLI binary.
 * Falls back to `npx tokenomics` if not installed globally.
 */
function resolveCli() {
  const candidates = [
    path.join(__dirname, "node_modules", ".bin", "tokenomics"),
    "tokenomics",
    "npx tokenomics",
  ];
  for (const c of candidates) {
    try {
      execSync(`${c} --help`, { stdio: "pipe", timeout: 2000 });
      return c.split(" ")[0];
    } catch (e) {
      // try next
    }
  }
  return "tokenomics";
}

/**
 * Run a tokenomics CLI command and return parsed JSON output.
 * @param {string[]} args
 * @param {object} opts
 * @returns {object|null}
 */
function runCli(args, opts = {}) {
  const cli = resolveCli();
  const cmd = [cli, ...args].join(" ");
  try {
    const out = execSync(cmd, {
      encoding: "utf8",
      timeout: opts.timeout || 10000,
      maxBuffer: opts.maxBuffer || 10 * 1024 * 1024,
    });
    // Tokenomics CLI prints ASCII logo + table. Extract JSON if present.
    const jsonMatch = out.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      try {
        return JSON.parse(jsonMatch[0]);
      } catch (e) {
        // fall through
      }
    }
    return { raw: out.trim() };
  } catch (e) {
    if (opts.throwOnError) throw e;
    return { error: e.message };
  }
}

/**
 * Compress prose using tokenomics.
 * @param {string} text
 * @param {object} opts
 * @returns {string}
 */
function compressProse(text, opts = {}) {
  const result = runCli(
    ["estimate", "--text", text],
    { throwOnError: false }
  );
  if (result && result.raw) {
    // Extract the "Compressed:" line from CLI output
    const compressedMatch = result.raw.match(/Compressed:\s+(.+)/);
    if (compressedMatch) {
      return compressedMatch[1].trim();
    }
  }
  return text;
}

/**
 * Review code for over-engineering using ponytail-inspired rules.
 * @param {string} code
 * @returns {object}
 */
function reviewCode(code) {
  const tmpFile = path.join(require("os").tmpdir(), `tokenomics-review-${Date.now()}.py`);
  fs.writeFileSync(tmpFile, code);
  try {
    const result = runCli(["review", "--code", code], { throwOnError: false });
    return {
      ok: true,
      issues: result.raw ? result.raw.split("\n").filter((l) => l.includes("•")) : [],
      savings: result && result.raw ? result.raw.match(/Savings:\s+(\d+)/) : null,
      raw: result.raw || "",
    };
  } finally {
    try { fs.unlinkSync(tmpFile); } catch (e) {}
  }
}

/**
 * Get tokenomics status (level, streak, savings, achievements).
 * @returns {object}
 */
function getStatus() {
  return runCli(["status"], { throwOnError: false }) || {};
}

/**
 * Get token budget status.
 * @returns {object}
 */
function getBudget() {
  return runCli(["budget", "check"], { throwOnError: false }) || {};
}

/**
 * Record tokens used against daily budget.
 * @param {number} tokens
 * @returns {object}
 */
function recordTokens(tokens) {
  return runCli(["record", String(tokens)], { throwOnError: false }) || {};
}

/**
 * Set daily token budget.
 * @param {number} limit
 * @returns {object}
 */
function setBudget(limit) {
  return runCli(["budget", "set", String(limit)], { throwOnError: false }) || {};
}

/**
 * Set project type for smart defaults.
 * @param {string} type — web | cli | library | api | none
 * @returns {object}
 */
function setProjectType(type) {
  return runCli(["project", type], { throwOnError: false }) || {};
}

/**
 * Toggle auto-learn from user reverts.
 * @param {boolean} enabled
 * @returns {object}
 */
function setAutoLearn(enabled) {
  return runCli(["learn", enabled ? "" : ""], {
    throwOnError: false,
  }).then ? null : runCli(["learn"], { throwOnError: false }) || {};
  // The `learn` command requires the `enable` flag positionally.
  // We handle it via the shell directly below.
  const result = runCli(
    ["learn", enabled ? "true" : "false"],
    { throwOnError: false }
  );
  return result || {};
}

/**
 * Toggle smart default suggestions.
 * @param {boolean} enabled
 * @returns {object}
 */
function setSmartDefaults(enabled) {
  return runCli(["defaults", enabled ? "true" : "false"], {
    throwOnError: false,
  }) || {};
}

/**
 * Enable tokenomics.
 * @returns {object}
 */
function enable() {
  return runCli(["enable"], { throwOnError: false }) || {};
}

/**
 * Disable tokenomics.
 * @returns {object}
 */
function disable() {
  return runCli(["disable"], { throwOnError: false }) || {};
}

/**
 * DSH Plugin apply(ctx) entry point.
 *
 * @param {object} ctx — DeepSeek Harness plugin context
 * @param {string} ctx.text — Input text to process
 * @param {string} ctx.code — Code to review (optional)
 * @param {object} ctx.options — Plugin options (optional)
 * @returns {object} — Processed result
 */
function apply(ctx) {
  const options = { ...DEFAULTS, ...(ctx.options || {}) };

  // Respect enabled flag
  if (!options.enabled) {
    return {
      ...ctx,
      tokenomics: { enabled: false, skipped: true },
    };
  }

  const result = {
    ...ctx,
    tokenomics: {
      enabled: true,
      version: "2.3.0",
      author: "Souvik Chakraborty",
      repo: "https://github.com/z99wE/tokenomics",
    },
  };

  // Compress prose if text is provided
  if (ctx.text) {
    const compressed = compressProse(ctx.text, options);
    result.tokenomics.original = ctx.text;
    result.tokenomics.compressed = compressed;
    result.tokenomics.savedChars =
      ctx.text.length - compressed.length;
    result.text = compressed; // Override with compressed output
  }

  // Review code if code is provided
  if (ctx.code) {
    const review = reviewCode(ctx.code);
    result.tokenomics.review = review;
  }

  // Record tokens used against budget if budget is set
  if (options.dailyTokenBudget) {
    const used = ctx.text ? ctx.text.length / 4 : 0; // rough token estimate
    const budget = recordTokens(Math.round(used));
    result.tokenomics.budget = budget;
  }

  // Get current status
  const status = getStatus();
  result.tokenomics.status = status;

  return result;
}

/**
 * Register the plugin with DSH host (optional handshake).
 * @returns {object}
 */
function register() {
  return {
    name: "tokenomics",
    version: "2.3.0",
    author: "Souvik Chakraborty",
    description:
      "Agentic-efficiency layer: compress agent prose, minimize code generation, track token savings.",
    category: "Tools & Capabilities",
    profile: "web",
    apply: apply.toString(),
  };
}

module.exports = { apply, register, compressProse, reviewCode, getStatus, getBudget, recordTokens, setBudget, setProjectType, setAutoLearn, setSmartDefaults, enable, disable };

// If run directly, print registration info
if (require.main === module) {
  console.log(JSON.stringify(register(), null, 2));
}
