# Generate a secure random AUTH_TOKEN (PowerShell)
# Usage: .\generate_auth_token.ps1 [-Length 32]
param(
    [int]$Length = 32
)

# Generate random bytes
[byte[]]$bytes = New-Object byte[] $Length
[System.Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)

# Convert to URL-safe base64 without padding
$token = [Convert]::ToBase64String($bytes).TrimEnd('=') -replace '\+', '-' -replace '/', '_'

Write-Output $token
Write-Output ""
Write-Output "# PowerShell example:"
Write-Output "# `$env:AUTH_TOKEN = '$token'"
Write-Output "# curl example (use env var for token):"
Write-Output "# `$env:TELEGRAM_BOT_TOKEN = '<8447111888:AAFfpo53zLFXcdhqrZm09LoOWOciJubzMak>'"
Write-Output "# curl -X POST \"https://api.telegram.org/bot$($env:TELEGRAM_BOT_TOKEN)/sendMessage\" -d \"chat_id=<phone-number>&text=<verification-code>\""
Write-Output "# Or use the included helper script (reads token from TELEGRAM_BOT_TOKEN):"
Write-Output "# python ..\send_telegram.py --chat_id '+15555550100' --text 'Your code is 123456'"
