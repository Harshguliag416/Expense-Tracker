<div align="center">

# 💰 Expense Tracker

**A clean, single-file expense tracker with a premium dashboard — KPIs, a pie + bar breakdown, a monthly trend, quick-add shortcuts, and dark/light themes. No frameworks, no build step, no dependencies — just Python.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org/downloads)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-lightgrey?style=for-the-badge)](app.py)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-informational?style=for-the-badge)](#)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Netlify-00c7b7?style=for-the-badge)](https://radiant-rabanadas-ae2a4c.netlify.app)

▶ **Live demo:** https://radiant-rabanadas-ae2a4c.netlify.app — try it instantly, no install (your data stays in the browser).

</div>

---

## ✨ Highlights

- 📊 **Premium dashboard** — KPI tiles (total spent, entries, top category, avg/entry, this month) with a sidebar nav and glassy cards.
- 🥧📊 **Pie *and* bar charts** — spending by category shown as a donut (share of total) and horizontal bars (amount + % of total), side by side.
- 📈 **Monthly trend** — last 6 months of spending at a glance.
- ⚡ **Quick Add** — tap a category chip, type an amount, hit Add. Done in two clicks.
- 🗓️ **Month filter** — scope the KPIs, charts, and list to any single month, or view all time.
- 📆 **This vs last month** — KPI with an up/down delta indicator.
- 🌗 **Light / Dark** — toggle remembered in `localStorage`.
- ✏️ **Edit / Delete** — fix or remove any expense inline; everything auto-saves.
- 💾 **Auto-save** — expenses persist to `expenses.json` (created on first run).
- 🧪 **Demo Mode** — one click fills the app with realistic sample data so you can explore instantly.
- 🪶 **Zero dependencies** — built only with the Python standard library + vanilla JS.

---

## 🚀 Getting Started

No install, no `pip`. You just need Python 3.8+.

```bash
# from the project folder
python3 app.py
```

Then open **http://localhost:8000** in your browser.

> The app prints the URL and the number of loaded expenses on startup. Stop it any time with `Ctrl+C` — your data is already saved.

### 🧰 What you can do

| Action | How |
| :--- | :--- |
| Add an expense | **Transactions** tab → enter amount + category (+ optional date) → *Add Expense* |
| Add in one tap | **Dashboard** → tap a category chip → type amount → *Add Expense* |
| Edit / Delete | Hover any entry → *Edit* (change amount/category/date) or *Delete* |
| Filter by month | Use the month picker in the top bar |
| Switch theme | ☀️ / 🌙 button in the top bar (remembered) |
| See charts | **Dashboard** (overview) or **Statistics** (full breakdown) |
| Wipe everything | **Settings → Clear All** (with confirmation) |

---

## 🎯 Demo Mode — check how it works

Want to see the dashboard, charts, and trends populated **without typing anything**? Use **Demo Mode**:

1. Open **Settings** (sidebar).
2. Click **✨ Load Demo Data**.

Prefer not to run anything locally? Open the **[live demo](https://radiant-rabanadas-ae2a4c.netlify.app)** and click *Load Demo Data* — no install needed.

The app instantly seeds **14 sample expenses** across 6 categories and 3 months (Food, Transport, Shopping, Bills, Entertainment, Health). Your KPIs, pie chart, bar chart, monthly trend, and transaction list all fill in right away — perfect for a quick tour or a screenshot.

> 💡 **Tip for reviewers:** if you just want to eyeball the UI, Demo Mode is the fastest way. It replaces any existing data with the same consistent sample set every time, so the result is predictable. To start blank again, hit **Settings → Clear All**.

The page also embeds the current data on load, and the Demo button has a local fallback — so the charts populate for inspection even if the browser can't reach the backend.

---

## 🛠️ Tech

- **Backend:** Python standard library only — `http.server` (threaded), `json`, `datetime`. No Flask, no database.
- **Frontend:** A single HTML page with vanilla JavaScript and inline SVG charts. No bundler, no CDN dependencies for logic.
- **Storage:** a plain `expenses.json` file (`{"next_id": 1, "expenses": [...]}`).

## 📁 Project structure

```
expense_tracker/
├── app.py          # the entire app — server + UI in one file
├── expenses.json   # auto-created; your saved expenses (git-ignored)
├── .gitignore
├── LICENSE         # MIT
└── README.md
```

## 🤝 License

Released under the [MIT License](LICENSE).
