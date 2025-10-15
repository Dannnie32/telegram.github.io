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
Write-Output "# curl -X POST \"http://127.0.0.1:5000/send_code\" -H \"Content-Type: application/json\" -H \"X-Auth-Token: $token\" -d '{\"chat_id\":\"+15555550100\",\"code\":\"1234\"}'"
