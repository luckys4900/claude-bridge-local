/**
 * GLM API 接続テスト
 * Usage: node test_glm.mjs [model] [--zai]
 *   model: glm-4.7-flashx | glm-4.7 | glm-4-flash-250414 (default: glm-4.7-flashx)
 *   --zai: Z.ai Coding API を使用 (GLM Coding Plan 契約時)
 */
import { readFileSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const cfg = JSON.parse(readFileSync(path.join(__dirname, "config.json"), "utf8"));
const useZai = process.argv.includes("--zai") || cfg.glm_use_coding_plan === true;
const GLM_KEY = (useZai ? cfg.glm_zai_key : null) || cfg.glm_key || "";
const GLM_BASE = useZai ? "https://api.z.ai/api/coding/paas/v4" : "https://open.bigmodel.cn/api/paas/v4";
const defaultModel = useZai ? "glm-4.7" : "glm-4.7-flashx";
const model = process.argv.filter(a => !a.startsWith("-")).slice(2)[0] || defaultModel;

async function test() {
  if (!GLM_KEY) {
    console.error("[ERROR] config.json に glm_key が設定されていません");
    process.exit(1);
  }
  console.log(`[TEST] GLM API: model=${model}, endpoint=${useZai ? "Z.ai Coding" : "open.bigmodel.cn"}`);
  const res = await fetch(`${GLM_BASE}/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${GLM_KEY}`,
      ...(useZai && { "Accept-Language": "en-US,en" }),
    },
    body: JSON.stringify({
      model,
      messages: [{ role: "user", content: "こんにちは。1+1は?" }],
      max_tokens: 50,
      stream: false,
    }),
  });
  const text = await res.text();
  if (!res.ok) {
    console.error(`[FAIL] HTTP ${res.status}`);
    try {
      const j = JSON.parse(text);
      console.error("Error:", JSON.stringify(j, null, 2));
      if (j.error?.code === "1211") console.error("→ モデルが存在しません。正しいモデル名を確認してください");
      if (j.error?.code === "1113") {
        console.error("→ 1113: 残高不足またはクォータ超過");
        if (useZai) console.error("  Coding Plan時は glm-4.7 を試す: node test_glm.mjs glm-4.7 --zai");
      }
      if (j.error?.code === "1308" || j.error?.code === "1309") console.error("→ クォータ制限。プラン確認またはリセット待ち");
    } catch {
      console.error(text);
    }
    process.exit(1);
  }
  try {
    const j = JSON.parse(text);
    const msg = j.choices?.[0]?.message ?? j.data?.choices?.[0]?.message ?? {};
    const content = msg.content || msg.reasoning_content || "(empty)";
    console.log("[OK] Response:", String(content).substring(0, 300) || "(empty)");
    process.exit(0);
  } catch {
    console.error("[FAIL] Parse error:", text.substring(0, 300));
    process.exit(1);
  }
}
test();
