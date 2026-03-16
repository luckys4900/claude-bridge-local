/**
 * Anthropic API → OpenAI-compatible proxy
 * Supports: Ollama (local) / OpenRouter (cloud)
 */
import http from "http";
import https from "https";
import { readFileSync, promises as fsp } from "fs";
import { fileURLToPath } from "url";
import path from "path";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// ─── config ────────────────────────────────────────────────────────────────
const cfg = JSON.parse(readFileSync(path.join(__dirname, "config.json"), "utf8"));

const MODE           = process.env.PROXY_MODE || "openrouter"; // "openrouter" | "ollama" | "glm"
const PORT           = parseInt(process.env.PROXY_PORT || "9099");
const OLLAMA_BASE    = "http://127.0.0.1:11434"; // changed from localhost to avoid IPv6 resolution issues
const OR_KEY         = cfg.openrouter_key;
const OR_BASE        = "https://openrouter.ai/api/v1";
const GLM_KEY        = cfg.glm_key || cfg.glm_zai_key || "";
const GLM_USE_CODING = cfg.glm_use_coding_plan === true || !!cfg.glm_zai_key;
// GLM Coding Plan (Z.ai): サブスクリプションクォータを使用。open.bigmodel.cn は残高チャージ方式
const GLM_BASE       = GLM_USE_CODING ? "https://api.z.ai/api/coding/paas/v4" : "https://open.bigmodel.cn/api/paas/v4";
const MODEL          = process.env.OLLAMA_MODEL || "llama3.2:latest";

// ─── simple text memory (per-repo, global) ─────────────────────────────────
const MEMORY_DIR         = path.join(__dirname, ".memory");
const MEMORY_MAX_SESSIONS = 10;       // 直近何セッション分を見るか
const MEMORY_MAX_CHARS    = 4000;     // System に埋め込む最大文字数

async function appendMemory(body, model) {
  try {
    await fsp.mkdir(MEMORY_DIR, { recursive: true });
    const day = new Date().toISOString().slice(0, 10);
    const file = path.join(MEMORY_DIR, `history-${day}.jsonl`);
    const entry = {
      ts: new Date().toISOString(),
      model,
      system: body.system || null,
      messages: body.messages || []
    };
    await fsp.appendFile(file, JSON.stringify(entry) + "\n", "utf8");
  } catch (e) {
    // ログ保存失敗は致命的ではないので stderr にだけ出す
    process.stderr.write(`[memory] append failed: ${e.message}\n`);
  }
}

async function loadMemorySummary() {
  try {
    await fsp.mkdir(MEMORY_DIR, { recursive: true });
    const files = (await fsp.readdir(MEMORY_DIR))
      .filter(f => f.startsWith("history-") && f.endsWith(".jsonl"))
      .sort(); // 古い日付 → 新しい日付
    if (!files.length) return "";

    const recent = files.slice(-3); // 直近数日分だけ読む
    const sessions = [];
    for (const f of recent) {
      const full = path.join(MEMORY_DIR, f);
      const txt = await fsp.readFile(full, "utf8");
      for (const line of txt.split("\n")) {
        if (!line.trim()) continue;
        try {
          sessions.push(JSON.parse(line));
        } catch {
          // ignore bad line
        }
      }
    }
    if (!sessions.length) return "";

    const recentSessions = sessions.slice(-MEMORY_MAX_SESSIONS);
    const parts = [];
    for (const s of recentSessions) {
      const time = s.ts || "";
      const msgs = s.messages || [];
      const summaryPieces = [];
      for (const m of msgs) {
        if (!m || !m.role) continue;
        if (typeof m.content === "string") {
          const trimmed = m.content.trim();
          if (!trimmed) continue;
          summaryPieces.push(`[${m.role}] ${trimmed}`);
        } else if (Array.isArray(m.content)) {
          const texts = m.content
            .filter(b => b.type === "text")
            .map(b => (b.text || "").trim())
            .filter(Boolean);
          if (texts.length) {
            summaryPieces.push(`[${m.role}] ${texts.join(" ")}`);
          }
        }
      }
      if (summaryPieces.length) {
        parts.push(`- (${time})\n` + summaryPieces.join("\n"));
      }
    }
    let joined = parts.join("\n\n");
    if (joined.length > MEMORY_MAX_CHARS) {
      joined = joined.slice(-MEMORY_MAX_CHARS);
    }
    if (!joined) return "";

    return [
      "過去の重要な会話メモ（要約）:",
      joined,
      "上記は直近のやり取り抜粋です。矛盾がある場合は、最新のユーザー指示を最優先してください。"
    ].join("\n\n");
  } catch (e) {
    process.stderr.write(`[memory] load failed: ${e.message}\n`);
    return "";
  }
}

// GLM model alias: 非公式名 → 智谱公式モデル名 (1211エラー回避)
const GLM_MODEL_ALIAS = {
  "glm-4.7-flash": "glm-4.7-flash",  // Coding Plan 無制限枠 (推奨)
  "glm-4.7-flashx": "glm-4.7-flashx", // 軽量高速版
  "glm-4-flash": "glm-4.7-flash"      // 互換用
};


// ─── format conversion ─────────────────────────────────────────────────────
function toOpenAIMessages(body, memoryText) {
  const msgs = [];
  const jpInstruction = "\n\nCRITICAL INSTRUCTION: You must ALWAYS respond in Japanese. 必ず日本語で回答してください。";
  if (body.system) {
    const text = typeof body.system === "string"
      ? body.system
      : body.system.filter(b => b.type === "text").map(b => b.text).join("\n");
    const withMemory = memoryText
      ? `${memoryText}\n\n---\n\n${text}`
      : text;
    msgs.push({ role: "system", content: withMemory + jpInstruction });
  } else {
    const base = memoryText
      ? `${memoryText}\n\n---\n\n${jpInstruction.trim()}`
      : jpInstruction.trim();
    msgs.push({ role: "system", content: base });
  }
  for (const m of body.messages || []) {
    if (m.role === "user") {
      if (typeof m.content === "string") {
        msgs.push({ role: "user", content: m.content });
      } else {
        let textParts = [];
        for (const b of m.content) {
          if (b.type === "text") {
            textParts.push(b.text);
          } else if (b.type === "tool_result") {
            if (textParts.length > 0) {
              msgs.push({ role: "user", content: textParts.join("\n") });
              textParts = [];
            }
            let trContent = "";
            if (typeof b.content === "string") {
              trContent = b.content;
            } else if (Array.isArray(b.content)) {
              trContent = b.content.map(c => c.type === "text" ? c.text : JSON.stringify(c)).join("\n");
            } else {
              trContent = JSON.stringify(b.content);
            }
            if (!trContent) trContent = "Success";
            msgs.push({
              role: "tool",
              tool_call_id: b.tool_use_id,
              content: trContent
            });
          }
        }
        if (textParts.length > 0) {
          msgs.push({ role: "user", content: textParts.join("\n") });
        }
      }
    } else if (m.role === "assistant") {
      let content = "";
      const tool_calls = [];
      if (typeof m.content === "string") {
        content = m.content;
      } else {
        for (const b of m.content) {
          if (b.type === "text")     content += b.text;
          if (b.type === "tool_use") tool_calls.push({
            id: b.id, type: "function",
            function: { name: b.name, arguments: JSON.stringify(b.input || {}) }
          });
        }
      }
      const msg = { role: "assistant", content };
      if (tool_calls.length) msg.tool_calls = tool_calls;
      msgs.push(msg);
    }
  }
  return msgs;
}

function buildRequest(body, model, memoryText) {
  const req = {
    model,
    messages: toOpenAIMessages(body, memoryText),
    stream: body.stream === true,
  };
  if (body.max_tokens) req.max_tokens = body.max_tokens;
  if (body.tools?.length) {
    req.tools = body.tools.map(t => ({
      type: "function",
      function: { name: t.name, description: t.description || "", parameters: t.input_schema || {} }
    }));
  }
  return req;
}

// ─── upstream fetch ────────────────────────────────────────────────────────
async function callUpstream(body, model, memoryText) {
  if (MODE === "openrouter") {
    return fetch(`${OR_BASE}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${OR_KEY}`,
        "HTTP-Referer": "https://claude-bridge-local",
        "X-Title": "Claude Bridge Local",
      },
      body: JSON.stringify(buildRequest(body, model, memoryText)),
    });
  } else if (MODE === "glm") {
    const resolvedModel = GLM_MODEL_ALIAS[model] || model;
    if (!GLM_KEY) {
      process.stderr.write("[GLM] glm_key not set in config.json\n");
    }
    const headers = {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${GLM_KEY}`,
    };
    if (GLM_USE_CODING) {
      headers["Accept-Language"] = "en-US,en";
    }
    return fetch(`${GLM_BASE}/chat/completions`, {
      method: "POST",
      headers,
      body: JSON.stringify(buildRequest(body, resolvedModel, memoryText)),
    });
  } else {
    // Ollama local
    return fetch(`${OLLAMA_BASE}/v1/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": "Bearer dummy" },
      body: JSON.stringify(buildRequest(body, model, memoryText)),
    });
  }
}

// ─── SSE streaming ─────────────────────────────────────────────────────────
function sse(res, event, data) {
  res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
}

async function streamResponse(upstreamResp, res) {
  const msgId = "msg_" + Math.random().toString(36).slice(2);
  sse(res, "message_start", {
    type: "message_start",
    message: { id: msgId, type: "message", role: "assistant", content: [],
      model: "claude-sonnet-4-6", stop_reason: null, stop_sequence: null,
      usage: { input_tokens: 1, output_tokens: 1 } }
  });
  sse(res, "content_block_start", { type: "content_block_start", index: 0, content_block: { type: "text", text: "" } });
  sse(res, "ping", { type: "ping" });

  const decoder = new TextDecoder();
  const reader  = upstreamResp.body.getReader();
  let   buf     = "";
  const toolCalls = {};
  let   hasFinished = false;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const lines = buf.split("\n");
    buf = lines.pop();

    for (const line of lines) {
      // Handle both "data: {...}" and "data:{...}" (GLM uses no space)
      let raw;
      if (line.startsWith("data: ")) raw = line.slice(6).trim();
      else if (line.startsWith("data:")) raw = line.slice(5).trim();
      else raw = line.trim();
      if (!raw || raw === "[DONE]") continue;
      let chunk;
      try { chunk = JSON.parse(raw); } catch { continue; }

      const delta  = chunk.choices?.[0]?.delta;
      const finish = chunk.choices?.[0]?.finish_reason;

      // Always process content delta first (GLM may send content + finish in same chunk)
      if (delta?.content != null && !hasFinished) {
        sse(res, "content_block_delta", {
          type: "content_block_delta", index: 0,
          delta: { type: "text_delta", text: delta.content }
        });
      }
      // Support for reasoning models if they send reasoning_content (like GLM-4.7-Flash)
      if (delta?.reasoning_content != null && !hasFinished) {
        sse(res, "content_block_delta", {
          type: "content_block_delta", index: 0,
          delta: { type: "text_delta", text: delta.reasoning_content }
        });
      }
      if (delta?.tool_calls) {
        for (const tc of delta.tool_calls) {
          const i = tc.index ?? 0;
          if (!toolCalls[i]) toolCalls[i] = { id: tc.id || `toolu_${i}`, name: "", args: "" };
          if (tc.function?.name)      toolCalls[i].name += tc.function.name;
          if (tc.function?.arguments) toolCalls[i].args += tc.function.arguments;
        }
      }
      // Only finish if finish_reason is a valid terminal string (not null/undefined)
      if (finish && !hasFinished) {
        hasFinished = true;
        sse(res, "content_block_stop", { type: "content_block_stop", index: 0 });
        let idx = 1;
        for (const tc of Object.values(toolCalls)) {
          sse(res, "content_block_start", {
            type: "content_block_start", index: idx,
            content_block: { type: "tool_use", id: tc.id, name: tc.name, input: {} }
          });
          sse(res, "content_block_delta", {
            type: "content_block_delta", index: idx,
            delta: { type: "input_json_delta", partial_json: tc.args }
          });
          sse(res, "content_block_stop", { type: "content_block_stop", index: idx });
          idx++;
        }
        const stopReason = finish === "tool_calls" ? "tool_use" : "end_turn";
        sse(res, "message_delta", {
          type: "message_delta",
          delta: { stop_reason: stopReason, stop_sequence: null },
          usage: { output_tokens: 10 }
        });
        sse(res, "message_stop", { type: "message_stop" });
      }
    }
  }
  res.end();
}

// ─── HTTP server ───────────────────────────────────────────────────────────
async function handleMessages(req, res, model) {
  let raw = "";
  for await (const chunk of req) raw += chunk;
  const body = JSON.parse(raw);

  // simple text memory: load summary and log this request (fire-and-forget)
  const memoryText = await loadMemorySummary();
  appendMemory(body, model).catch(() => {});

  let upstreamResp;
  try {
    upstreamResp = await callUpstream(body, model, memoryText);
  } catch (e) {
    process.stderr.write(`[upstream] ${e.message}\n`);
    if (MODE === "ollama" && (e.cause?.code === "ECONNREFUSED" || /fetch|ECONNREFUSED|connect/i.test(String(e.message)))) {
      res.writeHead(502);
      res.end(JSON.stringify({
        error: "Ollama connection failed",
        hint: "Ollama is not running. Start Ollama app or run 'ollama serve' in terminal.",
      }));
      return;
    }
    if (!res.headersSent) { res.writeHead(500); res.end(JSON.stringify({ error: e.message })); }
    return;
  }

  if (!upstreamResp.ok) {
    const err = await upstreamResp.text();
    process.stderr.write(`[upstream error] ${upstreamResp.status}: ${err}\n`);
    let errObj = { error: err };
    try {
      const parsed = JSON.parse(err);
      if (parsed.error?.code) {
        const code = parsed.error.code;
        const msg = parsed.error.message || "";
        if (["1113", "1308", "1309", "1310"].includes(String(code))) {
          errObj.hint = MODE === "glm" && !GLM_USE_CODING
            ? "GLM Coding Plan契約時は config.json に glm_use_coding_plan: true を追加し、Z.ai エンドポイントを使用"
            : "トークン/クォータ不足。智谱: https://open.bigmodel.cn / Z.ai: https://z.ai/manage-apikey/subscription";
        } else if (code === "1211") {
          errObj.hint = "モデルが存在しません。glm-4.7, glm-4.7-flashx, glm-4.7-flash を確認";

        } else if (["1002", "1003", "1004"].includes(String(code))) {
          errObj.hint = "APIキーが無効または期限切れ。config.json の glm_key を確認";
        }
      }
    } catch (_) {}
    if (MODE === "ollama" && !errObj.hint) {
      errObj.hint = `Model may not exist. Run: ollama pull ${model}`;
    }
    res.writeHead(502); res.end(JSON.stringify(errObj));
    return;
  }

  if (body.stream !== false) {
    res.writeHead(200, { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" });
    await streamResponse(upstreamResp, res);
  } else {
    const data = await upstreamResp.json();
    const msg = data.choices?.[0]?.message || {};
    const text = msg.content || msg.reasoning || msg.reasoning_content || "";
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({
      id: "msg_" + Math.random().toString(36).slice(2),
      type: "message", role: "assistant",
      content: [{ type: "text", text }],
      model: "claude-sonnet-4-6",
      stop_reason: "end_turn", stop_sequence: null,
      usage: { input_tokens: 10, output_tokens: 10 }
    }));
  }
}

const server = http.createServer(async (req, res) => {
  const model = req.headers["x-model"] || MODEL;
  try {
    if (req.method === "POST" && req.url.startsWith("/v1/messages")) {
      await handleMessages(req, res, model);
    } else {
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end("{}");
    }
  } catch (e) {
    process.stderr.write("Proxy error: " + e.message + "\n");
    if (!res.headersSent) { res.writeHead(500); res.end("{}"); }
  }
});

server.listen(PORT, "127.0.0.1", () => {
  if (MODE === "glm") {
    process.stderr.write(`[GLM] ${GLM_USE_CODING ? "Z.ai Coding API" : "open.bigmodel.cn"}: ${GLM_BASE}\n`);
  }
  process.stdout.write(`PROXY_READY:${PORT}\n`);
});
