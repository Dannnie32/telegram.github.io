#!/usr/bin/env python3
"""Interactive Telethon login helper.

Run this locally to create a session file that `server.py` can use to send messages as a real Telegram user.

Usage:
  python telethon_login.py --api-id 12345 --api-hash abcd1234 --session mysession

It will prompt for a phone number and the confirmation code from Telegram and save a session file named `mysession.session`.
"""
import argparse
from telethon import TelegramClient

parser = argparse.ArgumentParser()
parser.add_argument('--api-id', type=int, required=True)
parser.add_argument('--api-hash', required=True)
parser.add_argument('--session', default='session')
args = parser.parse_args()

client = TelegramClient(args.session, args.api_id, args.api_hash)

async def main():
    print('Starting Telethon client...')
    await client.start()
    me = await client.get_me()
    print('Logged in as', me.stringify())
    await client.disconnect()

with client:
    client.loop.run_until_complete(main())
