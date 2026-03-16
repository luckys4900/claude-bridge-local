/**
 * Launcher: proxy + Claude Code
 * Usage: node launcher.mjs <mode> <model> [claude args...]
 *   mode  : "openrouter" | "ollama"
 *   model : e.g. "deepseek/deepseek-chat-v3-0324" or "llama3.2:latest"
 */
import { spawn, spawnSync, execSync } from "child_process";
import path from "path";
import os from "os";
import { fileURLToPath } from "url";

const __dirname  = path.dirname(fileURLToPath(import.meta.url));
const PROXY_FILE = path.join(__dirname, "proxy.mjs");
const NPM_BIN    = path.join(os.homedir(), "AppData", "Roaming", "npm");
const CLAUDE_JS  = path.join(NPM_BIN, "node_modules", "@anthropic-ai", "claude-code", "cli.js");
const PORT       = 9099;

const mode       = process.argv[2] || "openrouter";
const model      = process.argv[3] || "deepseek/deepseek-chat-v3-0324";
const claudeArgs = process.argv.slice(4);


// ─── 0. Kill any existing process on the port ────────────────────────────────
try {
  const out = execSync(
    `powershell -Command "Get-NetTCPConnection -LocalPort ${PORT} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"`,
    { encoding: "utf8", timeout: 5000 }
  ).trim();
  if (out) {
    for (const pid of out.split(/\r?\n/).filter(Boolean)) {
      try { execSync(`taskkill /PID ${pid.trim()} /F`, { timeout: 3000 }); } catch {}
    }
    await new Promise(r => setTimeout(r, 500));
  }
} catch {}

// ─── 1. Start proxy ──────────────────────────────────────────────────────────
const proxy = spawn(process.execPath, [PROXY_FILE], {
  env: { ...process.env, PROXY_MODE: mode, OLLAMA_MODEL: model, PROXY_PORT: String(PORT) },
  stdio: ["ignore", "pipe", "pipe"]
});
proxy.stderr.on("data", d => process.stderr.write("[proxy] " + d));

// ─── 2. Wait for proxy ready ─────────────────────────────────────────────────
await new Promise((resolve, reject) => {
  const timer = setTimeout(() => reject(new Error("Proxy startup timeout (10s)")), 10000);
  proxy.stdout.on("data", d => {
    if (d.toString().includes("PROXY_READY")) { clearTimeout(timer); resolve(); }
  });
  proxy.on("exit", code => reject(new Error(`Proxy exited early (code ${code})`)));
});

console.log("[OK] Proxy ready. Starting Claude Code...\n");

// ─── 3. Start Claude Code ─────────────────────────────────────────────────────
const result = spawnSync(process.execPath, [CLAUDE_JS, ...claudeArgs], {
  stdio: "inherit",
  env: {
    ...process.env,
    ANTHROPIC_BASE_URL: `http://127.0.0.1:${PORT}`,
    ANTHROPIC_API_KEY:  "sk-ant-local-bridge",
  },
});

// ─── 4. Cleanup ───────────────────────────────────────────────────────────────
proxy.kill();
if (result.error) {
  console.error("\n[ERROR]", result.error.message);
  process.exit(1);
}
console.log(`\n[Done] Claude exited (code ${result.status ?? 0})`);
process.exit(result.status ?? 0);
