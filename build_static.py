#!/usr/bin/env python3
"""Build the static, client-side version of the Expense Tracker for Netlify.

The canonical UI lives in app.py (PAGE). This script reuses that exact markup
and styles but swaps the Python-server data layer for a localStorage-backed one,
so the site runs on Netlify's static CDN with no backend. Run: python3 build_static.py
"""
import app

HTML = app.PAGE

# 1) Neutralize the server-side seed token (no backend in the static build).
HTML = HTML.replace("/*__SEED__*/", "undefined")

# 2) Replace the server API with a localStorage-backed store.
SERVER_API = """    async function api(path, payload) {
      const res = await fetch(path, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload) });
      return res.json();
    }"""

CLIENT_API = r"""    // ---- client-side store (localStorage) for the static Netlify build ----
    const LS_KEY = 'expense_tracker_v1';
    const LS = {
      load() {
        try { const d = JSON.parse(localStorage.getItem(LS_KEY)); if (d && Array.isArray(d.expenses)) return d; } catch (e) {}
        return { next_id: 1, expenses: [] };
      },
      save(d) { try { localStorage.setItem(LS_KEY, JSON.stringify(d)); } catch (e) {} },
      snapshot(status, message) {
        const d = this.load();
        const total = Math.round(d.expenses.reduce((s, e) => s + e.amount, 0) * 100) / 100;
        const by_category = {};
        for (const e of d.expenses) by_category[e.category] = Math.round(((by_category[e.category] || 0) + e.amount) * 100) / 100;
        return { status: status, message: message || '', expenses: d.expenses, total: total, count: d.expenses.length, by_category: by_category };
      }
    };
    async function api(path, payload) {
      const d = LS.load(); let msg = '';
      if (path === '/add') {
        const amt = parseFloat(String(payload.amount).trim());
        if (isNaN(amt)) return LS.snapshot('invalid', 'is not a valid number.');
        if (amt < 0) return LS.snapshot('invalid', 'Amount cannot be negative.');
        d.expenses.push({ id: d.next_id, amount: amt, category: (payload.category || 'Other') || 'Other', date: payload.date || new Date().toISOString().slice(0, 10) });
        d.next_id++; msg = 'Added ' + amt.toFixed(2) + ' under ' + (payload.category || 'Other');
      } else if (path === '/edit') {
        const e = d.expenses.find(x => x.id === Number(payload.id));
        if (!e) return LS.snapshot('invalid', 'No such expense.');
        const amt = parseFloat(String(payload.amount).trim());
        if (isNaN(amt)) return LS.snapshot('invalid', 'Invalid number.');
        if (amt < 0) return LS.snapshot('invalid', 'Amount cannot be negative.');
        e.amount = amt;
        if (payload.category && payload.category.trim()) e.category = payload.category.trim();
        if (payload.date && payload.date.trim()) e.date = payload.date.trim();
        msg = 'Updated expense.';
      } else if (path === '/delete') {
        const i = d.expenses.findIndex(x => x.id === Number(payload.id));
        if (i < 0) return LS.snapshot('invalid', 'No such expense.');
        d.expenses.splice(i, 1); msg = 'Deleted expense.';
      } else if (path === '/reset') {
        d.expenses = []; d.next_id = 1; msg = 'All expenses cleared.';
      } else if (path === '/demo') {
        d.expenses = DEMO_DATA.expenses.map(e => ({ ...e })); d.next_id = DEMO_DATA.expenses.length + 1;
        msg = 'Loaded ' + DEMO_DATA.expenses.length + ' demo expenses.';
      }
      LS.save(d); return LS.snapshot(path.slice(1), msg);
    }"""

assert SERVER_API in HTML, "server api block not found"
HTML = HTML.replace(SERVER_API, CLIENT_API)

# 3) Boot from localStorage instead of fetching the (nonexistent) server.
BOOT = "fetch('/summary').then(x => x.json()).then(render);"
assert BOOT in HTML, "bootstrap fetch not found"
HTML = HTML.replace(BOOT, "render(LS.snapshot('summary'));")

with open("index.html", "w") as f:
    f.write(HTML)

print("wrote index.html:", len(HTML), "bytes")
