#!/usr/bin/env node
// 從 element-table.js 產出的編號表裡，請 TypeSafe Jev 挑出最符合目標的元素（Lab）
// 完整說明：references/case-jev-pick.md
//
// 用法：node jev-pick.mjs "<要找的元素／要做的事>" [elements.json 路徑] [--top N]
// 需要環境變數 TYPESAFE_API_KEY。沒有金鑰或 API 失敗時 exit 2，agent 改用 snapshotForAI 自行判讀。
//
// Jev 的答案只是候選，不是證據：拿 [data-jev-idx="N"] 操作後仍要看畫面／DOM 驗證結果。
import { readFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";

const LOW_CONFIDENCE = 0.5;

const args = process.argv.slice(2);
const topIdx = args.indexOf("--top");
const top = topIdx >= 0 ? Number(args.splice(topIdx, 2)[1]) || 3 : 3;
const [goal, file = join(homedir(), ".dev-browser", "tmp", "elements.json")] = args;

const fallback = (why) => {
  console.error(`jev-pick 無結果：${why}\n→ 改用 page.snapshotForAI() 自行判讀。`);
  process.exit(2);
};

if (!goal) fallback('缺少目標描述。用法：node jev-pick.mjs "<要找的元素>" [elements.json]');
const key = process.env.TYPESAFE_API_KEY;
if (!key) fallback("未設定 TYPESAFE_API_KEY");

let table;
try {
  table = JSON.parse(readFileSync(file, "utf8"));
} catch (e) {
  fallback(`讀不到 ${file}（先跑 element-table.js）：${e.message}`);
}
if (!table.elements?.length) fallback("編號表是空的：頁面上沒有看得到的可操作元素");

const line = (e) => `[${e.idx}] ${e.role} ${e.name}${e.value ? " · " + e.value : ""}${e.disabled ? " (disabled)" : ""}`;
const criteria = Object.fromEntries(table.elements.map((e) => [`e${e.idx}`, line(e)]));
criteria.none = "以上都不符合";

const questions = {
  target: {
    type: "choice",
    instructions: `在這個頁面上，要完成「${goal}」應該操作哪一個元素？`,
    criteria,
  },
};
const state = `頁面：${table.title}\n網址：${table.url}\n\n可操作元素：\n${table.elements.map(line).join("\n")}`;

const t0 = performance.now();
let res, body;
try {
  res = await fetch("https://api.typesafe.ai/v1/systemone", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: "jev-latest", state, questions }),
    signal: AbortSignal.timeout(10_000),
  });
  body = await res.text();
} catch (e) {
  fallback(`呼叫 Jev 失敗：${e.message}`);
}
const ms = Math.round(performance.now() - t0);
if (!res.ok) fallback(`HTTP ${res.status}（${ms}ms）${body.slice(0, 300)}`);

const answer = JSON.parse(body).answers.target;
const ranked = Object.entries(answer.probabilities).sort((a, b) => b[1] - a[1]).slice(0, top);
const byKey = Object.fromEntries(table.elements.map((e) => [`e${e.idx}`, e]));
const pct = (p) => `${(p * 100).toFixed(1)}%`;

console.log(`目標：${goal}`);
console.log(`頁面：${table.title}（編號表擷取於 ${table.capturedAt}）`);
for (const [k, p] of ranked) {
  const e = byKey[k];
  console.log(e ? `${pct(p)}  ${line(e)}  → page.locator('[data-jev-idx="${e.idx}"]')` : `${pct(p)}  none（以上都不符合）`);
}
console.log(`confidence ${pct(answer.confidence)}｜來回 ${ms}ms`);
if (answer.choice === "none" || answer.confidence < LOW_CONFIDENCE) {
  console.log("⚠️ 低信心或無符合元素 → 不要照單操作，改用 snapshotForAI 自行判讀。");
}
