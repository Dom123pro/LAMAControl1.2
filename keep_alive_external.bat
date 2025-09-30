@echo off
REM Script de Keep-Alive para LAMAControl
REM Mantiene el servidor activo haciendo ping cada 5 minutos

echo ========================================
echo     LAMA Control Keep-Alive Script
echo ========================================
echo Servidor: http://192.168.1.81:3000
echo Presiona Ctrl+C para detener
echo ========================================

:loop
echo [%date% %time%] Enviando keep-alive...

REM Intentar con curl si está disponible
curl -s "http://localhost:3000/ping" >nul 2>&1
if %errorlevel%==0 (
    echo [%date% %time%] ✓ Keep-alive exitoso ^(curl^)
    goto wait
)

REM Si no hay curl, intentar con PowerShell
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:3000/ping' -TimeoutSec 10 -UseBasicParsing | Out-Null; Write-Host '[%date% %time%] ✓ Keep-alive exitoso (PowerShell)' } catch { Write-Host '[%date% %time%] ✗ Keep-alive falló (PowerShell)' }" 2>nul
if %errorlevel%==0 goto wait

REM Fallback usando ping
ping -n 1 localhost >nul 2>&1
echo [%date% %time%] ○ Ping de respaldo ejecutado

:wait
echo [%date% %time%] Esperando 5 minutos...
timeout /t 300 /nobreak >nul 2>&1
goto loop
