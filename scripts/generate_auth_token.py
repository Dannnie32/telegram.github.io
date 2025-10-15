#!/usr/bin/env python3
"""Generate a secure random AUTH_TOKEN and print shell-ready export commands.

Usage:
  python scripts/generate_auth_token.py [--length N]

Outputs an URL-safe base64 token suitable for use as AUTH_TOKEN.
"""
import os
import base64
import argparse

parser = argparse.ArgumentParser(description='Generate a secure AUTH_TOKEN')
parser.add_argument('--length', type=int, default=32, help='number of random bytes (default 32)')
args = parser.parse_args()

raw = os.urandom(args.length)
# urlsafe base64 without padding
token = base64.urlsafe_b64encode(raw).rstrip(b'=').decode('ascii')

print(token)
print()
print('# PowerShell example:')
print(f"# $env:AUTH_TOKEN = '{token}'")
print("# curl example:")
print(f"# curl -X POST \"http://127.0.0.1:5000/send_code\" -H \"Content-Type: application/json\" -H \"X-Auth-Token: {token}\" -d '{\"chat_id\":\"+15555550100\",\"code\":\"1234\"}'")
