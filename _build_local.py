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
