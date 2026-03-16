import { spawnSync, execSync } from "child_process";
import * as fs from "fs";
import * as path from "path";
import * as os from "os";

const log = (msg) => { process.stdout.write(msg + "\n"); };

const NPM_BIN = path.join(os.homedir(), "AppData", "Roaming", "npm");
const CLAUDE_JS = path.join(NPM_BIN, "node_modules", "@anthropic-ai", "claude-code", "cli.js");
const BRIDGE_JS = path.join(NPM_BIN, "node_modules", "@mariozechner", "claude-bridge", "dist", "cli.js");
const INTERCEPTOR = path.join(NPM_BIN, "node_modules", "@mariozechner", "claude-bridge", "dist", "interceptor-loader.js");

log("=== Diagnostics ===");
log("CLAUDE_JS exists: " + fs.existsSync(CLAUDE_JS));
log("BRIDGE_JS exists: " + fs.existsSync(BRIDGE_JS));
log("INTERCEPTOR exists: " + fs.existsSync(INTERCEPTOR));
log("ANTHROPIC_API_KEY set: " + !!(process.env.ANTHROPIC_API_KEY));
log("OPENAI_API_KEY set: " + !!(process.env.OPENAI_API_KEY));
log("NODE_OPTIONS: " + (process.env.NODE_OPTIONS || "(none)"));
log("");

// Test: run claude --version directly
log("Testing claude --version...");
const ver = spawnSync("node", [CLAUDE_JS, "--version"], { encoding: "utf8", timeout: 5000 });
log("  stdout: " + (ver.stdout || "").trim());
log("  stderr: " + (ver.stderr || "").trim());
log("  status: " + ver.status);
if (ver.error) log("  error: " + ver.error.message);
log("");

// Test: run claude with dummy ANTHROPIC_API_KEY briefly
log("Testing claude with dummy key (2 sec)...");
const claude = spawnSync("node", [CLAUDE_JS, "--version"], {
  encoding: "utf8",
  timeout: 5000,
  env: { ...process.env, ANTHROPIC_API_KEY: "dummy-sk-test" }
});
log("  stdout: " + (claude.stdout || "").trim());
log("  stderr: " + (claude.stderr || "").trim());
log("  status: " + claude.status);
if (claude.error) log("  error: " + claude.error.message);
