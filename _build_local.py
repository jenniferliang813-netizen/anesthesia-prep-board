# -*- coding: utf-8 -*-
# 從主程式（SDK 版）產生「本機離線版」：移除 gstatic SDK，改用 REST API + 輪詢。
import io, sys

SRC = r"C:\Users\jenni\我的雲端硬碟\AI\手術動態看板\麻醉備物溝通看板.html"
DST = r"C:\Users\jenni\我的雲端硬碟\AI\手術動態看板\麻醉備物溝通看板-本機版.html"

txt = io.open(SRC, encoding="utf-8").read()

# 標題與表頭標記
txt = txt.replace("<title>彰化秀傳麻醉備物溝通看板</title>",
                  "<title>彰化秀傳麻醉備物溝通看板（本機版）</title>")
txt = txt.replace('<div class="sub">麻醉備物溝通看板</div>',
                  '<div class="sub">麻醉備物溝通看板（本機離線版）</div>')

NEW_HEAD = '''<script>
/* ===== 本機離線版（自給自足，雙擊即可開） =====
   不從 gstatic 載入 Firebase SDK、也不靠 netlify；改用 Firebase Realtime Database
   的 REST API + 每 3 秒輪詢。整個檔案自己就能跑出畫面，醫院就算擋掉 netlify / Google
   SDK 也載得起來。即時同步仍需連得到資料庫網域 firebasedatabase.app（被擋時會自動
   退成離線單機模式，資料只存這台）。 */
const DB_BASE = "https://anesthesia-prep-board-default-rtdb.asia-southeast1.firebasedatabase.app";
const POLL_MS = 3000;
let cloudOnline = false;
let pollTimer = null;
let writing = 0;   // 寫入進行中暫停輪詢覆蓋，避免剛新增的 case 被蓋掉

async function cloudWriteCase(p) {
  writing++;
  try {
    const r = await fetch(DB_BASE + '/cases/' + p.id + '.json', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(p)
    });
    cloudOnline = r.ok; updateCloudStatus();
  } catch(e) { cloudOnline = false; updateCloudStatus(); }
  finally { writing--; }
  pollOnce();
}
async function cloudDeleteCase(id) {
  writing++;
  try {
    const r = await fetch(DB_BASE + '/cases/' + id + '.json', { method: 'DELETE' });
    cloudOnline = r.ok; updateCloudStatus();
  } catch(e) { cloudOnline = false; updateCloudStatus(); }
  finally { writing--; }
  pollOnce();
}
async function cloudPurgeAll() {
  writing++;
  try {
    const r = await fetch(DB_BASE + '/cases.json', { method: 'DELETE' });
    cloudOnline = r.ok; updateCloudStatus();
  } catch(e) { cloudOnline = false; updateCloudStatus(); }
  finally { writing--; }
  pollOnce();
}
async function pollOnce() {
  if (writing > 0) return;
  try {
    const r = await fetch(DB_BASE + '/cases.json', { cache: 'no-store' });
    if (!r.ok) throw new Error('http ' + r.status);
    const val = (await r.json()) || {};
    cloudOnline = true;
    const today = todayStr();
    const valid = [];
    Object.entries(val).forEach(([id, p]) => {
      if (!p) return;
      const d = p.date || today;
      if (d === today) valid.push(p);
      else { fetch(DB_BASE + '/cases/' + id + '.json', { method: 'DELETE' }).catch(()=>{}); }
    });
    localStorage.setItem(STORAGE_KEYS.patients, JSON.stringify(valid));
    localStorage.setItem(STORAGE_KEYS.dataDate, today);
    updateCloudStatus();
    const boardEl = document.getElementById('board-page');
    if (boardEl && boardEl.classList.contains('active')) renderBoard();
  } catch(e) {
    cloudOnline = false;
    updateCloudStatus();
  }
}
function startCloudSubscribe() {
  pollOnce();
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(pollOnce, POLL_MS);
}
function updateCloudStatus() {
  const el = document.getElementById('cloud-status');
  if (!el) return;
  el.textContent = cloudOnline ? '☁ 雲端同步中（每 3 秒更新）' : '⚠ 離線模式（僅存本機，未連到雲端）';
  el.className = 'cloud-status ' + (cloudOnline ? 'online' : 'offline');
}

'''

start = txt.index('<script type="module">')
anchor = txt.index('const STORAGE_KEYS')
txt = txt[:start] + NEW_HEAD + txt[anchor:]

io.open(DST, "w", encoding="utf-8", newline="\n").write(txt)
print("built:", DST.encode("ascii", "replace").decode())


# =========================================================================
# 護理師看板 本機版（大字體簡化版） board/index.html -> 護理師看板-本機版.html
# =========================================================================
BSRC = r"C:\Users\jenni\我的雲端硬碟\AI\手術動態看板\board\index.html"
BDST = r"C:\Users\jenni\我的雲端硬碟\AI\手術動態看板\護理師看板-本機版.html"
b = io.open(BSRC, encoding="utf-8").read()

# 標題、表頭、底部連結（指回本機版麻醫檔）
b = b.replace("<title>麻醉備物看板（護理師檢視）</title>",
              "<title>麻醉備物看板（護理師檢視·本機版）</title>")
b = b.replace('<div class="sub">護理師檢視（即時同步）</div>',
              '<div class="sub">護理師檢視（本機離線版·每 3 秒同步）</div>')
b = b.replace('<a class="full-link" href="../">→ 麻醉醫師完整版（新增 / 編輯 case）</a>',
              '<a class="full-link" href="麻醉備物溝通看板-本機版.html">→ 麻醉醫師完整版（新增 / 編輯 case）</a>')

# A. 移除 module import + Firebase SDK 初始化
b_start = b.index('<script type="module">')
b_anchor = b.index('const ROOM_GROUPS')
B_HEAD = '''<script>
/* ===== 護理師看板 本機離線版（自給自足，雙擊即開） =====
   不依賴 netlify / gstatic SDK；同步用 Firebase RTDB REST API + 每 3 秒輪詢。 */
const DB_BASE = "https://anesthesia-prep-board-default-rtdb.asia-southeast1.firebasedatabase.app";
const POLL_MS = 3000;
let pollTimer = null;
let writing = 0;

'''
b = b[:b_start] + B_HEAD + b[b_anchor:]

# B. cloudWriteCase -> REST PUT（含 writing 守衛）
b = b.replace(
'''async function cloudWriteCase(p) {
  try { await set(ref(fbDb, 'cases/' + p.id), p); }
  catch(e) { console.warn('cloud write fail', e); alert('⚠ 雲端寫入失敗，請檢查網路'); }
}''',
'''async function cloudWriteCase(p) {
  writing++;
  try {
    const r = await fetch(DB_BASE + '/cases/' + p.id + '.json', {
      method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(p)
    });
    if (!r.ok) throw new Error('http ' + r.status);
  } catch(e) { console.warn('cloud write fail', e); alert('⚠ 雲端寫入失敗，請檢查網路'); }
  finally { writing--; }
  pollOnce();
}''')

# C. startSubscribe(onValue) -> pollOnce + setInterval
b = b.replace(
'''function startSubscribe() {
  onValue(ref(fbDb, 'cases'), (snap) => {
    const val = snap.val() || {};
    const today = todayStr();
    const valid = [];
    Object.entries(val).forEach(([id, p]) => {
      if (!p) return;
      const d = p.date || today;
      if (d === today) valid.push(p);
      else { remove(ref(fbDb, 'cases/' + id)).catch(()=>{}); }
    });
    currentPatients = valid;
    updateCloudStatus(true);
    renderBoard();
  }, (err) => {
    updateCloudStatus(false);
    console.warn(err);
  });
}''',
'''async function pollOnce() {
  if (writing > 0) return;
  try {
    const r = await fetch(DB_BASE + '/cases.json', { cache: 'no-store' });
    if (!r.ok) throw new Error('http ' + r.status);
    const val = (await r.json()) || {};
    const today = todayStr();
    const valid = [];
    Object.entries(val).forEach(([id, p]) => {
      if (!p) return;
      const d = p.date || today;
      if (d === today) valid.push(p);
      else { fetch(DB_BASE + '/cases/' + id + '.json', { method: 'DELETE' }).catch(()=>{}); }
    });
    currentPatients = valid;
    updateCloudStatus(true);
    renderBoard();
  } catch(e) {
    updateCloudStatus(false);
    console.warn(e);
  }
}
function startSubscribe() {
  pollOnce();
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(pollOnce, POLL_MS);
}''')

# D. 狀態列文字
b = b.replace("online ? '☁ 雲端同步中（即時更新）'",
              "online ? '☁ 雲端同步中（每 3 秒更新）'")

io.open(BDST, "w", encoding="utf-8", newline="\n").write(b)
print("built:", BDST.encode("ascii", "replace").decode())
