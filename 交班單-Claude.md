# 🤖 Claude 交班單｜麻醉備物溝通看板

> 給未來 Claude session 接手用。讀完這份你就能理解專案現況、架構、設計慣例、與使用者偏好，可以直接接著改。

---

## 1. 一句話總結

彰化秀傳麻醉科內部 OR **備物溝通**工具。麻醉醫師輸入 case 與止痛/麻醉備物需求 → 雲端即時同步 → 麻醉護理師在自己的裝置看到要備什麼。**不是病歷、不是醫囑、不是 HIS 串接、不收病人個資**。

使用者是醫師（梁庭瑋）。她不是工程師，但能跑簡單 Git/CLI 指令。對話用中文。

---

## 2. 線上網址

| 角色 | 主力（Netlify，醫院內網可用） | 備援（GitHub Pages） |
|---|---|---|
| 麻醉醫師完整版 | https://anesthesia-prep-board.netlify.app/ | https://jenniferliang813-netizen.github.io/anesthesia-prep-board/ |
| 麻醉護理師看板 | https://anesthesia-prep-board.netlify.app/board/ | https://jenniferliang813-netizen.github.io/anesthesia-prep-board/board/ |

彰化秀傳內網封 `*.github.io`，所以**主力是 Netlify**。改了之後 push 到 GitHub main，Netlify 會 auto-deploy（也順便更新 Pages 備援，但醫院打不開）。

---

## 3. 工作目錄與檔案結構

```
C:\Users\jenni\我的雲端硬碟\AI\手術動態看板\
├── 麻醉備物溝通看板.html       ← 麻醫完整版（主程式）
├── index.html                  ← GitHub Pages 入口（meta-refresh 到主程式）
├── netlify.toml                ← Netlify 部署設定（含 / → 主程式 rewrite）
├── board/
│   └── index.html              ← 護理師看板（簡化版、唯讀大部分欄位、可改狀態/跳房）
├── docs/
│   ├── 麻醉醫師-使用說明.md    ← LINE 分享給麻醫
│   └── 護理師-使用說明.md      ← LINE 分享給護理師
├── archive/
│   └── 蛙蛙設計.html          ← 早期 prototype，封存
├── anesthesia_prep_board_claude_handoff.md ← 初版規格交班（歷史文件）
├── 交班單-Claude.md           ← 本檔
├── README.md
├── .gitignore
└── .git/                       ← repo 已 init，遠端 origin = github.com/jenniferliang813-netizen/anesthesia-prep-board
```

---

## 4. 技術架構

```
┌──────────────────────────────────────────────┐
│  Browser (Chrome / Safari / Edge)            │
│  ├── Vanilla JS（ES module）                  │
│  ├── localStorage（離線快取）                  │
│  └── 載入時 + 即時訂閱 Firebase RTDB           │
└──────────────────────────────────────────────┘
              ↕ HTTPS / WSS
┌──────────────────────────────────────────────┐
│  Firebase Realtime Database                   │
│  asia-southeast1（新加坡）                     │
│  Path: /cases/{id} = patient object           │
└──────────────────────────────────────────────┘
                ↑
        deploy 到下面兩個 host
┌──────────────────────┬──────────────────────┐
│  Netlify（主力）       │  GitHub Pages（備）   │
│  *.netlify.app        │  *.github.io          │
│  從 main branch       │  從 main branch       │
│  auto-deploy          │  auto-deploy          │
└──────────────────────┴──────────────────────┘
                ↑
            git push origin main
```

### 工具與帳號
- **GitHub repo**：`jenniferliang813-netizen/anesthesia-prep-board`（public）
- **Netlify project**：`anesthesia-prep-board`（owner: jenniferliang813's team）
- **Firebase project**：`anesthesia-prep-board`（owner: 同 Google 帳號）

### Firebase config（已 hardcode 在 HTML 內，可從 repo 看）
```js
{
  apiKey: "AIzaSyAE86UeO3tLo6JCT7v_W7jwMnvftg0EwIA",
  authDomain: "anesthesia-prep-board.firebaseapp.com",
  databaseURL: "https://anesthesia-prep-board-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "anesthesia-prep-board",
  ...
}
```

⚠️ Firebase **目前是 30 天測試模式（open access）**。anon 都能讀寫雲端。對 OR 內部小圈圈 OK，但要意識到。30 天後會自動鎖，到時必須改 production rules。

---

## 5. 資料 Schema（patient object）

```js
{
  id: 1717033200000,               // Date.now() 時 unique
  date: "2026-05-30",              // 用於日期過濾與 23:59 清理
  roomGroup: "day_front",          // 班別：'day_front' | 'day_back' | 'duty'
  originalRoom: "5",               // 原本指定房間
  currentRoom: "5",                // 目前房間（跳房後會不同於 originalRoom）
  turn: "第2台",                    // 第1~4台 / 急診插入 / 其他（自填字串）
  age: "45",                       // 字串，最多 3 字
  gender: "M",                     // 'M' | 'F' | ''
  dept: "CS",                      // 科別 key，見 OP_MAPPING
  op: "Lobectomy",                 // 術式，可預設按鈕或自填
  anes: "GA",                      // GA | SA | IVG | EA
  airway: {
    lma: true,
    nonKinkingEndo: false,
    nasalTube: false,
    hfnc: false                    // 2026-05-30 新增
  },
  monitoring: { bis: true, cvpKit: false },   // cvpKit 2026-05-30 新增
  medications: {                   // 2026-05-30 新增「備藥」區塊
    propofolTci: false,
    remiTci: false,
    nimbex: false,
    anectine: false,
    levophed: false,               // Levophed 10mcg/ml
    ketamine: false,
    droperidol: false,
    etomidate: false
  },
  analgesia: {
    nerveBlock: {
      enabled: true,
      blockType: "ESP",            // 選「其他」時可手動自填任意字串（blockType 會存自填值）
      perSyringe: {
        ropivacaineMl: "5",
        decadronMl: "1",
        epinephrineMl: "0.1",
        diluentType: "D5W",        // 'D5W' | 'Normal saline'
        diluteToMl: "20"
      },
      syringeCount: "2"
    },
    testing: {
      enabled: true,
      perSyringe: {
        lidocaineMl: "1",
        diluentType: "Normal saline",
        diluteToMl: "5"
      },
      syringeCount: "1"
    },
    spinalMorphine: false,
    dynastat: false,
    acetamol: false,
    epiduralPCA: false,
    ivpca: true
  },
  reminders: ["需 A-line", "需 DLT", "Post OP ICU"],
  hx: ["HTN", "DM"],
  data: ["CXR ok"],
  memo: "...",                     // ≤80 字
  status: "手術中",                 // 待手術 / 手術中 / 已完成
  createdAt: 1717033200000
}
```

Firebase path：`cases/{id}` 直接存整個 object。雲端訂閱回 `/cases` 整包 listen。

---

## 6. 重要常數（都在 `麻醉備物溝通看板.html` 的 `<script>` 區頂部）

```js
ROOM_GROUPS = {
  day_front: { label: '白班前段', rooms: ['1','2','5','6','13'] },
  day_back:  { label: '白班後段', rooms: ['7','8','9','11','13','18'] },
  duty:      { label: '值班',     rooms: ['1','2','5','6','7','8','9','11','13','18'] }
}

OP_MAPPING = {
  Ortho → ENT → NS → CS → CVS → GYN → GU → PS → OS → GS → CRS → BS → OPH
}  // 科別排序是使用者明確要求，動的時候確認
   // 2026-05-30 術式內容調整：
   //   Ortho 刪 ROI、加 PELD/L-spine/C-spine
   //   ENT  tumor→tumor excision、加 LN biopsy
   //   CS   Wedge/Rib fracture 置最前、加 tracheostomy/PP window
   //   GYN  TCR→子宮鏡、staging→Open Debulking/Laparoscopic Staging
   //   CRS  Rt hemi→Hemicolectomy、加 AR
   //   BS   砍 BCS/Mastectomy → Partial mastectomy/MRM

OP_PRESETS = {  // 選了術式自動勾選對應的特殊提醒（隱形預帶，不彈窗）
  'Lobectomy': ['需 A-line', '需 DLT', 'Post OP ICU'],
  'Esophagectomy': ['需 A-line', '需 DLT', '需粗 line', 'Post OP ICU'],
  '切肝': ['需 A-line', '需 CVC'],
  'Open Debulking': ['需 A-line', '需 CVC'],          // 2026-05-30 新增
  'Laparoscopic Staging': ['需 A-line', '需 CVC'],     // 2026-05-30 新增
  // ... 約 15 項
}
// 2026-05-30 移除的預帶路徑：Rib fracture(DLT)、食道擴張、Varicose、
//   TEVAR/AAA(粗 line)、AV shunt(A-line/粗 line)；CVS 一律不再預勾 DLT

REMINDER_LIST = ['高風險','未麻訪','Awake 插管','需 FOB','需 DLT','需 A-line','需粗 line','需 CVC','術後呼吸器','Post OP ICU']
// 2026-05-30 重新分類排序：高風險/未麻訪 → 呼吸道(Awake插管/FOB/DLT) → 線路(A-line/粗line/CVC) → 術後(呼吸器/ICU)
// 刪除：需回問、困難 airway、需 VL；「尚未麻評」改名「未麻訪」；「ICU postop」改名「Post OP ICU」

BLOCK_TYPES = ['ESP','TAP','PENG','FIB','ACB','DSB','PECS','CCB','SCB','superior trunk','QL','ITP','FTB','popliteal','Caudal','其他']
// 選「其他」會跳出自填輸入框（nb-type-custom），blockType 存自填字串

DILUENTS = ['Normal saline','D5W']

STATUS_ORDER = ['待手術','手術中','已完成']

MEDICATIONS（備藥區，2026-05-30 新增）= Propofol TCI / Remifentanil TCI / Nimbex /
  Anectine / Levophed 10mcg/ml / Ketamine / Droperidol / Etomidate
AIRWAY 新增 HFNC；MONITORING 新增 CVP kit

DATA_LIST 2026-05-30 重排：判讀類(CXR/EKG/echo)置前、抽血類置後
```

### 跨欄位連動規則
- ~~勾「困難 airway」→ 自動補勾「需 FOB」~~（2026-05-30 已移除，困難 airway 選項也砍了）
- 術式選了 → 套用 OP_PRESETS 預帶（隱形，不彈窗）
- NB block type 選「其他」→ 顯示自填輸入框

---

## 7. 使用者偏好與約束（一定要遵守）

1. **單檔 HTML + 原生 JS**，**不引入框架（React/Vue/...）、不引入 build step**
2. **不打外部 LLM API**（user 明確排除）
3. **只用 Firebase JS SDK 與 gstatic.com**，盡量不引入其他 CDN
4. **資料不寫病人個資**：姓名、病歷號、身分證、完整 lab、完整 HIS — 禁止
5. **所有 user 輸入用 `textContent`，不可 `innerHTML`** — XSS 防線
6. **每日 23:59 全清**（local + cloud），載入時也檢查 date 過期就清
7. **不要主動加 emoji 到檔案，除非 user 明確要**（但這個 prototype 已經滿 emoji 的，可延續風格）
8. **字體大、按鈕至少 44px**，使用者部分是中高年資視力不佳的醫護
9. **配色：深灰藍 + 鋼鐵藍 + 霧白**，醫療專業風
10. **Chrome 自動翻譯**會把英文藥名翻成中文，已加 `translate="no"` 防護，動 HTML head 注意保留

---

## 8. Deploy 流程

```bash
# 在 C:\Users\jenni\我的雲端硬碟\AI\手術動態看板\ 下
git add -A
git commit -m "說明這次改了什麼"
git push
```

push 完：
- **Netlify**：約 30-60 秒 auto-deploy，看 https://app.netlify.com/projects/anesthesia-prep-board/deploys
- **GitHub Pages**：約 1-2 分鐘 auto-rebuild

不需要其他 build step。檔案直接服務。

⚠️ 不要建 PR，user 是單人開發，直接 push main。

---

## 9. 開發歷史時間軸（精簡）

1. **初版規格**：見 `anesthesia_prep_board_claude_handoff.md`，user 找另一個 Claude 寫的交班
2. **v1 骨架**：建單檔 HTML、新增 case + 看板 兩 tab、班別篩選、第幾台、止痛備物、跳房
3. **欄位調整**：科別清單重排、新增 OS / OPH、刪掉 OPD / TRUS / LSC、NB types 大改、Data eGFR<30、Airway 加 Non-kinking endo + 鼻管
4. **BIS + 語音**：加 Monitoring 區塊（BIS）、加 🎙 語音輸入用 Web Speech API
5. **Firebase 雲端同步**：手動建 Firebase project，加 Realtime DB sync，原 localStorage 改為快取
6. **護理師看板分頁**：建 `board/index.html`，唯讀但可改狀態 + 跳房
7. **Netlify 部署**：醫院封 github.io，user 確認可開 netlify.app，遷移
8. **移除語音**：辨識不準，user 決定砍掉
9. **排序加 status 優先**：看板手術中 → 待手術 → 已完成
10. **術式與備物大更新（2026-05-30）**：六科術式清單調整、OP_PRESETS 移除多條預帶路徑、
    特殊提醒重新分類（刪困難airway/需回問/需VL，尚未麻評→未麻訪，加 Awake 插管）、
    Data 判讀類置前、Airway 加 HFNC、Monitoring 加 CVP kit、新增備藥區 8 項、
    NB「其他」可自填、ICU postop→Post OP ICU。主檔/看板/CSV 全同步（**this commit**）

---

## 10. 已知限制 / 之後可能要做

- [ ] Firebase 30 天測試模式到期，要改 production rules（建議 magic link auth + 只允許特定 email）
- [ ] 跨夜 case 還是會 23:59 清掉，沒做保留機制
- [ ] 沒做護理師備物進度追蹤（user 明確說第一版不做）
- [ ] 沒做病人姓名、病歷號、HIS 整合（仍是禁區）
- [ ] PCA 詳細配方目前只有 checkbox，user 說第一版不做配方
- [ ] Spinal morphine 沒劑量欄位，user 明確只要 checkbox
- [ ] CSV 匯出不含同步歷史（只當下快照）
- [ ] 沒有 PWA / 離線安裝，純網頁
- [ ] 沒有測試（單元測試、E2E 都沒有）

---

## 11. 給未來 Claude 的提醒

- user 改需求很頻繁，**先用 AskUserQuestion 對齊方向再動手**，避免做反方向
- 改動相關的測試指令 user 多半不會跑，**改完一定要 commit + push**
- 動 Firebase config 之前要先問 user（牽涉雲端服務）
- 用 TaskCreate 追蹤多步驟工作，user 看得到進度
- Edit 出現 "File has been modified since read" 通常是 linter 動過，**Re-Read 後重試即可**
- user 在 Windows + Cursor / Claude Code，路徑用 `C:/Users/jenni/...`
- 工作目錄是 Google Drive 同步資料夾，**慎用大量 .git 操作以免拖累 Drive sync**

---

## 12. 一段話 Onboarding（給未來 Claude 自己看）

> 這是台灣一家醫院（彰化秀傳）麻醉科內部備物溝通工具的 prototype。技術上是單檔 HTML + Firebase Realtime DB + Netlify host。使用者是醫師、不是工程師，所有溝通用中文，先問再動手。**不能加病人個資、不能引入框架、不能打 LLM API**。資料 schema 在第 5 節、預設清單與排序在第 6 節、使用者偏好在第 7 節。改完直接 `git push origin main`，Netlify 30 秒會更新。如果使用者拒絕某個方向，記下來不要再提（例如語音已經被砍）。
