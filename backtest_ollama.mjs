/**
 * Ollama バックテスト - ローカルモデル経由の動作確認
 * Usage: node backtest_ollama.mjs [model]
 *   model: llama3.2:latest | qwen3:30b | qwen3:8b (default: llama3.2:latest)
 */
import { spawn } from "child_process";
import http from "http";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const MODEL = process.argv[2] || "llama3.2:latest";
const PORT = 9198; // 9099と競合しないよう別ポート

function log(msg) {
  console.log(`[backtest] ${msg}`);
}

async function run() {
  log(`開始: model=${MODEL}, mode=ollama`);

  const proxy = spawn("node", ["proxy.mjs"], {
    env: { ...process.env, PROXY_MODE: "ollama", OLLAMA_MODEL: MODEL, PROXY_PORT: String(PORT) },
    cwd: __dirname,
    stdio: ["ignore", "pipe", "pipe"],
  });

  let stderrBuf = "";
  proxy.stderr.on("data", (d) => {
    stderrBuf += d.toString();
    process.stderr.write(d);
  });

  await new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error("Proxy timeout 15s")), 15000);
    proxy.stdout.on("data", (d) => {
      if (d.toString().includes("PROXY_READY")) {
        clearTimeout(t);
        resolve();
      }
    });
    proxy.on("exit", (code, sig) => reject(new Error(`Proxy exit code=${code} sig=${sig}`)));
  });

  log("プロキシ起動OK");

  // Anthropic形式でリクエスト（Claude Code が送る形式）
  const body = JSON.stringify({
    messages: [{ role: "user", content: [{ type: "text", text: "1+1=? 数字のみで答えて" }] }],
    max_tokens: 80,
    stream: false,
  });

  const result = await new Promise((resolve) => {
    const req = http.request(
      {
        host: "127.0.0.1",
        port: PORT,
        path: "/v1/messages",
        method: "POST",
        headers: { "Content-Type": "application/json", "x-model": MODEL },
      },
      (res) => {
        let buf = "";
        res.on("data", (c) => (buf += c));
        res.on("end", () => resolve({ status: res.statusCode, body: buf }));
      }
    );
    req.on("error", (e) => resolve({ status: 0, error: e.message }));
    req.write(body);
    req.end();
  });

  proxy.kill();

  if (result.status !== 200) {
    log(`FAIL: HTTP ${result.status}`);
    try {
      const j = JSON.parse(result.body || "{}");
      log(`Error: ${JSON.stringify(j.error || j, null, 2)}`);
      if (j.hint) log(`Hint: ${j.hint}`);
    } catch {
      log(result.body || result.error || "");
    }
    if (stderrBuf) log(`stderr: ${stderrBuf.slice(-500)}`);
    process.exit(1);
  }

  try {
    const j = JSON.parse(result.body);
    const content = j.content?.[0]?.text || "";
    if (!content || content.length < 1) {
      log("FAIL: 応答内容が空です");
      process.exit(1);
    }
    log(`OK: 応答取得成功 (${content.length} chars)`);
    log(`内容: ${content.substring(0, 150)}`);
    log("--- バックテスト完了: Ollama ローカルモデル 動作確認OK ---");
    process.exit(0);
  } catch (e) {
    log(`FAIL: パースエラー ${e.message}`);
    process.exit(1);
  }
}

run().catch((e) => {
  log(`FAIL: ${e.message}`);
  process.exit(1);
});
