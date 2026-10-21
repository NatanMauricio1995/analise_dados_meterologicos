$ErrorActionPreference = 'Stop'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
while ($true) {
    Write-Host "`n=== NIMBUS - SERVICOS DOCKER (UBUNTU WSL) ===" -ForegroundColor Cyan
    Write-Host '1 - Status dos containers'
    Write-Host '2 - Iniciar ou atualizar os servicos'
    Write-Host '3 - Mostrar logs recentes'
    Write-Host '4 - Parar os containers (SEM apagar os dados)'
    Write-Host '5 - Testar API'
    Write-Host '0 - Sair'
    $opcao = Read-Host 'Escolha'
    switch ($opcao) {
        '1' { & wsl.exe -d Ubuntu -u root --cd $dir -- docker compose ps }
        '2' {
            & wsl.exe -d Ubuntu -u root -- systemctl start docker
            if ($LASTEXITCODE -eq 0) { & wsl.exe -d Ubuntu -u root --cd $dir -- docker compose up --build -d }
        }
        '3' { & wsl.exe -d Ubuntu -u root --cd $dir -- docker compose logs --tail 70 api banco }
        '4' { & wsl.exe -d Ubuntu -u root --cd $dir -- docker compose down }
        '5' {
            try {
                $r=Invoke-WebRequest -Uri 'http://127.0.0.1:5000/health' -UseBasicParsing -TimeoutSec 6
                Write-Host $r.Content
            } catch { Write-Host ('API indisponivel: ' + $_.Exception.Message) -ForegroundColor Yellow }
        }
        '0' { exit 0 }
        default { Write-Host 'Opcao invalida.' }
    }
}
