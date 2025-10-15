#!/usr/bin/env python3
"""Flask server that issues numeric verification codes and forwards them to Telegram.

Endpoints:
- POST /request_code  -> { chat_id, password? }
    generates a numeric code, stores it in-memory with expiry, and sends via Telegram bot.
- POST /verify_code   -> { chat_id, code }
    verifies the code against the stored value.

Configuration:
- TELEGRAM_BOT_TOKEN (required) set in environment
- AUTH_TOKEN (optional) shared secret required in X-Auth-Token header

This is a demo/local server. Do not expose it publicly without TLS and proper auth.
"""
from flask import Flask, request, jsonify
import logging
from flask_cors import CORS
import os
import requests
import time
import secrets
import json
from pathlib import Path
try:
    from telethon import TelegramClient, errors as telethon_errors
except Exception:
    TelegramClient = None
    telethon_errors = None

app = Flask(__name__)
CORS(app, origins=["http://localhost:8000", "http://127.0.0.1:8000"], supports_credentials=True)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')
CODE_TTL = int(os.environ.get('CODE_TTL_SECONDS', '300'))  # 5 minutes default

TELEGRAM_API = 'https://api.telegram.org/bot{token}/{method}'

# In-memory store: chat_id -> { code: '123456', expires_at: 1234567890 }
CODE_STORE = {}
RATE_STORE = {}  # chat_id -> list[timestamps]
STORE_FILE = Path(os.environ.get('CODE_STORE_FILE', 'code_store.json'))
RATE_LIMIT = int(os.environ.get('RATE_LIMIT', '3'))
RATE_WINDOW = int(os.environ.get('RATE_WINDOW_SECONDS', '900'))  # 15 min
DRY_RUN = os.environ.get('DRY_RUN', '') not in ('', '0', 'False', 'false')
TELETHON_API_ID = os.environ.get('TELETHON_API_ID')
TELETHON_API_HASH = os.environ.get('TELETHON_API_HASH')
TELETHON_SESSION = os.environ.get('TELETHON_SESSION')  # session file base name
TELETHON_CLIENT = None
if TelegramClient and TELETHON_API_ID and TELETHON_API_HASH and TELETHON_SESSION:
    try:
        TELETHON_CLIENT = TelegramClient(TELETHON_SESSION, int(TELETHON_API_ID), TELETHON_API_HASH)
        TELETHON_CLIENT.start()
        logger.info('Telethon client started with session %s', TELETHON_SESSION)
    except Exception as e:
        logger.warning('Failed to start Telethon client: %s', e)

# configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('tg-verify')


def telegram_send_message(token: str, chat_id: str, text: str):
    url = TELEGRAM_API.format(token=token, method='sendMessage')
    logger.info('Sending Telegram message to %s', chat_id)
    resp = requests.post(url, data={'chat_id': chat_id, 'text': text})
    try:
        j = resp.json()
        logger.info('Telegram response status=%s, body=%s', resp.status_code, j)
        return resp.status_code, j
    except Exception:
        logger.warning('Telegram response non-json or error: %s', resp.text)
        return resp.status_code, {'text': resp.text}


def send_via_telethon(chat_id: str, text: str):
    """Send a message using a logged-in Telethon user client.
    chat_id can be a phone in international format or username; Telethon will resolve.
    """
    if not TELETHON_CLIENT:
        return 500, {'error': 'telethon not configured'}
    try:
        # Telethon send_message is synchronous-friendly when using .send_message
        res = TELETHON_CLIENT.send_message(chat_id, text)
        logger.info('Telethon message sent to %s: %s', chat_id, res)
        return 200, {'telethon': 'sent'}
    except Exception as e:
        logger.exception('Telethon send error: %s', e)
        return 500, {'error': str(e)}


def require_auth():
    if AUTH_TOKEN:
        header = request.headers.get('X-Auth-Token', '')
        if header != AUTH_TOKEN:
            return False
    return True


def load_store():
    global CODE_STORE
    try:
        if STORE_FILE.exists():
            with STORE_FILE.open('r', encoding='utf-8') as f:
                data = json.load(f)
            # convert to expected structure and drop expired
            now = time.time()
            for k, v in data.items():
                if v.get('expires_at', 0) > now:
                    CODE_STORE[k] = v
            logger.info('Loaded %s codes from %s', len(CODE_STORE), STORE_FILE)
    except Exception as e:
        logger.warning('Failed to load store: %s', e)


def save_store():
    try:
        tmp = STORE_FILE.with_suffix('.tmp')
        with tmp.open('w', encoding='utf-8') as f:
            json.dump(CODE_STORE, f)
        tmp.replace(STORE_FILE)
    except Exception as e:
        logger.warning('Failed to save store: %s', e)


def check_rate_limit(chat_id: str):
    now = time.time()
    arr = RATE_STORE.get(chat_id, [])
    # drop old
    arr = [t for t in arr if t > now - RATE_WINDOW]
    if len(arr) >= RATE_LIMIT:
        RATE_STORE[chat_id] = arr
        return False, len(arr)
    arr.append(now)
    RATE_STORE[chat_id] = arr
    return True, len(arr)


# load persisted store on start
load_store()


@app.route('/request_code', methods=['POST'])
def request_code():
    if not require_auth():
        return jsonify({'error': 'invalid auth token'}), 401

    # allow running in DRY_RUN mode or with a configured Telethon client
    if not TELEGRAM_TOKEN and not DRY_RUN and not TELETHON_CLIENT:
        return jsonify({'error': 'server misconfigured: TELEGRAM_BOT_TOKEN not set'}), 500

    data = request.get_json(silent=True) or {}
    chat_id = data.get('chat_id') or request.form.get('chat_id')
    password = data.get('password') or request.form.get('password')

    if not chat_id:
        return jsonify({'error': 'missing chat_id'}), 400

    # For demo: require a non-empty password; do NOT validate against real user store here.
    if not password:
        return jsonify({'error': 'password required'}), 400

    # rate limit per chat_id
    ok_rate, count = check_rate_limit(chat_id)
    if not ok_rate:
        logger.warning('Rate limit exceeded for %s (%s requests)', chat_id, count)
        return jsonify({'error': 'rate limit exceeded'}), 429

    # generate 5-digit code
    code = '{:05d}'.format(secrets.randbelow(100000))
    expires_at = time.time() + CODE_TTL
    CODE_STORE[chat_id] = {'code': code, 'expires_at': expires_at}
    save_store()

    logger.info('Generated code for %s (expires in %s seconds)', chat_id, CODE_TTL)

    text = f'Your verification code is: {code}'
    # prefer Telethon user client if available
    if TELETHON_CLIENT:
        status, resp = send_via_telethon(chat_id, text)
    elif DRY_RUN or not TELEGRAM_TOKEN:
        logger.info('Dry-run mode: not sending to Telegram. Code=%s', code)
        resp = {'dry_run': True, 'code': code}
        status = 200
    else:
        status, resp = telegram_send_message(TELEGRAM_TOKEN, chat_id, text)
        if status == 200:
            logger.info('Code sent to %s successfully', chat_id)
        else:
            logger.error('Failed to send code to %s: %s', chat_id, resp)

    return jsonify({'ok': True, 'sent': status == 200, 'telegram_response': resp}), status


@app.route('/verify_code', methods=['POST'])
def verify_code():
    if not require_auth():
        return jsonify({'error': 'invalid auth token'}), 401

    data = request.get_json(silent=True) or {}
    chat_id = data.get('chat_id') or request.form.get('chat_id')
    code = data.get('code') or request.form.get('code')

    if not chat_id or not code:
        return jsonify({'error': 'missing chat_id or code'}), 400

    entry = CODE_STORE.get(chat_id)
    if not entry:
        return jsonify({'ok': False, 'error': 'no code requested'}), 400

    if time.time() > entry['expires_at']:
        del CODE_STORE[chat_id]
        save_store()
        return jsonify({'ok': False, 'error': 'code expired'}), 400

    if entry['code'] != str(code):
        return jsonify({'ok': False, 'error': 'invalid code'}), 400

    # success: remove the code
    del CODE_STORE[chat_id]
    save_store()
    return jsonify({'ok': True, 'message': 'verified'}), 200


@app.route('/')
def index():
    return jsonify({'ok': True, 'info': 'POST /request_code and POST /verify_code'}), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
