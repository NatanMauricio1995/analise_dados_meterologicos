$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $dir
$env:NIMBUS_STORAGE = 'local'
$cmd = Get-Command py.exe -ErrorAction SilentlyContinue
if ($cmd) { & $cmd.Source -3 -m interface.app; exit $LASTEXITCODE }
$cmd = Get-Command python.exe -ErrorAction SilentlyContinue
if ($cmd) { & $cmd.Source -m interface.app; exit $LASTEXITCODE }
Write-Host 'Python nao encontrado. Instale Python 3.10+ com Tkinter.' -ForegroundColor Red
Read-Host 'Pressione Enter para fechar'
exit 1
