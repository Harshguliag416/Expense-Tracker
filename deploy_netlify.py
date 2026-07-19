#!/usr/bin/env python3
"""Deploy the static Expense Tracker (index.html) to Netlify via the API.

Usage: NETLIFY_TOKEN=xxx python3 deploy_netlify.py
"""
import os, json, zipfile, io, time, urllib.request, urllib.error

TOKEN = os.environ['NETLIFY_TOKEN']
API = 'https://api.netlify.com/api/v1'


def req(method, url, data=None, headers=None):
    h = {'Authorization': 'Bearer ' + TOKEN}
    if headers:
        h.update(headers)
    r = urllib.request.Request(url, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.read().decode(), resp.status
    except urllib.error.HTTPError as e:
        return e.read().decode(), e.code


# 1) create site (try a nice name, fall back to auto-generated)
name = 'expense-tracker-harsh'
out, st = req('POST', API + '/sites', data=json.dumps({'name': name}).encode(),
              headers={'Content-Type': 'application/json'})
if st >= 400:
    print('name taken, creating without name')
    out, st = req('POST', API + '/sites', data=b'{}', headers={'Content-Type': 'application/json'})
site = json.loads(out)
site_id, url = site['id'], site.get('url')
print('site:', site_id, url)

# 2) zip index.html
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write('index.html')
zip_bytes = buf.getvalue()

# 3) deploy (multipart drag-drop)
boundary = '----expensetrackerboundary'
body = b'--' + boundary.encode() + b'\r\n'
body += b'Content-Disposition: form-data; name="file"; filename="deploy.zip"\r\n'
body += b'Content-Type: application/zip\r\n\r\n'
body += zip_bytes + b'\r\n'
body += b'--' + boundary.encode() + b'--\r\n'
out, st = req('POST', f'{API}/sites/{site_id}/deploys', data=body,
              headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
dep = json.loads(out)
dep_id = dep.get('id')
print('deploy created:', dep_id, 'state:', dep.get('state'))

# 4) poll until live
state = dep.get('state')
for _ in range(40):
    if state in ('ready',):
        break
    time.sleep(1)
    out, _ = req('GET', f'{API}/sites/{site_id}/deploys/{dep_id}')
    state = json.loads(out).get('state')
    print('  polling...', state)
else:
    print('WARN: deploy still', state)

print('LIVE_URL=' + (url or ''))
