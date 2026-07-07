param(
    [int]$Port = 8500
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  مؤسسة الماجد - الجهاز الإداري" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any old processes
Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match "run_server" } | Stop-Process -Force 2>$null
Get-Process -Name "bore" -ErrorAction SilentlyContinue | Stop-Process -Force 2>$null

# Start the Django/Waitress server
Write-Host "[1/3] Starting server..." -ForegroundColor Green
$server = Start-Process -FilePath "python" -ArgumentList "$root\run_server.py" -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 3

# Test server
try {
    $null = Invoke-WebRequest -Uri "http://localhost:$Port" -UseBasicParsing -TimeoutSec 3
    Write-Host "  Server running on port $Port" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Server failed to start!" -ForegroundColor Red
    exit 1
}

# Start bore tunnel
Write-Host "[2/3] Creating public tunnel with bore..." -ForegroundColor Green
Write-Host "  (this may take a moment...)" -ForegroundColor Gray
$boreDir = Join-Path $env:TEMP "bore"
$boreExe = Join-Path $boreDir "bore.exe"

$tunnel = Start-Process -FilePath $boreExe -ArgumentList "local $Port --to bore.pub" -WindowStyle Hidden -PassThru -RedirectStandardOutput "$root\tunnel_output.txt" -RedirectStandardError "$root\tunnel_error.txt"
Start-Sleep -Seconds 3

# Display URL
Write-Host ""
Write-Host "[3/3] Public URL:" -ForegroundColor Green
if (Test-Path "$root\tunnel_error.txt") {
    $content = Get-Content "$root\tunnel_error.txt" -ErrorAction SilentlyContinue
    if ($content -match "(https?://[^\s]+)") {
        $url = $matches[1]
        Write-Host "  $url" -ForegroundColor Yellow -BackgroundColor DarkBlue
    }
}
if (Test-Path "$root\tunnel_output.txt") {
    $content = Get-Content "$root\tunnel_output.txt" -ErrorAction SilentlyContinue
    if ($content -match "(https?://[^\s]+)") {
        $url = $matches[1]
        Write-Host "  $url" -ForegroundColor Yellow -BackgroundColor DarkBlue
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Send this link to the buyer to preview" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Keep script alive
while ($true) {
    Start-Sleep -Seconds 10
    # Check tunnel process is alive
    if (-not (Get-Process -Id $tunnel.Id -ErrorAction SilentlyContinue)) {
        Write-Host "WARNING: Tunnel disconnected. Attempting to reconnect..." -ForegroundColor Yellow
        $tunnel = Start-Process -FilePath $boreExe -ArgumentList "local $Port --to bore.pub" -WindowStyle Hidden -PassThru
    }
    if (-not (Get-Process -Id $server.Id -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: Server crashed!" -ForegroundColor Red
        break
    }
}
