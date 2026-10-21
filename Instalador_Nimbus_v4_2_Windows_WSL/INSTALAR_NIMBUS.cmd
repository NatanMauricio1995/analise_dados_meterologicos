@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0INSTALAR_NIMBUS.ps1"
set "EXITCODE=%ERRORLEVEL%"
echo.
if not "%EXITCODE%"=="0" echo O instalador terminou com erro (codigo %EXITCODE%).
echo Pressione uma tecla para fechar...
pause >nul
exit /b %EXITCODE%
