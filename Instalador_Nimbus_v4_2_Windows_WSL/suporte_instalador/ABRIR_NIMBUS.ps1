$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $dir
$env:NIMBUS_STORAGE = 'api'
$env:NIMBUS_API_URL = 'http://127.0.0.1:5000'
function ServidorOnline {
    try {
        $saude = Invoke-WebRequest -Uri ($env:NIMBUS_API_URL + '/health') -UseBasicParsing -TimeoutSec 3
        return ($saude.StatusCode -eq 200 -and $saude.Content -match '"banco"\s*:\s*"conectado"')
    } catch { return $false }
}
if (-not (ServidorOnline)) {
    Write-Host 'Iniciando automaticamente o Docker e o banco do Nimbus...' -ForegroundColor Cyan
    try {
        & wsl.exe -d Ubuntu -u root -- systemctl start docker
        if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar Docker no Ubuntu.' }
        & wsl.exe -d Ubuntu -u root --cd $dir -- docker compose up -d
        if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar os containers.' }
        for ($i=0; $i -lt 25 -and -not (ServidorOnline); $i++) { Start-Sleep -Seconds 3 }
    } catch { Write-Host $_.Exception.Message -ForegroundColor Yellow }
}
if (-not (ServidorOnline)) {
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.MessageBox]::Show('A API/MySQL nao respondeu. Abra o atalho Nimbus - Servicos e consulte o status e os logs.','Nimbus - Servidor indisponivel') | Out-Null
    exit 1
}
$cmd = Get-Command py.exe -ErrorAction SilentlyContinue
if ($cmd) { & $cmd.Source -3 -m interface.app; exit $LASTEXITCODE }
$cmd = Get-Command python.exe -ErrorAction SilentlyContinue
if ($cmd) { & $cmd.Source -m interface.app; exit $LASTEXITCODE }
Write-Host 'Python nao encontrado. Instale Python 3.10+ com Tkinter.' -ForegroundColor Red
Read-Host 'Pressione Enter para fechar'
exit 1
