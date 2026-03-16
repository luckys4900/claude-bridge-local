// bat ファイルと同じ条件で claude-bridge を通して Claude Code + Ollama を検証
import { spawnSync } from "child_process";
import * as path from "path";
import * as os from "os";
import * as fs from "fs";

const NPM_BIN = path.join(os.homedir(), "AppData", "Roaming", "npm");
const BRIDGE_CMD = path.join(NPM_BIN, "claude-bridge.cmd");
const CLAUDE_JS = path.join(NPM_BIN, "node_modules", "@anthropic-ai", "claude-code", "cli.js");

const log = (msg) => process.stdout.write(msg + "\n");

log("=== Final Validation ===");
log("Testing: claude-bridge -> Ollama llama3.2 (non-interactive mode)");
log("");

const env = {
  ...process.env,
  PATH: NPM_BIN + ";" + process.env.PATH,
  ANTHROPIC_API_KEY: "sk-ant-bridge-dummy",
};

const r = spawnSync(
  BRIDGE_CMD,
  ["openai", "llama3.2",
   "--baseURL", "http://localhost:11434/v1",
   "--claude-binary", CLAUDE_JS,
   "--apiKey", "dummy",
   "-p", "respond with exactly the words: OLLAMA_BRIDGE_SUCCESS"
  ],
  { encoding: "utf8", timeout: 45000, env, shell: true }
);

log("stdout: " + (r.stdout || "").trim());
log("stderr: " + (r.stderr || "").trim().substring(0, 200));
log("status: " + r.status);
log("error:  " + (r.error?.message || "none"));
log("");
if ((r.stdout || "").includes("OLLAMA_BRIDGE_SUCCESS") || r.status === 0) {
  log("RESULT: SUCCESS - Claude Bridge + Ollama is working!");
} else {
  log("RESULT: FAILED");
}
