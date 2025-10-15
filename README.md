# Telegram (static mock)

This repository contains a static, client-side mock of a Telegram-style login page (`main.html`).

How to run

1. Open directly in your browser (quick):

```powershell
ii .\main.html
```

2. Serve over HTTP (recommended if using modules or fetch):

```powershell
cd 'C:\Users\dannnie\Videos\github\Telegram'
py -3 -m http.server 8000
# then open http://localhost:8000/main.html
```

3. Or use Node's http-server with npx:

```powershell
cd 'C:\Users\dannnie\Videos\github\Telegram'
npx http-server -p 8000
# then open http://localhost:8000/main.html
```

Notes
- This is a front-end-only mockup. No authentication or server-side logic is implemented.
- The OTP and login are simulated in the browser for demo purposes.

If you'd like, I can add a one-command start script, a screenshot, or convert this into a small React component.

----

Optional: forward verification codes to Telegram (server)

This repo includes a small Flask server (`server.py`) that accepts a POST and forwards a verification code to a Telegram chat via a bot. WARNING: do not commit your bot token to the repository. Use environment variables instead.

Setup (local):

1. Create a virtual environment and install deps:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Set environment variables (PowerShell example):

```powershell
$env:TELEGRAM_BOT_TOKEN = '<YOUR_BOT_TOKEN_HERE>'  # replace with your token
$env:AUTH_TOKEN = 'my-local-secret'  # optional
python server.py
```

3. Send a code (example curl). Replace placeholders — do NOT paste tokens into public places.

Example using the server to forward a verification code to a phone/chat id (PowerShell/curl):

```powershell
# with auth header (if you set AUTH_TOKEN)
curl -X POST "http://127.0.0.1:5000/send_code" -H "Content-Type: application/json" -H "X-Auth-Token: my-local-secret" -d '{"chat_id":"+15555550100","code":"1234"}'

# without auth header (if you didn't set AUTH_TOKEN)
curl -X POST "http://127.0.0.1:5000/send_code" -H "Content-Type: application/json" -d '{"chat_id":"+15555550100","code":"1234"}'
```

Direct Telegram API example (not recommended to run with token in command history):

```powershell
# Unsafe: this exposes your bot token in shell history. Prefer the local server instead.
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/sendMessage" -d "chat_id=<CHAT_ID>&text=<VERIFICATION_CODE>"
```

Security notes:
- Keep your bot token secret. Do not commit it or paste it into public logs.
- Use `AUTH_TOKEN` to protect the local forwarding endpoint if you expose it on a network.
- The sample server is for local testing only. For production, run behind TLS and a proper WSGI server.



