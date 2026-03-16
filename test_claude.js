import { spawnSync } from "child_process";
import * as path from "path";
import * as os from "os";
import * as fs from "fs";
import { pathToFileURL } from "url";

const NPM_BIN = path.join(os.homedir(), "AppData", "Roaming", "npm");
const CLAUDE_JS = path.join(NPM_BIN, "node_modules", "@anthropic-ai", "claude-code", "cli.js");
const BRIDGE_JS = path.join(NPM_BIN, "node_modules", "@mariozechner", "claude-bridge", "dist", "cli.js");
const INTERCEPTOR = path.join(NPM_BIN, "node_modules", "@mariozechner", "claude-bridge", "dist", "interceptor-loader.js");
// Use file:// URL for Windows compatibility
const INTERCEPTOR_URL = pathToFileURL(INTERCEPTOR).href;

const LOG = path.join(os.homedir(), "Desktop", "claude-bridge-local", "test_result.txt");
const log = (msg) => {
  fs.appendFileSync(LOG, msg + "\n");
  process.stdout.write(msg + "\n");
};

fs.writeFileSync(LOG, "=== Test Start ===\n");
log("INTERCEPTOR_URL: " + INTERCEPTOR_URL);

// Test: full claude-bridge with interceptor using file:// URL
log("[Test] claude-bridge interceptor launch (file:// URL fix)");
const bridgeConfig = {
  provider: "openai",
  model: "llama3.2:latest",
  apiKey: "dummy",
  baseURL: "http://localhost:11434/v1",
  maxRetries: 1,
  debug: false
};
const spawnArgs = [
  "--import", INTERCEPTOR_URL,
  "--no-deprecation",
  CLAUDE_JS,
  "-p", "respond with exactly: BRIDGE_OK"
];
log("spawnArgs: " + spawnArgs.join(" "));
const r = spawnSync("node", spawnArgs, {
  encoding: "utf8",
  timeout: 30000,
  env: {
    ...process.env,
    ANTHROPIC_API_KEY: "sk-ant-dummy",
    NODE_OPTIONS: "--no-deprecation",
    CLAUDE_BRIDGE_CONFIG: JSON.stringify(bridgeConfig)
  }
});
log("  stdout: " + (r.stdout || "").substring(0, 500));
log("  stderr: " + (r.stderr || "").substring(0, 500));
log("  status: " + r.status + " error: " + (r.error?.message || "none"));
log("=== Done ===");
