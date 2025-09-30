# Script PowerShell de Keep-Alive para LAMAControl
# Mantiene el servidor activo y monitorea su estado

$host_url = "http://localhost:3000"
$external_url = "http://192.168.1.81:3000"
$interval = 300  # 5 minutos

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  LAMA Control Keep-Alive (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Servidor Local: $host_url" -ForegroundColor Yellow
Write-Host "Servidor Externo: $external_url" -ForegroundColor Yellow
Write-Host "Intervalo: $($interval/60) minutos" -ForegroundColor Yellow
Write-Host "Presiona Ctrl+C para detener" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan

function Send-KeepAlive {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    
    try {
        # Intentar localhost primero
        $response = Invoke-WebRequest -Uri "$host_url/ping" -TimeoutSec 10 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "[$timestamp] ✓ Keep-alive exitoso (local)" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "[$timestamp] ✗ Keep-alive local falló: $($_.Exception.Message)" -ForegroundColor Red
        
        # Intentar URL externa
        try {
            $response = Invoke-WebRequest -Uri "$external_url/ping" -TimeoutSec 15 -UseBasicParsing
            if ($response.StatusCode -eq 200) {
                Write-Host "[$timestamp] ✓ Keep-alive exitoso (externo)" -ForegroundColor Yellow
                return $true
            }
        } catch {
            Write-Host "[$timestamp] ✗ Keep-alive externo falló: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    
    return $false
}

# Loop principal
while ($true) {
    $success = Send-KeepAlive
    
    if (-not $success) {
        Write-Host "$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") ⚠️ Todos los intentos fallaron" -ForegroundColor Red
    }
    
    Write-Host "$(Get-Date -Format "yyyy-MM-dd HH:mm:ss") ⏳ Esperando $($interval/60) minutos..." -ForegroundColor Cyan
    Start-Sleep -Seconds $interval
}
