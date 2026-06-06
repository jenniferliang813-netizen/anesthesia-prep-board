# 🤖 Claude 交班單｜麻醉 OP Checklist（個人記錄版）

> 給未來 Claude session 接手用。**讀完這份，你就能單獨改動或延伸這個 OP Checklist，不需要去看備物看板的交班單。**
> 這是一個**獨立產品**，和同 repo 內的「麻醉備物溝通看板」共用「部分邏輯」但**檔案各自獨立、互不影響**。

---

## 0. 最重要的一句話（先讀這段）

**這個資料夾 `OP checklist/` 是一個獨立 app，跟上一層的備物看板是兩回事。**
- 改這裡（`OP checklist/index.html`）**不會、也不應該**動到 `../麻醉備物溝通看板.html`、`../board/`、`../護理師看板-本機版.html`、`../交班單-Claude.md`。
- 兩者有相同的部分邏輯（房間班別、科別術式對照、看板排序、跳房、每日 23:59 清空、`textContent` 防 XSS、配色）——但那是**當初複製過來各自維護**，不是共用檔案。改一邊不會同步到另一邊，也**不要**去做成共用。
- 例外：部署用的 `netlify.toml` 是**整個 repo 共用的、放在上一層（repo 根）**。要改網址路徑才會動它（見第 8 節）。

---

## 1. 這是什麼 / 不是什麼

彰化秀傳麻醉科醫師（梁庭瑋）的**個人** OP checklist 記錄工具。麻醉醫師在自己手機上，把今天每一台刀的重點（科別、術式、麻醉方式、自費項目、特殊提醒、病史、異常數據…）快速點一點記下來，在看板上一覽今天的進度。

- **是**：個人記錄、提醒、當天交接自己看的小工具。單檔 HTML、**純本機**（資料只存這支手機的瀏覽器 localStorage）。
- **不是**：病歷、醫囑、HIS 串接、跨裝置同步、和護理師的溝通工具。**不收完整個資**（姓氏 OK 供自行辨認，但禁止全名 / 病歷號 / 身分證 / 完整 lab）。

使用者是醫師、**不是工程師**，但能跑簡單 Git/CLI。**對話一律用中文，先問再動手**（她改需求很頻繁）。

---

## 2. 線上網址

| 用途 | 網址 |
|---|---|
| OP Checklist（主力，醫院內網 / 手機 4G 都可開） | https://anesthesia-prep-board.netlify.app/checklist |

- 走的是 repo 根 `netlify.toml` 的 rewrite：`/checklist` → `/OP checklist/index.html`（status 200）。
- 醫院封 `*.github.io`，所以**主力是 Netlify**。push 到 GitHub `main`，Netlify 約 30–60 秒 auto-deploy。
- ⚠️ 因為 `/checklist` 是 rewrite（網址列顯示 `/checklist`，實體檔在 `/OP checklist/`），**頁面內引用圖示 / manifest 一律用絕對路徑** `/OP%20checklist/...`（空白要 encode 成 `%20`）。用相對路徑會抓到 `/icons/...` 而 404。

---

## 3. 檔案結構（都在 `OP checklist/` 內）

```
OP checklist/
├── index.html              ← 主程式（唯一的 app 檔，單檔 HTML + 原生 JS，純本機）
├── manifest.webmanifest    ← PWA manifest（加到主畫面用，standalone、start_url=/checklist）
├── _build_icon.py          ← 由 icons/source.png 母圖產生各尺寸圖示的腳本（改圖示重跑這支）
├── icons/
│   ├── source.png          ← 圖示母圖（1254×1254，使用者提供的「麻醉面罩＋查核板」設計）
│   ├── icon-512.png        ← 512×512（Android / PWA）  ← 由腳本產生，勿手改
│   ├── icon-192.png        ← 192×192（Android / PWA）  ← 同上
│   ├── apple-touch-icon.png← 180×180（iOS 主畫面）      ← 同上
│   └── favicon-32.png      ← 32×32（瀏覽器分頁）        ← 同上
└── 交班單-OPchecklist.md   ← 本檔

# 上一層（repo 根，跟備物看板共用，會用到的只有這個）：
../netlify.toml             ← 含 /checklist → OP checklist/index.html 的 rewrite
```

**沒有 build step**：`index.html` 直接被 Netlify 服務。唯一的「產生物」是圖示（`_build_icon.py` 產生），其餘手寫即所得。

---

## 4. 技術架構

```
┌─────────────────────────────────────────────┐
│  手機瀏覽器（Safari / Chrome）                │
│  ├── Vanilla JS（普通 <script>，非 module）   │
│  └── localStorage（唯一資料來源，前綴 opChecklist_）│
└─────────────────────────────────────────────┘
        ↑ 純靜態檔，git push 後由 Netlify 服務
        └── 沒有後端、沒有資料庫、沒有 Firebase、沒有任何外部 API 呼叫
```

- **和備物看板最大的差別：這版完全沒有 Firebase / 雲端 / websocket / 輪詢。** 資料不出這支手機。
- 沒有護理師看板、沒有本機離線版（不需要，因為它本身就是純本機）。

---

## 5. 資料 Schema（一筆 case 的 patient object）

存在 `localStorage['opChecklist_patients']`，是一個 array，每筆：

```js
{
  id: 1717033200000,        // Date.now()，唯一鍵
  date: "2026-06-06",       // 用於每日過期清除
  roomGroup: "day_front",   // 'day_front' | 'day_back' | 'duty'（送出當下的班別）
  originalRoom: "5",        // 原指定房
  currentRoom: "5",         // 目前房（跳房後不同）
  turn: "第2台",            // 第1~4台 / 急診插入 / 其他（自填字串）
  surname: "王",            // 病人姓氏（辨認用，勿存全名）★本版新增
  age: "62",                // 字串，最多 3 字
  gender: "M",              // 'M' | 'F' | ''
  dept: "CS",               // 科別 key，見 OP_MAPPING
  op: "Lobectomy",          // 術式（預設按鈕或自填）
  anes: "GA",               // GA | SA | IVG | EA
  selfpay: ["Suga","BIS"],  // 自費項目（多選）★本版新增
  reminders: ["未麻訪","Post OP ICU"],   // 特殊提醒（多選，只有 4 個選項）
  hx: ["HTN","其他"],       // 病史（多選，含 '其他'）
  hxOther: "裝過支架",      // hx 含 '其他' 時的自填字串 ★本版新增
  data: ["EF<40"],          // 異常數據（多選，含 '其他'）
  dataOther: "",            // data 含 '其他' 時的自填字串 ★本版新增
  memo: "...",              // 備註 ≤80 字
  status: "手術中",         // 待手術 / 手術中 / 已完成
  createdAt: 1717033200000
}
```

⚠️ **本版沒有** 備物看板那些欄位：`airway` / `monitoring` / `medications` / `analgesia`（NB 配方、Testing 針筒、PCA…）全部移除了。如果未來要加回某項「備物」，多半應該做成 `selfpay` 那種單純多選，而不是把整套配方搬回來（除非使用者明確要）。

---

## 6. 重要常數（都在 `index.html` 的 `<script>` 頂部）

```js
STORAGE_KEYS = { patients:'opChecklist_patients',
                 selectedRoomGroup:'opChecklist_selectedRoomGroup',
                 dataDate:'opChecklist_dataDate' }   // 前綴 opChecklist_，刻意和備物看板(anesthesiaPrep_)分開

ROOM_GROUPS = { day_front:{label:'白班前段',rooms:['1','2','5','6','13']},
                day_back :{label:'白班後段',rooms:['7','8','9','11','13','18']},
                duty     :{label:'值班',    rooms:['1','2','5','6','7','8','9','11','13','18']} }

OP_MAPPING = { Ortho, ENT, NS, CS, CVS, GYN, GU, PS, OS, GS, CRS, BS, OPH → 各自術式陣列 }
            // 科別排序是使用者明確要求，要動先確認。內容和備物看板目前一致（複製過來）。

REMINDER_LIST = ['高風險','未麻訪','Awake 插管','Post OP ICU']   // 只有 4 項（risk-opt 紅框樣式、多選）
SELFPAY_LIST  = ['Suga','BIS','NB','Dynastat','Acetamol','Epidural PCA','Byfavo','HFNC']  // 多選
HX_LIST       = [...病史..., '其他']    // 末項 '其他' → 跳出 hx-other 自填框
DATA_LIST     = [...數據..., '其他']    // 末項 '其他' → 跳出 data-other 自填框
ANES_LIST     = ['GA','SA','IVG','EA']  // 預設選 GA
GENDER_LIST   = ['M','F']
TURN_LIST     = ['第1台','第2台','第3台','第4台','急診插入','其他']  // '其他' → turn-custom 自填
STATUS_ORDER  = ['待手術','手術中','已完成']
```

**已從備物看板版移除、本版不存在的常數**：`OP_PRESETS`（選術式自動帶提醒）、`BLOCK_TYPES`、`DILUENTS`、備藥/止痛相關。
- `OP_PRESETS` 拿掉的原因：它原本自動帶「需 A-line / 需 DLT」等，但本版的特殊提醒只剩 4 項，帶了會帶錯。若使用者想要「選某術式自動勾 Post OP ICU」這類，可重做一個精簡版 preset。

---

## 7. 行為與邏輯（看板 / 表單）

### 送出
- `submitPatient()` **只強制選 Room**，其餘全可空就送出（使用者明確要求：欄位不必填完整）。
- 新增成功跳 alert；編輯模式（`editingId`）則更新後切到看板。

### 每日清空（與備物看板同邏輯）
- 載入時 `checkAndPurgeStaleData()`：`dataDate` 不是今天就清掉 patients。
- `scheduleNightlyPurge()`：排程到當天 23:59 清空 localStorage + 重繪。
- `resetAll()`（看板「重置全天」鈕）：手動清空（只清這支手機本機）。

### 看板排序（使用者要的邏輯，**勿改**）
`renderBoard()` 內，每間房的 case 依序：
1. **狀態**：手術中(0) → 待手術(1) → 已完成(2)（`STATUS_SORT`）
2. **台次**：第1台→第2台→第3台→第4台→急診插入（`TURN_SORT`，其餘排 99）
3. `createdAt`（早的在前）

### 看板版面：同一手術室 case 橫向排列 ★本版特性
- 每間房一個 `.room-block`，標題下是一條 `.room-cases`（`display:flex; overflow-x:auto; scroll-snap`）。
- 卡片固定寬 `280px` 並排，手機可左右滑看同房其餘台次。
- 想一次看到更多 case → 把 `.room-cases .case-card` 的 `flex/width 280px` 改小即可。

### 卡片內容順序（`renderCase()`，使用者調過，**勿任意改順序**）
1. 狀態 badge（點擊 `cycleStatus` 循環切換）
2. headline：`姓氏｜台次｜科別｜術式｜麻醉｜年齡y性別`
3. 跳房提示（`originalRoom !== currentRoom` 時顯示 ⚠️ Rx → Ry）
4. ⚠️ 特殊提醒（含「未麻訪」時，旁邊有「✓ 已評估」鈕 → `clearAnesReview` 移除未麻訪）
5. **Hx**（直接顯示、不收合；`其他` 以 `hxOther` 取代呈現）★使用者要求直接攤開
6. **Data**（同上，`dataOther`）
7. **💲 自費**（排在 Hx/Data 之後）★使用者要求的順序
8. 備註
9. actions：進入 / 完成 / 🔀跳房 / ✎編輯 / 刪除

> `buildHxList()` / `buildDataList()`：把陣列中的 `'其他'` 濾掉、改塞 `hxOther`/`dataOther` 的自填字串。

### 表單欄位順序（和看板一致）
Room → 第幾台 → 姓氏 → 年齡/性別 → 科別 → 術式 → 麻醉方式 → 特殊提醒 → Hx → Data → **自費** → 備註

### 其他
- 跳房：`openRoomChange` modal，可選班別內房間 + 原房 + 目前房。
- CSV 匯出（`exportCSV`）：欄位含 日期/班別/原房/目前房/第幾台/姓氏/年齡/性別/科別/術式/麻醉方式/自費/特殊提醒/Hx/Data/備註/手術狀態。
- 所有顯示使用者輸入的地方用 `textContent`（**禁止 `innerHTML` 塞使用者資料** — XSS 防線）。

---

## 8. Deploy 流程

```bash
# 在 repo 根 C:\Users\jenni\我的雲端硬碟\AI\手術動態看板\ 下
git add -A
git commit -m "說明這次改了什麼"
git push        # 直接推 main，單人開發，不要開 PR
```

- push 後 Netlify 約 30–60 秒 auto-deploy（同一個 Netlify 站，備物看板和 checklist 都在裡面）。
- **網址路徑** `/checklist` 定義在 repo 根 `../netlify.toml` 的 `[[redirects]]`（`/checklist` 和 `/checklist/` 兩條，status 200 rewrite 到 `/OP checklist/index.html`）。要改網址才動它。
- ⚠️ 工作目錄是 Google Drive 同步資料夾，**慎用大量 .git 操作**以免拖累 Drive sync。

---

## 9. App 圖示 / 加到手機主畫面

- `manifest.webmanifest`：`display:standalone`、`start_url:/checklist`、`theme/background_color:#1e3a5f`、icons 192/512（`purpose:"any maskable"`）。
- `index.html` `<head>` 已放 `apple-touch-icon` / `icon` / `manifest` 連結 + iOS 的 `apple-mobile-web-app-*` meta（主畫面標題顯示「OP Checklist」）。**全用絕對路徑** `/OP%20checklist/icons/...`。
- **要換圖示**：把新的正方形母圖覆蓋 `icons/source.png`（建議 ≥1024×1024、滿版背景、四角別自己切圓、主圖留約 10% 安全邊距），然後跑：
  ```
  py "OP checklist/_build_icon.py"
  ```
  會由 source.png 重產 180/192/512/32 四個尺寸（覆蓋同名檔，head/manifest 不用改）。沒有 source.png 時腳本會 fallback 用程式畫一個面罩圖。
  - Windows 上 `python` 是 Microsoft Store stub（不會動），**請用 `py`**。SVG 轉檔工具（cairosvg）沒裝且難裝；Pillow 有裝，所以走「光柵母圖縮圖」路線，不要假設能 render SVG。
- **使用者怎麼加主畫面**：iOS 用 Safari 開 `/checklist` → 分享 → 加入主畫面；Android 用 Chrome → 選單 → 加到主畫面。iOS 會快取舊圖示，換圖後要刪掉重加。

---

## 10. 使用者偏好與約束（一定要遵守）

1. **單檔 HTML + 原生 JS**，不引入框架、不引入 build step。
2. **純本機**：不要擅自加雲端 / 後端 / 外部 API（**包含不打任何 LLM API**）。要加雲端必須先問使用者，且**別和備物看板撞同一個 Firebase path**。
3. **不收個資**：姓氏 OK，但禁止全名 / 病歷號 / 身分證 / 完整 lab / HIS。
4. **使用者輸入一律 `textContent`，不可 `innerHTML`**。
5. **字體大、按鈕至少 44px**（部分使用者中高年資、視力不佳）。
6. **配色**：深灰藍 `#1e3a5f` + 鋼藍 `#3b6fa0` + 霧白，醫療專業風（CSS `:root` 變數）。
7. **`translate="no"`**：防 Chrome 把英文藥名/術式翻成中文。動 `<head>` 注意保留 `translate="no"` 與 `notranslate` meta。
8. emoji 風格可延續（這專案本來就用了不少）。
9. **改完一定 commit + push**（使用者多半不會自己跑指令），直接推 `main`、不開 PR。
10. **先用 AskUserQuestion 對齊方向再動手** —— 使用者改需求頻繁，做反方向很浪費。

---

## 11. 本產品開發歷史（2026-06-06，這個 session 從無到有）

1. **建立**：從 `../麻醉備物溝通看板.html` 瘦身複製出 `OP checklist/index.html`。移除全部備物區（Airway/Monitoring/備藥/止痛配方）、移除 Firebase/雲端、移除護理師看板，改純本機（獨立 `opChecklist_` key）。
2. **欄位調整**：新增「姓氏」；新增「自費」8 項多選；特殊提醒精簡為 4 項（高風險/未麻訪/Awake 插管/Post OP ICU）；Hx、Data 各加「其他」自填；移除 OP_PRESETS 自動帶入。
3. **部署**：在 repo 根 `netlify.toml` 加 `/checklist` rewrite → 上線 `…netlify.app/checklist`。
4. **看板/表單調整**：把 Hx、Data 移到「自費」之前；看板的 Hx/Data 改成**直接攤開顯示**（移除原本收合的 pill）。
5. **App 圖示**：使用者提供「麻醉面罩＋查核板」母圖（`icons/source.png`），用 `_build_icon.py` 縮出各尺寸；加 `manifest.webmanifest` 與 head 連結，可加到手機主畫面像 App。
6. **看板版面**：同一手術室的 case 從直向堆疊改成**橫向排列、可左右拉**（排序邏輯不變）。
7. **交班單**：寫了本檔（與備物看板交班單獨立）。

---

## 12. 已知限制 / 之後可能要做

- [ ] 純本機：換手機、清瀏覽器資料、換瀏覽器 → 資料不見；無跨裝置同步（這是刻意的設計）。
- [ ] 跨夜 case 一樣 23:59 被清（沒做保留機制）。
- [ ] 沒有測試（單元 / E2E 都沒有）。
- [ ] `favicon-32.png` 在 32px 下內容略密（面罩＋查核板細節多）；想更清楚可考慮做一個「簡化版小圖」單獨給 favicon。
- [ ] 卡片固定 280px；若使用者想一次看更多台 case，可把卡片做窄或做精簡模式。
- [ ] 若未來要雲端同步：需自己接，務必用獨立 path / 獨立專案，別污染備物看板的 `cases/`。

---

## 13. 給未來 Claude 的提醒（接手前讀這段）

- **這是獨立 app。** 你的改動範圍應該侷限在 `OP checklist/`（外加偶爾 repo 根的 `netlify.toml`）。**不要去改** `../麻醉備物溝通看板.html`、`../board/index.html`、`../*-本機版.html`、`../交班單-Claude.md`、`../_build_local.py`——那些是另一個產品（備物看板）的。
- 共用邏輯是「各自一份拷貝」。在這裡改房間清單 / 科別 / 排序**不會**同步到備物看板，反之亦然。除非使用者要求，不要去做「抽成共用檔」。
- **預覽驗證**：用 preview 工具開 `/OP%20checklist/index.html`。**靜態 server 沒有 HMR**，改完檔案要手動 reload（`window.location.href = '/OP%20checklist/index.html?v=' + Date.now()`）才看得到新版。（本 session 曾遇到 `preview_screenshot` 逾時，但 `preview_eval` 正常 → 可改用 DOM 量測驗證。）
- `Edit` 出現 "File has been modified since read" 通常是 linter 動過，**Re-Read 後重試即可**。
- 使用者在 Windows + Cursor / Claude Code，路徑用 `C:/Users/jenni/...`；shell 是 PowerShell（python 用 `py` 不要用 `python`）。
- 動圖示就改 `icons/source.png` 再跑 `py "OP checklist/_build_icon.py"`，別手改產生出來的 PNG。

---

## 14. 一段話 Onboarding（給未來 Claude 自己看）

> 這是台灣彰化秀傳麻醉科醫師的**個人** OP checklist 記錄工具，單檔 HTML + 原生 JS + **純本機 localStorage**（無雲端、無後端、無 LLM API），部署在 Netlify 的 `/checklist` 子路徑，可加到手機主畫面當 App。它是從同 repo 的「備物溝通看板」瘦身來的**獨立產品**，共用部分 UI/邏輯但檔案各自維護——**只動 `OP checklist/`，別碰備物看板的檔**。資料 schema 在第 5 節、常數在第 6 節、看板/表單行為在第 7 節、使用者鐵律在第 10 節。改完直接 `git push origin main`（不開 PR），Netlify 30–60 秒更新。使用者是醫師非工程師、用中文、改需求頻繁，**先問再動手**。
