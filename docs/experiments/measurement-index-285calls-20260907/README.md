# 285 次 Codex CLI 執行：如何讀用量索引

[完整 index.json](index.json)是已結束批次的固定索引；[manifest.json](manifest.json)指定了哪些來源納入。新增這份說明不更改原始呼叫或索引。

本批合計讀最外層：calls = 285，known_usage_calls = 277，unknown_usage_calls = 8；known_usage_subtotal.total_tokens = 42,623,631。pricing.known_usage_standard_short_subtotal_usd = 96.06783308；它是 2026-09-06 公開費率假設下的已知 API 等值，不是帳單。

pricing.rate_source 保留先前索引的完整來源快照，內含舊批次的 182 次範圍、3 次未知與 US$36.10703888 等歷史欄位。這些只作來源追溯，不能當成本批總量；本批數量、金額及未知範圍以最外層欄位為準。價格參數是 rate_source.standard_short_rates，不把舊小計當費率。

本索引不含 Fable 遭政策拒絕的嘗試；不可把未取得的用量或費用填成零。一個 CLI 執行可包含多輪模型往返，285 不是 API 請求數。input 已含 cached，output 已含 reasoning；未知用量不計為零。呼叫秒數相加含並行，區間聯集排除空檔，兩者都不是整場純工作工時。主線／原生代理另有快照，未藏在這份索引裡。

[人可讀的結論與已知限制](../RESULTS-20260907.md)
