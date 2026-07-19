"""
Expense Tracker — a simple yet powerful web app.  (v8 — bigger, fuller dashboard)

Inspired by ezbookkeeping's premium look (Vuetify-style nav drawer, warm
orange primary #c67e48, dark sidebar) with a larger, denser dashboard that
fills the page: KPIs, one-tap quick-add shortcuts, recent expenses, a pie
chart, and a monthly trend graph — all on the main view.

Features:
    💾 Saving expenses to a file   -> expenses.json (auto load + save)
    ✏️ Editing / Deleting entries  -> each expense has a unique id
    🏷️ A category per expense      -> e.g. Food, Transport, Bills, ...
    📅 A date per expense          -> defaults to today, editable
    ⚡ Quick-add shortcuts         -> one-tap category buttons -> type amount
    📈 Pie OR bar chart            -> toggle between the two views
    📊 Monthly trend graph         -> last 6 months at a glance
    🌗 Light / Dark toggle         -> remembered in localStorage
    🗓️ Monthly filter             -> KPIs + chart + list scoped to a month
    📆 This vs last month KPI      -> delta with up/down indicator
    🧹 Clear-all / reset button    -> wipes everything after confirm
    ✨ Premium dashboard UI        -> sidebar nav, KPI cards, glass surfaces

Core beginner concepts still used:
    🧠 Variables & data storage   -> expenses list + total accumulator
    ⌨️ User input handling        -> form data from the browser
    🔁 while loop (server)        -> server.serve_forever()
    ⚡ Conditional statements      -> if / elif for validation
    ➕ Accumulator pattern         -> total += expense (and -= on delete)
    🛡️ Error handling (try-except)-> bad numbers / dates / missing ids
    💰 Final total calculation     -> total reported after every change

Run it:  python3 app.py
Then open:  http://localhost:8000
"""

import datetime
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ------------------------------------------------------------
# 🧠 VARIABLES & DATA STORAGE
# ------------------------------------------------------------
expenses = []
total = 0.0
next_id = 1
DATA_FILE = "expenses.json"
CATEGORIES = ["Food", "Transport", "Shopping", "Bills",
              "Entertainment", "Health", "Other"]


# ------------------------------------------------------------
# 💾 FILE PERSISTENCE
# ------------------------------------------------------------
def save_data():
    payload = {"next_id": next_id, "expenses": expenses}
    with open(DATA_FILE, "w") as f:
        json.dump(payload, f, indent=2)


def load_data():
    global total, next_id
    if not os.path.exists(DATA_FILE):
        return
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
        expenses.extend(data.get("expenses", []))
        total = sum(e["amount"] for e in expenses)
        next_id = data.get("next_id", len(expenses) + 1)
    except (json.JSONDecodeError, KeyError, TypeError):
        print("Warning: could not read", DATA_FILE, "- starting empty.")


def parse_date(raw):
    if not raw:
        return datetime.date.today().isoformat()
    try:
        datetime.date.fromisoformat(raw)
        return raw
    except ValueError:
        return datetime.date.today().isoformat()


def by_category():
    breakdown = {}
    for e in expenses:
        breakdown[e["category"]] = round(breakdown.get(e["category"], 0.0) + e["amount"], 2)
    return breakdown


def snapshot(status, message=""):
    return {
        "status": status,
        "message": message,
        "expenses": expenses,
        "total": round(total, 2),
        "count": len(expenses),
        "by_category": by_category(),
    }


# ------------------------------------------------------------
# Core logic — one function per action
# ------------------------------------------------------------
def add_expense(raw_amount, raw_category, raw_date):
    global total, next_id
    text = raw_amount.strip()
    category = (raw_category or "Other").strip() or "Other"
    date = parse_date(raw_date)
    try:
        amount = float(text)
    except ValueError:
        return snapshot("invalid", f"'{text}' is not a valid number. Try again.")
    if amount < 0:
        return snapshot("invalid", "Amount cannot be negative. Enter a positive value.")
    expenses.append({"id": next_id, "amount": amount, "category": category, "date": date})
    total += amount
    next_id += 1
    save_data()
    return snapshot("added", f"Added {amount:.2f} under '{category}' on {date}.")


def edit_expense(raw_id, raw_amount, raw_category, raw_date):
    global total
    try:
        eid = int(raw_id)
    except (ValueError, TypeError):
        return snapshot("invalid", "Missing or invalid expense id.")
    target = next((e for e in expenses if e["id"] == eid), None)
    if target is None:
        return snapshot("invalid", f"No expense with id {eid}.")
    text = raw_amount.strip()
    try:
        new_amount = float(text)
    except ValueError:
        return snapshot("invalid", f"'{text}' is not a valid number.")
    if new_amount < 0:
        return snapshot("invalid", "Amount cannot be negative.")
    total += new_amount - target["amount"]
    target["amount"] = new_amount
    if raw_category and raw_category.strip():
        target["category"] = raw_category.strip()
    if raw_date and raw_date.strip():
        target["date"] = parse_date(raw_date)
    save_data()
    return snapshot("edited", f"Updated expense #{eid}.")


def delete_expense(raw_id):
    global total
    try:
        eid = int(raw_id)
    except (ValueError, TypeError):
        return snapshot("invalid", "Missing or invalid expense id.")
    target = next((e for e in expenses if e["id"] == eid), None)
    if target is None:
        return snapshot("invalid", f"No expense with id {eid}.")
    total -= target["amount"]
    expenses.remove(target)
    save_data()
    return snapshot("deleted", f"Deleted expense #{eid}.")


def reset_all():
    global total, next_id
    expenses.clear()
    total = 0.0
    next_id = 1
    save_data()
    return snapshot("reset", "All expenses cleared.")


# ------------------------------------------------------------
# Demo data — one click to fill the app with sample expenses
# ------------------------------------------------------------
DEMO_EXPENSES = [
    ("12.50", "Food", "2026-07-18"),
    ("4.00", "Transport", "2026-07-17"),
    ("59.99", "Shopping", "2026-07-15"),
    ("120.00", "Bills", "2026-07-10"),
    ("25.00", "Entertainment", "2026-07-12"),
    ("8.75", "Food", "2026-07-19"),
    ("35.00", "Health", "2026-07-05"),
    ("6.50", "Transport", "2026-07-14"),
    ("22.30", "Food", "2026-06-20"),
    ("115.00", "Bills", "2026-06-12"),
    ("9.25", "Transport", "2026-06-25"),
    ("40.00", "Shopping", "2026-05-18"),
    ("18.00", "Entertainment", "2026-05-22"),
    ("7.50", "Food", "2026-05-09"),
]


def load_demo():
    global total, next_id
    expenses.clear()
    total = 0.0
    next_id = 1
    for amount, category, date in DEMO_EXPENSES:
        add_expense(amount, category, date)
    return snapshot("demo", f"Loaded {len(expenses)} demo expenses.")


# ------------------------------------------------------------
# The HTML page (ezbookkeeping-style premium frontend). One file to run.
# ------------------------------------------------------------
PAGE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="color-scheme" content="dark light" />
  <title>Expense Tracker</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #15171c;
      --sidebar-bg: #202122;
      --surface: #1d2026;
      --surface-2: #23272f;
      --border: rgba(255,255,255,0.08);
      --input-bg: rgba(255,255,255,0.05);
      --chip-bg: rgba(0,0,0,0.30);
      --topbar-bg: rgba(29,32,38,0.85);
      --text: #e7ebf0;
      --muted: #9aa3b2;
      --primary: #c67e48;
      --primary-2: #d8915c;
      --radius: 16px;
      --shadow: 0 12px 34px rgba(0,0,0,0.42);
      font-family: 'Inter', Roboto, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    :root[data-theme="light"] {
      --bg: #eef0f3;
      --sidebar-bg: #202122;
      --surface: #ffffff;
      --surface-2: #ffffff;
      --border: rgba(15,23,42,0.10);
      --input-bg: #ffffff;
      --chip-bg: rgba(15,23,42,0.06);
      --topbar-bg: rgba(255,255,255,0.85);
      --text: #1f2733;
      --muted: #6b7280;
      --shadow: 0 12px 34px rgba(15,23,42,0.10);
    }
    * { box-sizing: border-box; }
    body { margin:0; color: var(--text); background: var(--bg); font-size:15px;
      -webkit-font-smoothing: antialiased; transition: background .3s, color .3s; }

    /* ---------- Sidebar ---------- */
    .sidebar {
      position: fixed; top:0; left:0; bottom:0; width:258px;
      background: var(--sidebar-bg); display:flex; flex-direction:column;
      padding: 22px 15px; z-index: 30;
      border-right: 1px solid rgba(255,255,255,0.06);
    }
    .brand { display:flex; align-items:center; gap:13px; padding: 4px 10px 24px; }
    .logo {
      width:42px; height:42px; border-radius:12px; flex:none;
      background: linear-gradient(135deg, var(--primary), var(--primary-2));
      display:flex; align-items:center; justify-content:center;
      box-shadow: 0 6px 16px rgba(198,126,72,0.45);
    }
    .brand-text .brand-name { color:#fff; font-weight:800; font-size:17px; letter-spacing:-0.01em; }
    .brand-text .brand-sub { color:#9aa3b2; font-size:11px; }
    .nav { display:flex; flex-direction:column; gap:5px; }
    .nav-item {
      display:flex; align-items:center; gap:14px; padding:13px 16px;
      border-radius:11px; color:#b9c0cb; cursor:pointer; font-weight:500;
      font-size:15px; transition: background .15s, color .15s; position:relative;
    }
    .nav-item svg { width:22px; height:22px; flex:none; }
    .nav-item:hover { background: rgba(255,255,255,0.06); color:#fff; }
    .nav-item.active { background: rgba(198,126,72,0.16); color: var(--primary-2); }
    .nav-item.active::before {
      content:''; position:absolute; left:0; top:8px; bottom:8px; width:3px;
      border-radius:0 3px 3px 0; background: var(--primary-2);
    }
    .sidebar-foot { margin-top:auto; padding: 16px 10px 0; color:#7d8593; font-size:11px; border-top:1px solid rgba(255,255,255,0.07); }

    /* ---------- Main ---------- */
    .main { margin-left:258px; min-height:100vh; transition: margin .2s; }
    .topbar {
      position: sticky; top:0; z-index:20; height:70px;
      display:flex; align-items:center; justify-content:space-between;
      padding: 0 30px; border-bottom:1px solid var(--border);
      background: var(--topbar-bg); backdrop-filter: blur(12px);
    }
    .topbar .title { font-size:20px; font-weight:700; }
    .top-actions { display:flex; align-items:center; gap:11px; }
    .content { padding: 28px; max-width: 1240px; }

    @media (max-width: 900px) {
      .sidebar { width:78px; padding:18px 10px; align-items:center; }
      .brand { padding: 4px 0 20px; }
      .brand-text, .sidebar-foot { display:none; }
      .nav-item { justify-content:center; padding:13px; gap:0; }
      .nav-item .label { display:none; }
      .main { margin-left:78px; }
      .content { padding: 18px; }
    }

    /* ---------- Buttons & inputs ---------- */
    button {
      font-family:inherit; font-weight:600; font-size:15px; cursor:pointer;
      border:none; border-radius:11px; padding:12px 18px; transition: transform .12s, filter .15s, background .15s;
    }
    button:active { transform: translateY(1px); }
    .icon-btn { background: var(--surface-2); border:1px solid var(--border); color:var(--text); padding:10px 13px; font-size:17px; }
    .icon-btn:hover { filter: brightness(1.12); }
    .add { background: linear-gradient(135deg, var(--primary), var(--primary-2)); color:#fff; box-shadow:0 8px 18px rgba(198,126,72,0.35); }
    .add:hover { filter: brightness(1.06); }
    .reset { background: rgba(239,68,68,0.14); color:#ff9b9b; border:1px solid rgba(239,68,68,0.30); }
    .reset:hover { background: rgba(239,68,68,0.22); }
    .seg-btn { background: var(--surface-2); border:1px solid var(--border); color:var(--text); padding:9px 16px; border-radius:10px; cursor:pointer; font-size:14px; font-weight:600; }
    .seg-btn:hover { filter: brightness(1.1); }

    input, select {
      font-family:inherit; font-size:15px; color:var(--text);
      background: var(--input-bg); border:1px solid var(--border);
      border-radius:11px; padding:13px 15px; outline:none; transition: border .15s, background .15s;
    }
    input::placeholder { color:#6b7689; }
    input:focus, select:focus { border-color: var(--primary); background: rgba(198,126,72,0.08); }
    #amount { flex:1.2; min-width:120px; }
    #category { flex:1; min-width:120px; }
    #date { flex:1; min-width:140px; }
    .month-sel { padding:10px 13px; font-size:14px; cursor:pointer; }
    #date::-webkit-calendar-picker-indicator { filter: invert(0.8); cursor:pointer; }
    :root[data-theme="light"] #date::-webkit-calendar-picker-indicator { filter: invert(0.45); }

    /* ---------- Cards ---------- */
    .card {
      background: var(--surface); border:1px solid var(--border);
      border-radius: var(--radius); padding:24px 26px; box-shadow: var(--shadow);
      animation: rise .45s ease both; transition: background .3s, border-color .3s;
    }
    @keyframes rise { from { opacity:0; transform: translateY(10px); } to { opacity:1; transform:none; } }
    .card-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:18px; gap:10px; flex-wrap:wrap; }
    h2 { font-size:16px; font-weight:700; margin:0; }
    .muted { color: var(--muted); font-size:14px; }
    .grid { display:grid; gap:18px; }
    .grid.two { grid-template-columns: 1fr 1fr; }
    .grid.side { grid-template-columns: 1.1fr 0.9fr; align-items:start; }
    .col { display:flex; flex-direction:column; gap:18px; }
    @media (max-width: 820px) { .grid.two, .grid.side { grid-template-columns: 1fr; } }

    /* ---------- KPI tiles ---------- */
    .kpis { display:grid; grid-template-columns: repeat(auto-fit, minmax(195px,1fr)); gap:18px; margin-bottom:18px; }
    .kpi {
      position:relative; overflow:hidden; background: var(--surface);
      border:1px solid var(--border); border-radius: var(--radius);
      padding:20px 22px; box-shadow: var(--shadow); animation: rise .45s ease both;
    }
    .kpi::after {
      content:''; position:absolute; right:-30px; top:-30px; width:96px; height:96px;
      border-radius:50%; background: radial-gradient(circle, rgba(198,126,72,0.22), transparent 70%);
    }
    .k-label { font-size:11px; text-transform:uppercase; letter-spacing:0.10em; color:var(--muted); }
    .k-value { font-size:30px; font-weight:800; margin-top:9px; letter-spacing:-0.02em; }
    .k-sub { font-size:13px; color:var(--muted); margin-top:6px; }
    .kpi.accent .k-value {
      background: linear-gradient(135deg, var(--primary-2), #e0a878);
      -webkit-background-clip:text; background-clip:text; color:transparent;
    }
    .k-sub.up { color:#fca5a5; } .k-sub.down { color:#86efac; }
    :root[data-theme="light"] .k-sub.up { color:#dc2626; } :root[data-theme="light"] .k-sub.down { color:#059669; }

    /* ---------- Quick-add shortcuts ---------- */
    .chips { display:flex; flex-wrap:wrap; gap:10px; }
    .chip {
      display:inline-flex; align-items:center; gap:9px; padding:11px 16px;
      border-radius:99px; border:1px solid var(--border); background: var(--surface-2);
      color: var(--text); font-size:14px; font-weight:500; cursor:pointer;
      transition: transform .12s, border-color .15s, background .15s;
    }
    .chip:hover { border-color: var(--primary); transform: translateY(-1px); }
    .chip:active { transform: translateY(0); }

    /* ---------- Expense list / table ---------- */
    .entries { list-style:none; padding:0; margin:0; display:flex; flex-direction:column; gap:9px; }
    .entry {
      display:flex; align-items:center; gap:13px; background: var(--surface-2);
      border:1px solid var(--border); border-radius:12px; padding:12px 15px;
      transition: transform .12s, border-color .15s;
    }
    .entry:hover { border-color: rgba(198,126,72,0.5); transform: translateX(2px); }
    .entry .amt { font-weight:700; min-width:82px; font-size:16px; }
    .entry .cat { display:inline-flex; align-items:center; gap:7px; background: var(--chip-bg); border-radius:20px; padding:4px 12px; font-size:13px; }
    .dot { width:9px; height:9px; border-radius:50%; display:inline-block; flex:none; }
    .entry .dt { font-size:13px; color:var(--muted); }
    .entry .spacer { flex:1; }
    .mini { padding:8px 13px; font-size:13px; border-radius:9px; }
    .edit { background: rgba(16,185,129,0.16); color:#6ee7b7; }
    .edit:hover { background: rgba(16,185,129,0.26); }
    .del  { background: rgba(239,68,68,0.16); color:#fca5a5; }
    .del:hover { background: rgba(239,68,68,0.26); }
    .save { background: linear-gradient(135deg, var(--primary), var(--primary-2)); color:#fff; }
    .cancel { background: rgba(255,255,255,0.10); color:var(--text); }
    :root[data-theme="light"] .cancel { background: rgba(15,23,42,0.08); }

    /* ---------- Charts ---------- */
    .chart-card { min-height: 330px; }
    .donut-wrap { display:flex; justify-content:center; margin:6px 0 4px; }
    .donut { width:220px; height:220px; }
    .donut circle { transition: stroke-dasharray .55s cubic-bezier(.22,1,.36,1); }
    .donut-total { fill: var(--text); font-size:14px; font-weight:800; }
    .donut-sub { fill: var(--muted); font-size:6.5px; letter-spacing:0.5px; text-transform:uppercase; }
    .legend { margin-top:18px; padding-top:16px; border-top:1px solid var(--border); display:flex; flex-direction:column; gap:9px; }
    .leg-row { display:flex; align-items:center; justify-content:space-between; font-size:14px; padding:4px 0; }
    .leg-name { display:inline-flex; align-items:center; gap:9px; font-weight:600; }
    .leg-val { color:var(--muted); font-weight:600; }
    .bar { margin-bottom:16px; padding-bottom:14px; border-bottom:1px solid var(--border); }
    .bar:last-child { margin-bottom:0; padding-bottom:0; border-bottom:none; }
    .bar-top { display:flex; align-items:center; justify-content:space-between; margin-bottom:9px; font-size:14px; }
    .bar-name { display:inline-flex; align-items:center; gap:9px; font-weight:600; }
    .bar-val { color:var(--muted); font-weight:600; }
    .bar-track { height:13px; background: rgba(255,255,255,0.06); border-radius:99px; overflow:hidden; }
    :root[data-theme="light"] .bar-track { background: rgba(15,23,42,0.08); }
    .bar-fill { height:100%; border-radius:99px; width:0; transition: width .55s cubic-bezier(.22,1,.36,1); }
    .empty { color:var(--muted); font-size:14px; text-align:center; padding:32px 10px; }
    #msg { min-height:18px; font-size:14px; margin-top:14px; font-weight:500; }
    #msg.ok { color:#86efac; } #msg.err { color:#fca5a5; }
    :root[data-theme="light"] #msg.ok { color:#047857; } :root[data-theme="light"] #msg.err { color:#b91c1c; }
    .row { display:flex; gap:11px; flex-wrap:wrap; }
    .e-amt { width:90px; } .e-cat { width:110px; } .e-dt { width:140px; }

    .view { display:none; }
    .view.active { display:block; animation: fade .35s ease; }
    @keyframes fade { from { opacity:0; transform: translateY(6px); } to { opacity:1; transform:none; } }
    .setting-row { display:flex; align-items:center; justify-content:space-between; padding:15px 0; border-bottom:1px solid var(--border); }
    .setting-row:last-child { border-bottom:none; }
  </style>
</head>
<body>
  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="brand">
      <div class="logo">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12a9 9 0 1 1-9-9v9z"/><path d="M12 3a9 9 0 0 1 9 9h-9z"/>
        </svg>
      </div>
      <div class="brand-text">
        <div class="brand-name">Expense Tracker</div>
        <div class="brand-sub">finance dashboard</div>
      </div>
    </div>
    <nav class="nav">
      <div class="nav-item active" data-view="dashboard">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
        <span class="label">Dashboard</span>
      </div>
      <div class="nav-item" data-view="transactions">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M3 12h18M3 18h12"/></svg>
        <span class="label">Transactions</span>
      </div>
      <div class="nav-item" data-view="statistics">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a9 9 0 1 1-9-9v9z"/><path d="M12 3a9 9 0 0 1 9 9h-9z"/></svg>
        <span class="label">Statistics</span>
      </div>
      <div class="nav-item" data-view="settings">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        <span class="label">Settings</span>
      </div>
    </nav>
    <div class="sidebar-foot">v8 · localhost</div>
  </aside>

  <!-- Main -->
  <div class="main">
    <header class="topbar">
      <div class="title" id="viewTitle">Dashboard</div>
      <div class="top-actions">
        <select id="monthFilter" class="month-sel" title="Filter by month"></select>
        <button class="icon-btn" id="themeToggle" title="Toggle theme">☀️</button>
      </div>
    </header>

    <div class="content">
      <!-- DASHBOARD -->
      <section class="view active" id="view-dashboard">
        <div class="kpis">
          <div class="kpi accent"><div class="k-label">Total Spent</div><div class="k-value" id="kpiTotal">$0.00</div><div class="k-sub" id="kpiTotalSub">all time</div></div>
          <div class="kpi"><div class="k-label">Entries</div><div class="k-value" id="kpiCount">0</div><div class="k-sub">expenses logged</div></div>
          <div class="kpi"><div class="k-label">Top Category</div><div class="k-value" id="kpiTop" style="font-size:22px;">—</div><div class="k-sub">highest spend</div></div>
          <div class="kpi"><div class="k-label">Avg / Entry</div><div class="k-value" id="kpiAvg">$0.00</div><div class="k-sub">per expense</div></div>
          <div class="kpi"><div class="k-label">This Month</div><div class="k-value" id="kpiMonth">$0.00</div><div class="k-sub" id="kpiMonthSub">vs last month</div></div>
        </div>

        <!-- ⚡ Quick-add shortcuts -->
        <div class="card" style="margin-bottom:18px;">
          <div class="card-head"><h2>⚡ Quick Add</h2><span class="muted">tap a category, type an amount, press Add</span></div>
          <div class="chips" id="quickChips"></div>
          <div class="row" id="quickRow" style="margin-top:16px; display:none;">
            <input id="quickAmount" type="text" placeholder="Amount e.g. 4.50" style="max-width:220px;" />
            <span class="muted" id="quickCatLabel"></span>
            <button class="add" id="quickAddBtn">Add Expense</button>
            <button class="cancel" id="quickCancel" style="padding:12px 16px;">✕</button>
          </div>
        </div>

        <div class="grid side">
          <div class="card">
            <div class="card-head"><h2>Recent Expenses</h2><span class="muted" id="countDash">0 entries</span></div>
            <ul class="entries" id="dashList"></ul>
          </div>
          <div class="card chart-card">
            <div class="card-head"><h2>🥧 Spending by Category</h2><span class="muted">share of total spend</span></div>
            <div id="chartPie"></div>
          </div>
        </div>

        <div class="grid two">
          <div class="card chart-card">
            <div class="card-head"><h2>📊 Category Breakdown</h2><span class="muted">amount per category</span></div>
            <div id="chartBars"></div>
          </div>
          <div class="card">
            <div class="card-head"><h2>📈 Monthly Trend</h2><span class="muted">last 6 months</span></div>
            <div id="trendDash"></div>
          </div>
        </div>
      </section>

      <!-- TRANSACTIONS -->
      <section class="view" id="view-transactions">
        <div class="grid two">
          <div class="card">
            <div class="card-head"><h2>Add Expense</h2></div>
            <div class="row">
              <input id="amount" type="text" placeholder="Amount e.g. 12.50" />
              <input id="category" list="cats" placeholder="Category" />
            </div>
            <div class="row" style="margin-top:11px;">
              <input id="date" type="date" />
              <button class="add" id="addBtn" style="flex:1;">Add Expense</button>
            </div>
            <div id="msg"></div>
          </div>
          <div class="card">
            <div class="card-head"><h2>💡 Tip</h2></div>
            <p class="muted" style="line-height:1.7; margin:0;">Add an amount and pick a category, then choose a date (defaults to today). Use <b>Edit</b> to fix a mistake or <b>Delete</b> to remove an entry. Everything saves automatically to <code>expenses.json</code>.</p>
          </div>
        </div>
        <div class="card" style="margin-top:18px;">
          <div class="card-head"><h2>All Transactions</h2><span class="muted" id="countTxn">0 entries</span></div>
          <ul class="entries" id="txnList"></ul>
        </div>
      </section>

      <!-- STATISTICS -->
      <section class="view" id="view-statistics">
        <div class="grid two">
          <div class="card chart-card">
            <div class="card-head"><h2>🥧 Spending by Category</h2><span class="muted">share of total spend</span></div>
            <div id="chartPie2"></div>
          </div>
          <div class="card chart-card">
            <div class="card-head"><h2>📊 Category Breakdown</h2><span class="muted">amount per category</span></div>
            <div id="chartBars2"></div>
          </div>
        </div>
        <div class="card" style="margin-top:18px;">
          <div class="card-head"><h2>📈 Monthly Trend</h2><span class="muted">last 6 months</span></div>
          <div id="trend"></div>
        </div>
      </section>

      <!-- SETTINGS -->
      <section class="view" id="view-settings">
        <div class="card" style="max-width:640px;">
          <div class="card-head"><h2>Settings</h2></div>
          <div class="setting-row">
            <div><div style="font-weight:600;">Theme</div><div class="muted">Switch between dark and light</div></div>
            <button class="seg-btn active" id="themeToggle2">🌙 Dark</button>
          </div>
          <div class="setting-row">
            <div><div style="font-weight:600;">Storage</div><div class="muted" id="storageInfo">—</div></div>
            <span class="muted">expenses.json</span>
          </div>
          <div class="setting-row">
            <div><div style="font-weight:600;">Demo Data</div><div class="muted">Fill the app with sample expenses to explore the charts</div></div>
            <button class="seg-btn" id="demoBtn">✨ Load Demo Data</button>
          </div>
          <div class="setting-row">
            <div><div style="font-weight:600; color:#ff9b9b;">Danger Zone</div><div class="muted">Permanently delete all expenses</div></div>
            <button class="reset" id="resetBtn">🧹 Clear All</button>
          </div>
        </div>
      </section>
    </div>
  </div>

  <datalist id="cats">
    <option value="Food"></option><option value="Transport"></option>
    <option value="Shopping"></option><option value="Bills"></option>
    <option value="Entertainment"></option><option value="Health"></option>
    <option value="Other"></option>
  </datalist>

  <script>
    window.__SEED_DATA__ = /*__SEED__*/;
    const $ = id => document.getElementById(id);
    let currentState = window.__SEED_DATA__ || { expenses: [], total: 0, count: 0, by_category: {} };
    let currentView = { expenses: [], total: 0, count: 0, by_category: {} };
    let editingId = null;
    let quickCat = 'Food';
    const CATEGORIES = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Other"];

    // Local demo dataset — used as a fallback if the server call can't reach
    // the backend, so the UI still populates for inspection.
    const DEMO_DATA = {
      expenses: [
        {id:1,amount:12.5,category:"Food",date:"2026-07-18"},
        {id:2,amount:4.0,category:"Transport",date:"2026-07-17"},
        {id:3,amount:59.99,category:"Shopping",date:"2026-07-15"},
        {id:4,amount:120.0,category:"Bills",date:"2026-07-10"},
        {id:5,amount:25.0,category:"Entertainment",date:"2026-07-12"},
        {id:6,amount:8.75,category:"Food",date:"2026-07-19"},
        {id:7,amount:35.0,category:"Health",date:"2026-07-05"},
        {id:8,amount:6.5,category:"Transport",date:"2026-07-14"},
        {id:9,amount:22.3,category:"Food",date:"2026-06-20"},
        {id:10,amount:115.0,category:"Bills",date:"2026-06-12"},
        {id:11,amount:9.25,category:"Transport",date:"2026-06-25"},
        {id:12,amount:40.0,category:"Shopping",date:"2026-05-18"},
        {id:13,amount:18.0,category:"Entertainment",date:"2026-05-22"},
        {id:14,amount:7.5,category:"Food",date:"2026-05-09"}
      ],
      total: 483.79, count: 14,
      by_category: { "Food":51.05, "Transport":19.75, "Shopping":99.99, "Bills":235.0, "Entertainment":43.0, "Health":35.0 }
    };

    const CAT_COLORS = {
      Food:'#f59e0b', Transport:'#38bdf8', Shopping:'#ec4899', Bills:'#a78bfa',
      Entertainment:'#34d399', Health:'#fb7185', Other:'#94a3b8'
    };
    function colorFor(cat) {
      if (CAT_COLORS[cat]) return CAT_COLORS[cat];
      let h = 0; for (const ch of cat) h = (h * 31 + ch.charCodeAt(0)) % 360;
      return `hsl(${h} 70% 62%)`;
    }

    // ---------- 🌗 Theme ----------
    function applyTheme(t) {
      document.documentElement.setAttribute('data-theme', t);
      localStorage.setItem('theme', t);
      $('themeToggle').textContent = t === 'dark' ? '☀️' : '🌙';
      $('themeToggle2').textContent = t === 'dark' ? '🌙 Dark' : '☀️ Light';
    }
    applyTheme(localStorage.getItem('theme') || 'dark');
    $('themeToggle').onclick = () => applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');
    $('themeToggle2').onclick = () => applyTheme(document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark');

    // ---------- View switching ----------
    const TITLES = { dashboard:'Dashboard', transactions:'Transactions', statistics:'Statistics', settings:'Settings' };
    document.querySelectorAll('.nav-item').forEach(n => {
      n.onclick = () => {
        document.querySelectorAll('.nav-item').forEach(x => x.classList.toggle('active', x === n));
        document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
        const v = n.dataset.view;
        $('view-' + v).classList.add('active');
        $('viewTitle').textContent = TITLES[v];
      };
    });

    $('date').value = new Date().toISOString().slice(0, 10);

    function setMsg(text, kind) {
      $('msg').textContent = text || '';
      $('msg').className = kind || '';
    }

    async function api(path, payload) {
      const res = await fetch(path, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      return res.json();
    }

    // ---------- month helpers ----------
    function ym(y, m) { return y + '-' + String(m + 1).padStart(2, '0'); }
    function monthlyTotals(state) {
      const tot = {};
      for (const e of state.expenses) if (e.date) { const k = e.date.slice(0,7); tot[k] = (tot[k]||0) + e.amount; }
      return tot;
    }

    // ---------- filter ----------
    function filteredView(state, month) {
      let exps = state.expenses;
      if (month && month !== 'all') exps = exps.filter(e => e.date && e.date.startsWith(month));
      const t = exps.reduce((s,e)=>s+e.amount,0);
      const byCat = {};
      for (const e of exps) byCat[e.category] = (byCat[e.category]||0) + e.amount;
      return { expenses: exps, total: Math.round(t*100)/100, count: exps.length, by_category: byCat };
    }
    function populateMonths(state) {
      const months = [...new Set(state.expenses.map(e => e.date ? e.date.slice(0,7) : ''))].filter(Boolean).sort().reverse();
      const sel = $('monthFilter'); const cur = sel.value || 'all';
      sel.innerHTML = '<option value="all">All time</option>' + months.map(m => `<option value="${m}">${m}</option>`).join('');
      sel.value = months.includes(cur) ? cur : 'all';
    }

    // ---------- charts ----------
    function renderDonut(view, boxId) {
      const box = $(boxId); const bc = view.by_category || {};
      const keys = Object.keys(bc).sort((a,b)=>bc[b]-bc[a]); const total = view.total;
      if (!keys.length || total <= 0) { box.innerHTML = '<div class="empty">No data yet — load Demo Data or add an expense to see your breakdown.</div>'; return; }
      const R=52, C=2*Math.PI*R; let offset=0, arcs='';
      for (const k of keys) {
        const len=(bc[k]/total)*C; const c=colorFor(k);
        arcs += `<circle cx="60" cy="60" r="${R}" fill="none" stroke="${c}" stroke-width="16" stroke-dasharray="${len.toFixed(2)} ${(C-len).toFixed(2)}" stroke-dashoffset="${(-offset).toFixed(2)}" transform="rotate(-90 60 60)" />`;
        offset += len;
      }
      let legend='';
      for (const k of keys) { const pct=((bc[k]/total)*100).toFixed(1);
        legend += `<div class="leg-row"><span class="leg-name"><span class="dot" style="background:${colorFor(k)}"></span>${k}</span><span class="leg-val">$${bc[k].toFixed(2)} · ${pct}%</span></div>`; }
      box.innerHTML = `<div class="donut-wrap"><svg viewBox="0 0 120 120" class="donut">${arcs}<text x="60" y="57" text-anchor="middle" class="donut-total">$${total.toFixed(2)}</text><text x="60" y="72" text-anchor="middle" class="donut-sub">total</text></svg></div><div class="legend">${legend}</div>`;
    }
    function renderBars(view, boxId) {
      const box = $(boxId); const bc = view.by_category || {};
      const keys = Object.keys(bc).sort((a,b)=>bc[b]-bc[a]); const max = Math.max(0, ...keys.map(k=>bc[k]));
      const total = view.total || 0;
      if (!keys.length) { box.innerHTML = '<div class="empty">No data yet — load Demo Data or add an expense to see your breakdown.</div>'; return; }
      let html='';
      for (const k of keys) { const pct = max>0 ? (bc[k]/max*100):0; const share = total>0 ? (bc[k]/total*100):0; const c=colorFor(k);
        html += `<div class="bar"><div class="bar-top"><span class="bar-name"><span class="dot" style="background:${c}"></span>${k}</span><span class="bar-val">$${bc[k].toFixed(2)} · ${share.toFixed(0)}%</span></div><div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:linear-gradient(90deg,${c},${c}aa)"></div></div></div>`; }
      box.innerHTML = html;
    }
    function renderTrend(state, boxId) {
      const box = $(boxId); const mt = monthlyTotals(state); const now = new Date(); const months=[];
      for (let i=5;i>=0;i--){ const d=new Date(now.getFullYear(), now.getMonth()-i, 1); const key=ym(d.getFullYear(), d.getMonth()); months.push({label:d.toLocaleString('en',{month:'short'}), val:Math.round((mt[key]||0)*100)/100}); }
      const max = Math.max(0, ...months.map(m=>m.val)); let html='';
      for (const m of months) { const pct = max>0 ? (m.val/max*100):0;
        html += `<div class="bar"><div class="bar-top"><span class="bar-name">${m.label}</span><span class="bar-val">$${m.val.toFixed(2)}</span></div><div class="bar-track"><div class="bar-fill" style="width:${pct}%;background:linear-gradient(90deg,var(--primary),var(--primary-2))"></div></div></div>`; }
      box.innerHTML = html;
    }

    // ---------- quick-add shortcuts ----------
    function populateChips() {
      const wrap = $('quickChips'); wrap.innerHTML = '';
      for (const c of CATEGORIES) {
        const b = document.createElement('button');
        b.className = 'chip';
        b.innerHTML = `<span class="dot" style="background:${colorFor(c)}"></span>${c}`;
        b.onclick = () => {
          quickCat = c;
          $('quickCatLabel').textContent = '→ ' + c;
          $('quickRow').style.display = 'flex';
          $('quickAmount').value = '';
          $('quickAmount').focus();
        };
        wrap.appendChild(b);
      }
    }
    async function doQuickAdd() {
      const amt = $('quickAmount').value;
      const r = await api('/add', { amount: amt, category: quickCat, date: $('date').value });
      render(r);
      if (r.status === 'invalid') { setMsg(r.message, 'err'); }
      else { $('quickAmount').value = ''; $('quickAmount').focus(); }
    }
    $('quickAddBtn').onclick = doQuickAdd;
    $('quickAmount').addEventListener('keydown', e => { if (e.key === 'Enter') doQuickAdd(); });
    $('quickCancel').onclick = () => { $('quickRow').style.display = 'none'; $('quickAmount').value = ''; };

    // ---------- entry list builder ----------
    function buildEntries(containerId, arr, fullState) {
      const ul = $(containerId); ul.innerHTML='';
      if (!arr.length) { ul.innerHTML = '<div class="empty">No expenses here yet. ✨</div>'; return; }
      for (const e of arr) {
        const li = document.createElement('li'); li.className='entry'; const c=colorFor(e.category);
        if (editingId === e.id) {
          li.innerHTML = `<input class="e-amt" type="text" value="${e.amount}" /><input class="e-cat" list="cats" value="${e.category}" /><input class="e-dt" type="date" value="${e.date}" /><span class="spacer"></span><button class="mini save">Save</button><button class="mini cancel">Cancel</button>`;
          li.querySelector('.save').onclick = async () => {
            const r = await api('/edit', { id:e.id, amount:li.querySelector('.e-amt').value, category:li.querySelector('.e-cat').value, date:li.querySelector('.e-dt').value });
            editingId=null; render(r); setMsg(r.message, r.status==='invalid'?'err':'ok');
          };
          li.querySelector('.cancel').onclick = () => { editingId=null; render(fullState); };
        } else {
          li.innerHTML = `<span class="amt">$${e.amount.toFixed(2)}</span><span class="cat"><span class="dot" style="background:${c}"></span>${e.category}</span><span class="dt">${e.date}</span><span class="spacer"></span><button class="mini edit">Edit</button><button class="mini del">Delete</button>`;
          li.querySelector('.edit').onclick = () => { editingId=e.id; render(fullState); };
          li.querySelector('.del').onclick = async () => { const r = await api('/delete', { id:e.id }); render(r); setMsg(r.message,'ok'); };
        }
        ul.appendChild(li);
      }
    }

    // ---------- main render ----------
    function render(state) {
      currentState = state; populateMonths(state);
      const view = filteredView(state, $('monthFilter').value); currentView = view;
      const isFiltered = $('monthFilter').value !== 'all'; const mt = monthlyTotals(state);

      $('kpiTotal').textContent = '$' + view.total.toFixed(2);
      $('kpiTotalSub').textContent = isFiltered ? $('monthFilter').value : 'all time';
      $('kpiCount').textContent = view.count;
      let top='—', topVal=0; for (const k of Object.keys(view.by_category)) if (view.by_category[k]>topVal){topVal=view.by_category[k];top=k;}
      $('kpiTop').textContent = top;
      $('kpiAvg').textContent = view.count ? '$'+(view.total/view.count).toFixed(2) : '$0.00';
      const sub = $('kpiMonthSub'); sub.className='k-sub';
      const now=new Date(); const cmTotal=mt[ym(now.getFullYear(),now.getMonth())]||0; const lmTotal=mt[ym(now.getFullYear(),now.getMonth()-1)]||0;
      $('kpiMonth').textContent = '$'+cmTotal.toFixed(2);
      if (lmTotal>0){ const pct=((cmTotal-lmTotal)/lmTotal)*100; const arrow=pct>0?'▲':(pct<0?'▼':'—'); sub.classList.add(pct>0?'up':(pct<0?'down':'')); sub.textContent=`${arrow} ${Math.abs(pct).toFixed(1)}% vs last`; }
      else if (cmTotal>0){ sub.classList.add('up'); sub.textContent='▲ first month'; }
      else sub.textContent='vs last month';

      $('countDash').textContent = view.count + (view.count===1?' entry':' entries');
      $('countTxn').textContent = view.count + (view.count===1?' entry':' entries');
      $('storageInfo').textContent = view.count + ' expense(s) saved';

      renderDonut(view, 'chartPie');
      renderBars(view, 'chartBars');
      renderDonut(view, 'chartPie2');
      renderBars(view, 'chartBars2');
      renderTrend(state, 'trend');
      renderTrend(state, 'trendDash');
      buildEntries('dashList', [...view.expenses].reverse().slice(0,8), state);
      buildEntries('txnList', view.expenses, state);
    }

    async function addExpense() {
      const amt=$('amount').value, cat=$('category').value, dt=$('date').value;
      $('amount').value=''; $('category').value=''; $('amount').focus();
      const r = await api('/add', { amount:amt, category:cat, date:dt });
      render(r); setMsg(r.message, r.status==='invalid'?'err':'ok');
    }
    $('addBtn').onclick = addExpense;
    $('amount').addEventListener('keydown', e=>{ if(e.key==='Enter') addExpense(); });
    $('category').addEventListener('keydown', e=>{ if(e.key==='Enter') addExpense(); });
    $('date').addEventListener('keydown', e=>{ if(e.key==='Enter') addExpense(); });
    $('monthFilter').onchange = () => render(currentState);

    $('resetBtn').onclick = async () => {
      if (!confirm('Clear ALL expenses? This cannot be undone.')) return;
      const r = await api('/reset', {}); render(r); setMsg(r.message,'ok');
    };

    $('demoBtn').onclick = async () => {
      const btn = $('demoBtn'); const old = btn.textContent;
      btn.textContent = 'Loading…'; btn.disabled = true;
      try {
        const r = await api('/demo', {});
        render(r);
        btn.textContent = '✓ Loaded';
      } catch (e) {
        currentState = DEMO_DATA; render(DEMO_DATA);
        btn.textContent = '✓ Loaded (local)';
      }
      setTimeout(() => { btn.textContent = old; btn.disabled = false; }, 1600);
    };

    populateChips();
    render(currentState);
    fetch('/summary').then(x => x.json()).then(render);
  </script>
</body>
</html>"""


# ------------------------------------------------------------
# Web server
# ------------------------------------------------------------
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, content_type="application/json"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/summary":
            self._send(200, json.dumps(snapshot("summary")))
            return
        self._send(200, PAGE.replace("/*__SEED__*/", json.dumps(snapshot("summary"))), "text/html; charset=utf-8")

    def do_POST(self):
        if self.path not in ("/add", "/edit", "/delete", "/reset", "/demo", "/summary"):
            self._send(404, '{"status":"invalid","message":"not found"}')
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._send(400, '{"status":"invalid","message":"Bad request"}')
            return
        if self.path == "/add":
            result = add_expense(payload.get("amount", ""), payload.get("category", "Other"), payload.get("date", ""))
        elif self.path == "/edit":
            result = edit_expense(payload.get("id"), payload.get("amount", ""), payload.get("category", ""), payload.get("date", ""))
        elif self.path == "/delete":
            result = delete_expense(payload.get("id"))
        elif self.path == "/reset":
            result = reset_all()
        elif self.path == "/demo":
            result = load_demo()
        else:
            result = snapshot("summary")
        self._send(200, json.dumps(result))

    def log_message(self, fmt, *args):
        pass


def main():
    load_data()
    host, port = "localhost", 8000
    server = ThreadingHTTPServer((host, port), Handler)
    print("=" * 50)
    print("  Expense Tracker v8 (bigger, fuller dashboard) is running 📊")
    print(f"  Open:  http://{host}:{port}")
    print(f"  Saving to: {DATA_FILE} (loaded {len(expenses)} expense(s))")
    print("  Press Ctrl+C here to stop the server.")
    print("=" * 50)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped. Your data is saved. Goodbye!")
        server.shutdown()


if __name__ == "__main__":
    main()
