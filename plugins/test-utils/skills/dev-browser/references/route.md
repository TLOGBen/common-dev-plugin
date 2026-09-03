# 受測站台 Route Index（路由索引）

> 各專案在此記錄自己的路由地圖，讓 agent 導覽時不必猜路徑。
> 請將下方表格中的 placeholder 與範例路由替換成你自己專案的實際值。
> 完整路由定義通常位於前端的 router 設定（例：`src/router/config/routes*.js`）。

## Environment（環境）

| Item | URL |
|------|-----|
| 前端 dev server | `http://localhost:3000` |
| 後端 API | `http://localhost:8080` |
| 前端 base path | `/` |

---

## Common Module（範例模組，請替換成你自己的模組）

> 以下為示意用的範例路由，請改成你專案實際的功能與路徑。

| Feature | Path |
|---------|------|
| Login | `/login` |
| List page（登入後預設頁，範例） | `/app/list` |
| Detail page（範例） | `/app/detail` |

---

> 簽核／審核頁通常是從清單頁點擊進入的，其 URL 多半帶有 `id`、`applyNo` 之類的 route param。
> 若你的專案有多個模組，可比照上方表格各自新增一個區塊。
