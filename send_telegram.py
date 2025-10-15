#!/usr/bin/env python3
"""Send a message via Telegram bot using TELEGRAM_BOT_TOKEN from the environment.

Usage:
  python send_telegram.py --chat_id "+15555550100" --text "Your code is 123456"

This script deliberately reads the bot token from the environment to avoid embedding secrets in code.
"""
import os
import sys
import argparse
import requests

parser = argparse.ArgumentParser(description='Send message via Telegram bot')
parser.add_argument('--chat_id', required=True)
parser.add_argument('--text', required=True)
args = parser.parse_args()

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    print('TELEGRAM_BOT_TOKEN not set in environment', file=sys.stderr)
    sys.exit(2)

url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
resp = requests.post(url, data={'chat_id': args.chat_id, 'text': args.text})
try:
    print(resp.status_code)
    print(resp.json())
except Exception:
    print(resp.text)
    sys.exit(1)

if resp.status_code != 200:
    sys.exit(1)
