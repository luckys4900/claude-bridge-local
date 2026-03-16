/**
 * Direct test of Ollama API
 */
import http from "http";

const body = JSON.stringify({
  model: "qwen3:8b",
  messages: [{ role: "user", content: "1+1=? Answer with number only" }],
  stream: false,
});

const req = http.request(
  {
    host: "127.0.0.1",
    port: 11434,
    path: "/v1/chat/completions",
    method: "POST",
    headers: { "Content-Type": "application/json" },
  },
  (res) => {
    let buf = "";
    res.on("data", (c) => (buf += c));
    res.on("end", () => {
      console.log(`Status: ${res.statusCode}`);
      console.log(`Response: ${buf.substring(0, 500)}`);
      try {
        const j = JSON.parse(buf);
        const content = j.choices?.[0]?.message?.content;
        console.log(`Content: ${content}`);
      } catch {}
    });
  }
);
req.on("error", (e) => console.error("Error:", e.message));
req.write(body);
req.end();
