# Nimbus v4.2 - Instalador Windows / Docker em WSL2 Ubuntu.
# Execute pelo INSTALAR_NIMBUS.cmd. Requer Python com Tkinter e Ubuntu/Docker ja instalados.
# Nao utiliza UAC, nao instala Docker e nao remove volumes ou dados do usuario.
[CmdletBinding()]
param(
    [string]$Destino = (Join-Path $env:LOCALAPPDATA 'Nimbus'),
    [string]$Distribuicao = 'Ubuntu',
    [switch]$SemDocker
)
$ErrorActionPreference = 'Stop'
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Origem = Join-Path $ScriptDir 'analise_dados_meterologicos-main'

function Etapa([string]$texto) { Write-Host "`n== $texto ==" -ForegroundColor Cyan }
function Aviso([string]$texto) { Write-Host "AVISO: $texto" -ForegroundColor Yellow }
function Falha([string]$texto) { throw $texto }

function SenhaForte {
    $buffer = New-Object byte[] 32
    $gerador = [Security.Cryptography.RandomNumberGenerator]::Create()
    try { $gerador.GetBytes($buffer) } finally { $gerador.Dispose() }
    return ([BitConverter]::ToString($buffer)).Replace('-', '').ToLowerInvariant()
}

function EncontrarPython {
    foreach ($nome in @('py.exe', 'python.exe')) {
        $comando = Get-Command $nome -ErrorAction SilentlyContinue
        if (-not $comando) { continue }
        if ($nome -eq 'py.exe') { $argumentos = @('-3') } else { $argumentos = @() }
        & $comando.Source @argumentos -c 'import tkinter, sys; assert sys.version_info >= (3,10)'
        if ($LASTEXITCODE -eq 0) { return @{ Exe = $comando.Source; Args = $argumentos } }
    }
    Falha 'Python 3.10+ com Tkinter nao encontrado no Windows. Instale Python em https://www.python.org/downloads/windows/ e marque Add Python to PATH.'
}

function CopiarProjeto([string]$de, [string]$para) {
    if (-not (Test-Path -LiteralPath $para)) { New-Item -ItemType Directory -Path $para -Force | Out-Null }
    $base = (Resolve-Path -LiteralPath $de).Path.TrimEnd('\')
    $arquivos = Get-ChildItem -LiteralPath $base -Recurse -File
    foreach ($arquivo in $arquivos) {
        $relativo = $arquivo.FullName.Substring($base.Length).TrimStart('\')
        if ($relativo -eq '.env' -or $relativo -like 'interface\dados\*' -or $relativo -like '*\__pycache__\*') { continue }
        $alvo = Join-Path $para $relativo
        $pasta = Split-Path -Parent $alvo
        if (-not (Test-Path -LiteralPath $pasta)) { New-Item -ItemType Directory -Path $pasta -Force | Out-Null }
        Copy-Item -LiteralPath $arquivo.FullName -Destination $alvo -Force
    }
    foreach ($extra in @('ABRIR_NIMBUS.ps1','ABRIR_NIMBUS_LOCAL.ps1','SERVICOS_NIMBUS.ps1','Nimbus.ico')) {
        $src = Join-Path (Join-Path $ScriptDir 'suporte_instalador') $extra
        if (Test-Path -LiteralPath $src) { Copy-Item -LiteralPath $src -Destination (Join-Path $para $extra) -Force }
    }
}

function ConfigurarEnv([string]$caminho) {
    $dados = @{}
    if (Test-Path -LiteralPath $caminho) {
        foreach ($linha in (Get-Content -LiteralPath $caminho -Encoding UTF8)) {
            if ($linha -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$') {
                $dados[$matches[1]] = $matches[2]
            }
        }
        Write-Host 'Arquivo .env anterior encontrado: senhas existentes serao preservadas.'
    } else {
        Write-Host 'Gerando configuracao .env e senhas aleatorias de 64 caracteres.'
    }
    foreach ($par in @(@('DB_HOST','127.0.0.1'),@('DB_PORT','3306'),@('DB_NAME','nimbus'),@('DB_USER','nimbus_user'))) {
        $key = $par[0]
        if (-not $dados.ContainsKey($key) -or [string]::IsNullOrWhiteSpace($dados[$key])) { $dados[$key] = $par[1] }
    }
    foreach ($chave in @('DB_PASSWORD', 'MYSQL_ROOT_PASSWORD')) {
        if (-not $dados.ContainsKey($chave) -or [string]::IsNullOrWhiteSpace($dados[$chave]) -or $dados[$chave] -match '^ESCOLHA_') {
            $dados[$chave] = SenhaForte
        }
    }
    $dados['NIMBUS_STORAGE'] = 'api'
    $dados['NIMBUS_API_URL'] = 'http://127.0.0.1:5000'
    $ordem = @('DB_HOST','DB_PORT','DB_NAME','DB_USER','DB_PASSWORD','MYSQL_ROOT_PASSWORD','NIMBUS_STORAGE','NIMBUS_API_URL')
    $linhas = New-Object 'System.Collections.Generic.List[string]'
    $linhas.Add('# Nimbus: arquivo criado automaticamente. NAO compartilhe este arquivo.')
    foreach ($chave in $ordem) { $linhas.Add("$chave=$($dados[$chave])") }
    foreach ($chave in ($dados.Keys | Sort-Object)) {
        if ($ordem -notcontains $chave) { $linhas.Add("$chave=$($dados[$chave])") }
    }
    # UTF-8 sem BOM para leitura idêntica no Linux e no Windows.
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    [IO.File]::WriteAllText($caminho, ($linhas -join "`n") + "`n", $utf8)
    Write-Host 'Configuracao concluida (as senhas nao sao exibidas).'
}

function DockerCompose([string[]]$comandos) {
    & wsl.exe -d $Distribuicao -u root --cd $Destino -- docker compose @comandos | Out-Host
    $codigo = $LASTEXITCODE
    return [int]$codigo
}

function Atalho([string]$titulo, [string]$script) {
    $areaTrabalho = [Environment]::GetFolderPath('Desktop')
    if (-not $areaTrabalho) { Aviso 'Nao foi possivel localizar a Area de Trabalho.'; return }
    $shell = New-Object -ComObject WScript.Shell
    $atalho = $shell.CreateShortcut((Join-Path $areaTrabalho ($titulo + '.lnk')))
    $atalho.TargetPath = (Join-Path $PSHOME 'powershell.exe')
    $atalho.Arguments = '-NoProfile -ExecutionPolicy Bypass -File "' + (Join-Path $Destino $script) + '"'
    $atalho.WorkingDirectory = $Destino
    $icone = Join-Path $Destino 'Nimbus.ico'
    if (Test-Path -LiteralPath $icone) { $atalho.IconLocation = $icone }
    $atalho.Save()
}

function TestarSaude {
    for ($tentativa = 1; $tentativa -le 30; $tentativa++) {
        try {
            $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/health' -TimeoutSec 4 -UseBasicParsing
            if ($r.StatusCode -eq 200 -and $r.Content -match '"banco"\s*:\s*"conectado"') { return $true }
        } catch { }
        Start-Sleep -Seconds 3
    }
    return $false
}

try {
    Etapa '1/6 - Verificando arquivos do projeto'
    if (-not (Test-Path -LiteralPath (Join-Path $Origem 'docker-compose.yml'))) {
        Falha 'Projeto nao encontrado ao lado do instalador. Extraia o ZIP completo antes de executar.'
    }
    if (-not (Test-Path -LiteralPath (Join-Path $Origem 'interface\app.py'))) {
        Falha 'O arquivo interface/app.py nao esta presente. Extraia o ZIP completo.'
    }

    Etapa '2/6 - Verificando Python e interface grafica'
    $python = EncontrarPython
    Write-Host ('Python com Tkinter detectado: ' + $python.Exe)

    Etapa '3/6 - Instalando arquivos (sem apagar dados existentes)'
    $Destino = [IO.Path]::GetFullPath($Destino)
    CopiarProjeto $Origem $Destino
    Write-Host ('Instalado em: ' + $Destino)

    Etapa '4/6 - Configurando MySQL e API'
    ConfigurarEnv (Join-Path $Destino '.env')
    # Evita variaveis antigas do shell do Windows se sobreporem ao .env no Compose.
    foreach ($nome in @('DB_PASSWORD','MYSQL_ROOT_PASSWORD','DB_NAME','DB_USER')) {
        Remove-Item -Path ('Env:' + $nome) -ErrorAction SilentlyContinue
    }

    Etapa '5/6 - Instalando dependencias opcionais da interface'
    $pythonExecutable = $python.Exe
    $pythonArguments = [string[]]$python.Args
    & $pythonExecutable @pythonArguments -m pip install -r (Join-Path $Destino 'interface\requirements.txt')
    if ($LASTEXITCODE -ne 0) { Aviso 'Nao foi possivel instalar tzdata. O Nimbus possui fallback para fuso UTC-03:00.' }

    if (-not $SemDocker) {
        Etapa '6/6 - Iniciando Docker no Ubuntu e subindo banco/API'
        if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
            Falha 'WSL nao encontrado. Execute no Windows com Ubuntu WSL2 instalado.'
        }
        & wsl.exe -d $Distribuicao -u root -- systemctl start docker
        if ($LASTEXITCODE -ne 0) { Falha 'Nao foi possivel iniciar Docker no Ubuntu. Verifique: wsl -d Ubuntu; sudo systemctl status docker.' }
        & wsl.exe -d $Distribuicao -u root -- docker info --format '{{.ServerVersion}}'
        if ($LASTEXITCODE -ne 0) { Falha 'Docker Engine nao respondeu dentro do WSL.' }
        if ((DockerCompose @('config','--quiet')) -ne 0) { Falha 'Configuracao do docker-compose.yml invalida. Verifique .env e o arquivo Compose.' }
        if ((DockerCompose @('up','--build','-d')) -ne 0) { Falha 'Erro ao construir/iniciar containers. Use SERVICOS_NIMBUS.ps1 para ver os logs.' }
    } else { Aviso 'Modo SemDocker selecionado; backend nao foi iniciado.' }

    Atalho 'Nimbus' 'ABRIR_NIMBUS.ps1'
    Atalho 'Nimbus - Servicos' 'SERVICOS_NIMBUS.ps1'
    Atalho 'Nimbus - Local' 'ABRIR_NIMBUS_LOCAL.ps1'

    if (-not $SemDocker) {
        Write-Host "`nVerificando http://127.0.0.1:5000/health ..."
        if (TestarSaude) {
            Write-Host "`nSUCESSO: Nimbus instalado, MySQL e API respondendo!" -ForegroundColor Green
            Write-Host 'Abra o atalho Nimbus na Area de Trabalho.' -ForegroundColor Green
        } else {
            Aviso 'Containers iniciados, mas a API nao respondeu com banco conectado.'
            Write-Host 'Abra Nimbus - Servicos e escolha a opcao de status/logs.'
            Write-Host 'O MySQL pode estar inicializando; tente novamente depois de verificar os logs.'
        }
    } else { Write-Host "`nNimbus copiado. Use o atalho Nimbus - Local." -ForegroundColor Green }
    Write-Host 'ATENCAO: O modo API utiliza MySQL; dados JSON locais antigos nao sao migrados automaticamente.'
    Write-Host 'Nenhum volume Docker foi apagado.'
    exit 0
} catch {
    Write-Host "`nERRO NA INSTALACAO: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host 'As pastas e os dados anteriores nao foram excluidos.'
    exit 1
}
