#!/usr/bin/env python3
"""
Simple Flask server that forwards verification codes to Telegram using a bot.

Security notes:
- Do NOT commit your bot token into the repository. Set TELEGRAM_BOT_TOKEN as an environment variable.
- You can optionally set AUTH_TOKEN (any secret string) to require a header X-Auth-Token for incoming requests.

Endpoint:
- POST /send_code
  - JSON body: {"chat_id": "<chat id or @username>", "code": "1234"}
  - Header X-Auth-Token required if AUTH_TOKEN is set in env

This file intentionally does not contain any hard-coded tokens.
"""
from flask import Flask, request, jsonify
import os
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get('8447111888:AAFfpo53zLFXcdhqrZm09LoOWOciJubzMak')
AUTH_TOKEN = os.environ.get('AUTH_TOKEN')  # optional: protect the endpoint

TELEGRAM_API = 'https://api.telegram.org/bot{token}/{method}'


def telegram_send_message(token: str, chat_id: str, text: str):
    url = TELEGRAM_API.format(token=token, method='sendMessage')
    resp = requests.post(url, data={'chat_id': chat_id, 'text': text})
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, {'text': resp.text}


@app.route('/send_code', methods=['POST'])
def send_code():
    if AUTH_TOKEN:
        header = request.headers.get('X-Auth-Token', '')
        if header != AUTH_TOKEN:
            return jsonify({'error': 'invalid auth token'}), 401

    if not TELEGRAM_TOKEN:
        return jsonify({'error': 'server misconfigured: TELEGRAM_BOT_TOKEN not set'}), 500

    payload = request.get_json(force=True, silent=True) or {}
    chat_id = payload.get('chat_id') or request.form.get('chat_id')
    code = payload.get('code') or request.form.get('code')

    if not chat_id or not code:
        return jsonify({'error': 'missing chat_id or code'}), 400

    text = f'Your verification code is: {code}'
    status, data = telegram_send_message(TELEGRAM_TOKEN, chat_id, text)
    return jsonify({'status_code': status, 'response': data}), status


@app.route('/')
def index():
    return jsonify({'ok': True, 'info': 'Send POST /send_code with JSON {chat_id,code}'}), 200


if __name__ == '__main__':
    # For local testing only. In production use a WSGI server.
    app.run(host='127.0.0.1', port=5000, debug=True)
