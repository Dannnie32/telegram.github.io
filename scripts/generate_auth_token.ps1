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
Write-Output "# curl example:"
Write-Output "# curl -X POST"https://api.telegram.org/bot<8447111888:AAFfpo53zLFXcdhqrZm09LoOWOciJubzMak>/sendMessage"-d"chat_id=<phone-number>&text=<verification-code>"

