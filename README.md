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

