# 彰化秀傳麻醉備物溝通看板

> 麻醉醫師 OR 內部備物溝通工具（prototype）

## 🩺 它在做什麼

麻醉醫師看完 HIS data 之後，用最少點擊把當天的 case 與止痛 / 麻醉備物需求登錄上看板，讓護理師可以一眼看到清楚的備物摘要，減少口頭交班遺漏。

**僅供彰化秀傳麻醉科 OR 內部備物溝通，不作為正式醫囑或病歷紀錄。實際藥物、劑量、濃度與給藥仍以麻醉醫師現場確認與院內規範為準。**

## 🚀 試玩

線上版（GitHub Pages，手機 / 平板 / 醫院電腦皆可開）：

👉 **<https://jenniferliang813-netizen.github.io/anesthesia-prep-board/>**

或下載 [`麻醉備物溝通看板.html`](麻醉備物溝通看板.html) 雙擊在瀏覽器打開即可，不需安裝任何東西。

### 建議試玩流程（給麻醫）

1. 上方點「白班前段」/「白班後段」/「值班」切換房間範圍
2. 點 Room → 第幾台 → 科別 → 術式
3. 試試選 **CS → Lobectomy**，看看「特殊提醒」是不是自動帶入 `需 A-line`、`需 DLT`、`ICU postop`
4. 勾「困難 airway」，看看是不是自動連動勾「需 FOB」
5. 試試開 Nerve block，填配方、稀釋液、抽幾隻
6. 按「送出到看板」→ 切到「📊 看板」分頁，看臨床語句呈現
7. 卡片上可一鍵切狀態、跳房、編輯、刪除

## 💡 已實作功能

- 班別篩選（白班前段 / 白班後段 / 值班），記憶最後選擇
- Room / 第幾台 / 年齡性別 / 科別術式 / 麻醉方式
- **Airway 備物**：LMA、Non-kinking endo、鼻管
- **止痛備物**：Nerve block（含每隻配方 / 稀釋液 / 抽幾隻臨床語意）、Testing syringe、Spinal morphine、Dynastat、Acetamol、Epidural PCA、IVPCA
- **特殊提醒**：高風險、尚未麻評、困難 airway、需 A-line / CVC / DLT / VL / FOB / 粗 line、ICU postop、術後呼吸器
- **術式自動帶入備物**（隱形預填，不要的可手動點掉）：例如 Lobectomy → A-line + DLT + ICU postop
- **跨欄位連動**：勾困難 airway → 自動補勾需 FOB
- Hx、Data 完整保留，看板上預設摺疊
- 跳房 modal：`⚠️ R5 → R8`
- 「✓ 已評估」一鍵清「尚未麻評」
- 編輯 = 重開表單預填全部內容
- CSV 匯出（含全部備物欄位）

## 🔒 資安設計

- **不輸入病人姓名、病歷號、身分證、完整 lab / HIS data**
- 不串接 HIS，純前端
- 所有資料存在瀏覽器 localStorage，**每日 23:59 自動清除**
- 隔天打開若日期不對，也會自動清除前一天資料
- 不會傳到任何伺服器；換瀏覽器 / 換裝置看不到別人輸入的內容
- 備註欄限制 80 字，並標註「請勿輸入姓名、病歷號或完整病歷內容」

## 📝 第一版限制（不做）

- HIS 串接
- 登入系統
- 原生手機 App
- 護理師備物進度追蹤
- 病人姓名 / 病歷號 / 完整 lab
- PCA 詳細配方
- Spinal morphine 劑量
- 複雜統計 dashboard

## 💬 回饋

歡迎麻醫、護理長提供使用心得：哪些欄位多餘、哪些缺漏、術式對應的預設備物應該調整、UI 是否易讀、按鈕順序⋯⋯

回饋管道：（請自行補上：LINE / Email / GitHub Issues）

## 🛠 技術筆記

- 純單檔 HTML + 原生 JS，無框架、無 build step
- 資料持久化：localStorage
- 不引入任何外部 CDN
- 所有 user 輸入皆以 `textContent` 顯示，無 innerHTML 注入風險

## 📁 檔案說明

| 檔名 | 用途 |
|---|---|
| `麻醉備物溝通看板.html` | 主程式（單檔，雙擊即可開） |
| `index.html` | GitHub Pages 入口（自動跳轉到主程式） |
| `anesthesia_prep_board_claude_handoff.md` | 開發規格交班文件 |
| `archive/蛙蛙設計.html` | 早期 prototype（封存，作對照用） |
