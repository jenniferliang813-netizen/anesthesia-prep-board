# Claude Code 交班：彰化秀傳麻醉科麻醉備物溝通看板

## 目標

請以現有 `蛙蛙設計.html` 為基礎修改，不要重寫成複雜框架。  
新版定位為：**麻醉 case 快速紀錄＋止痛／麻醉備物溝通看板**。

核心用途：麻醉醫師看完 HIS data 後，用最少點擊記錄 case 與麻醉備物需求，讓護理師在看板上看到清楚的備物摘要。

第一版限制：
- 不串 HIS
- 不輸入姓名、病歷號、身分證字號
- 不貼完整 HIS data / lab
- 不作為正式醫囑或病歷紀錄
- 不做護理師備物進度追蹤
- 暫時維持單檔 HTML + localStorage prototype

頁面提醒文字：
> 本工具僅供彰化秀傳麻醉科 OR 內部備物溝通，不作為正式醫囑或病歷紀錄。實際藥物、劑量、濃度與給藥仍以麻醉醫師現場確認與院內規範為準。

---

## UI 風格

請改成簡潔、專業、醫療藍灰風。

標題：
- 主標題：彰化秀傳麻醉科
- 副標題：麻醉備物溝通看板

需求：
- 字體大一點，方便視力不好的人閱讀
- 按鈕高度至少 44px
- body font-size 建議 18px 以上
- case card 主文字 20px 以上
- 配色：深灰藍、鋼鐵藍、霧白、淺灰
- 手機、平板、醫院電腦皆可閱讀

---

## 班別房間篩選

刪掉「全部」選項。  
值班就等於全部常用房間。

```javascript
const ROOM_GROUPS = {
  day_front: {
    label: '白班前段',
    rooms: ['1', '2', '5', '6', '13']
  },
  day_back: {
    label: '白班後段',
    rooms: ['7', '8', '9', '11', '13', '18']
  },
  duty: {
    label: '值班',
    rooms: ['1', '2', '5', '6', '7', '8', '9', '11', '13', '18']
  }
};
```

需求：
1. 新增手術頁最上方加入班別按鈕：白班前段 / 白班後段 / 值班。
2. 選擇班別後，Room 按鈕只顯示該班別房間。
3. 看板頁也依同一班別篩選。
4. 看板不要顯示沒有 case 的空房間。
5. 使用 localStorage 記住最後選擇的班別。

---

## 房間異動

因為 OR 會臨時跳房，不要只使用 `room`。

case 欄位請改為：

```javascript
originalRoom: '5',
currentRoom: '5',
roomStatus: '原房'
```

若 `originalRoom !== currentRoom`，看板顯示：

```text
⚠️ 跳房：R5 → R8
```

可先保留簡單修改 currentRoom 的功能，不需要做拖拉排序。

---

## 醫師端新增 case 欄位順序

1. 班別 / 負責區段
2. Room
3. 第幾台
4. 科別
5. 術式
6. 麻醉方式
7. 止痛 / 麻醉備物
8. 特殊提醒
9. 備註
10. 送出到看板

### 第幾台

按鈕：
- 第1台
- 第2台
- 第3台
- 第4台
- 急診插入
- 其他

其他可開簡短輸入框。

---

## 止痛 / 麻醉備物區塊

新增區塊：**止痛 / 麻醉備物**

包含：
- Nerve block
- Testing syringe
- Spinal morphine
- Dynastat
- Acetamol
- Epidural PCA
- IVPCA

---

## Nerve block 設計

臨床語意很重要。  
不是「總量稀釋後分成幾隻」。  
而是「每一隻針筒都是同樣配方，每隻最後稀釋到指定 ml，總共抽幾隻同樣配方」。

正確顯示範例：

```text
NB：ESP block
Ropivacaine 5 ml + Decadron 1 ml + Epinephrine 0.1 ml
用 D5W 稀釋至 20 ml，抽 2 隻
```

意思是：每一隻針筒都是以上配方，最後稀釋到 20 ml，總共抽 2 隻同樣配方。

### UI 欄位

```text
□ Nerve block

Block type：
[ESP] [TAP] [PENG] [FIB] [ACB] [DSB] [ICNB] [PECS] [其他]

每隻針筒配方：
Ropivacaine ____ ml
Decadron ____ ml
Epinephrine ____ ml

稀釋液：
[Normal saline] [D5W]

每隻稀釋至：
____ ml

數量：
抽 ____ 隻
```

### 顯示邏輯

若某藥物欄位空白，不要顯示該藥物。  
例如 Epinephrine 空白時，顯示：

```text
NB：PENG block
Ropivacaine 10 ml + Decadron 1 ml
用 Normal saline 稀釋至 20 ml，抽 1 隻
```

禁止使用：
- total volume
- 分裝
- 分 __ 隻

請使用：
- 每隻稀釋至
- 抽 __ 隻

資料結構：

```javascript
nerveBlock: {
  enabled: true,
  blockType: 'ESP',
  perSyringe: {
    ropivacaineMl: '5',
    decadronMl: '1',
    epinephrineMl: '0.1',
    diluentType: 'D5W',
    diluteToMl: '20'
  },
  syringeCount: '2'
}
```

---

## Testing syringe

Testing 也使用「每隻針筒」語意。

UI：

```text
□ Testing syringe
Lidocaine ____ ml
稀釋液：[Normal saline] [D5W]
每隻稀釋至 ____ ml
抽 ____ 隻
```

顯示：

```text
Testing：
Lidocaine 1 ml
用 Normal saline 稀釋至 5 ml，抽 1 隻
```

資料結構：

```javascript
testing: {
  enabled: true,
  perSyringe: {
    lidocaineMl: '1',
    diluentType: 'Normal saline',
    diluteToMl: '5'
  },
  syringeCount: '1'
}
```

---

## Spinal morphine

只要 checkbox，不要劑量欄位。

UI：

```text
□ Spinal morphine
```

顯示：

```text
Spinal morphine
```

資料結構：

```javascript
spinalMorphine: true
```

---

## Dynastat / Acetamol

使用 checkbox 或大按鈕。

```text
□ Dynastat
□ Acetamol
```

顯示：

```text
Systemic analgesics：Dynastat、Acetamol
```

---

## Epidural PCA / IVPCA

使用 checkbox 或大按鈕。

```text
□ Epidural PCA
□ IVPCA
```

顯示：

```text
PCA：Epidural PCA、IVPCA
```

第一版不要做 PCA 詳細配方。

---

## 特殊提醒

保留或新增以下快速提醒：

- 高風險
- 尚未麻評
- 需回問
- 困難 airway
- 需 A-line
- 需 CVC
- 需 DLT
- 需 VL
- 需 FOB
- 備血 / T&S
- ICU postop
- 術後呼吸器

---

## 看板卡片顯示格式

請顯示成臨床可讀語句，不要顯示 JSON 或原始欄位名。

範例：

```text
Room 7｜第2台｜CS｜Lobectomy｜GA

止痛 / 麻醉備物：
NB：ESP block
Ropivacaine 5 ml + Decadron 1 ml + Epinephrine 0.1 ml
用 D5W 稀釋至 20 ml，抽 2 隻

Testing：
Lidocaine 1 ml
用 Normal saline 稀釋至 5 ml，抽 1 隻

PCA：IVPCA
Systemic analgesics：Dynastat、Acetamol

提醒：需 A-line、尚未麻評
備註：＿＿＿
```

---

## 每日 23:59 自動清除資料

資安需求：每天晚上 23:59 刪掉所有 app 記憶。

要求：
1. 不要使用 `localStorage.clear()`。
2. 所有 app 資料使用專屬 localStorage key。
3. 每次 app 載入時檢查資料日期；若不是今天，清除舊資料。
4. app 運行中設定 timer，到 23:59 自動清除資料並刷新看板。
5. 若瀏覽器 23:59 沒開，隔天打開也要自動清除前一天資料。

建議 key：

```javascript
const STORAGE_KEYS = {
  patients: 'anesthesiaPrep_patients',
  selectedRoomGroup: 'anesthesiaPrep_selectedRoomGroup',
  dataDate: 'anesthesiaPrep_dataDate'
};
```

---

## CSV 匯出

保留 CSV 匯出，新增欄位：

- 日期
- 班別
- 原房間
- 目前房間
- 第幾台
- 科別
- 術式
- 麻醉方式
- 止痛備物摘要
- NB block type
- NB 每隻配方
- NB 稀釋液
- NB 每隻稀釋至 ml
- NB 抽幾隻
- Testing 摘要
- Spinal morphine
- Dynastat
- Acetamol
- Epidural PCA
- IVPCA
- 特殊提醒
- 備註
- 手術狀態

請處理逗號、換行、雙引號，避免 CSV 格式跑掉。

---

## 安全與輸入限制

1. 備註最多 80 字。
2. placeholder：請勿輸入姓名、病歷號或完整病歷內容。
3. 避免使用 innerHTML 直接插入使用者輸入文字。
4. 若必須使用 innerHTML，請先 escape HTML。
5. 不要輸入姓名、病歷號、完整 lab 或 HIS 內容。

---

## 第一版不要做

- HIS 串接
- 登入系統
- 原生手機 App
- 護理師備物進度
- 病人姓名
- 病歷號
- 完整 lab data
- PCA 詳細配方
- Spinal morphine 劑量
- 複雜統計 dashboard

---

## 完成標準

完成後應具備：

1. 彰化秀傳麻醉科標題
2. 簡潔專業大字體 UI
3. 班別房間篩選：白班前段 / 白班後段 / 值班
4. 快速新增 case
5. 第幾台欄位
6. originalRoom / currentRoom
7. 跳房提示
8. 止痛 / 麻醉備物輸入
9. NB 使用「每隻配方、稀釋至幾 ml、抽幾隻」語意
10. Testing syringe 使用同樣語意
11. Spinal morphine 只勾選，不輸入劑量
12. Dynastat / Acetamol / Epidural PCA / IVPCA 勾選
13. 看板顯示清楚備物摘要
14. 每日 23:59 清除 app 記憶
15. CSV 匯出包含止痛備物欄位
16. 不使用 localStorage.clear()
17. 不要求醫師逐台確認
18. 不做護理師備物進度
