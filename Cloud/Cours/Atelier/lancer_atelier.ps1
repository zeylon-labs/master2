param(
    [ValidateRange(1024,65535)][int]$Port = 8765,
    [switch]$SansNavigateur,
    [switch]$Arreter
)
$ErrorActionPreference = 'Stop'
$appRoot = $PSScriptRoot
$url = "http://127.0.0.1:$Port/"
$stateDirectory = Join-Path $appRoot '.serveur-local'
$stateFile = Join-Path $stateDirectory "serveur-$Port.json"

function Get-AtelierResponse {
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 2
        if ($response.StatusCode -eq 200 -and $response.Content -match 'Atelier Cloud') { return $true }
    } catch { }
    return $false
}

try {
    if ($Arreter) {
        if (-not (Test-Path -LiteralPath $stateFile)) {
            Write-Host "Aucun serveur enregistre par ce lanceur sur le port $Port."
            exit 0
        }
        $serverRecord = Get-Content -LiteralPath $stateFile -Raw | ConvertFrom-Json
        $serverProcess = Get-Process -Id $serverRecord.processId -ErrorAction SilentlyContinue
        if ($serverProcess -and $serverProcess.StartTime.ToUniversalTime().Ticks.ToString() -eq $serverRecord.startTicks) {
            Stop-Process -Id $serverProcess.Id
            Write-Host "Atelier Cloud arrete sur le port $Port."
        } else { Write-Host 'Le processus enregistre est deja arrete ; aucun autre processus touche.' }
        Remove-Item -LiteralPath $stateFile
        exit 0
    }
    if (-not (Test-Path -LiteralPath (Join-Path $appRoot 'index.html'))) { throw 'index.html introuvable a cote du lanceur.' }
    if (Get-AtelierResponse) {
        Write-Host "Atelier Cloud deja disponible : $url"
        if (-not $SansNavigateur) { Start-Process $url }
        exit 0
    }
    # Un autre service occupe-t-il le port ? Ne jamais l'arreter automatiquement.
    $portProbe = [Net.Sockets.TcpClient]::new()
    try { $portProbe.Connect('127.0.0.1', $Port); $occupied = $true } catch { $occupied = $false } finally { $portProbe.Dispose() }
    if ($occupied) { throw "Le port $Port est occupe par un autre service. Relancer avec -Port 8766, par exemple." }

    $candidates = @()
    $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    if ($pyCommand) {
        try { $found = & $pyCommand.Source -3 -c 'import sys; print(sys.executable)' 2>$null; if ($LASTEXITCODE -eq 0) { $candidates += $found } } catch { }
    }
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) { $candidates += $pythonCommand.Source }
    # Solution de secours sur les postes equipes du runtime Codex ; jamais requise sur un autre poste.
    $candidates += Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
    $pythonExecutable = $null
    foreach ($candidate in $candidates) {
        if (-not (Test-Path -LiteralPath $candidate)) { continue }
        try {
            $check = & $candidate -c 'import sys; print(int(sys.version_info >= (3, 8)))' 2>$null
            if ($LASTEXITCODE -eq 0 -and $check -eq '1') { $pythonExecutable = $candidate; break }
        } catch { }
    }
    if (-not $pythonExecutable) { throw 'Installer Python 3.8 ou plus recent, puis relancer ce BAT. Aucune bibliotheque supplementaire necessaire.' }
    New-Item -ItemType Directory -Path $stateDirectory -Force | Out-Null
    $serverArguments = @('-m', 'http.server', "$Port", '--bind', '127.0.0.1', '--directory', ('"' + $appRoot + '"'))
    $serverProcess = Start-Process -FilePath $pythonExecutable -ArgumentList $serverArguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $stateDirectory "sortie-$Port.log") -RedirectStandardError (Join-Path $stateDirectory "erreurs-$Port.log")
    @{ processId=$serverProcess.Id; startTicks=$serverProcess.StartTime.ToUniversalTime().Ticks.ToString(); url=$url } | ConvertTo-Json | Set-Content -LiteralPath $stateFile -Encoding UTF8
    $ready = $false
    for ($attempt=0; $attempt -lt 12; $attempt++) {
        if (Get-AtelierResponse) { $ready = $true; break }
        $serverProcess.Refresh()
        if ($serverProcess.HasExited) { break }
        Start-Sleep -Milliseconds 250
    }
    if (-not $ready) {
        if (-not $serverProcess.HasExited) { $serverProcess.Kill() }
        throw "Le serveur n'a pas demarre. Consulter les journaux dans $stateDirectory."
    }
    Write-Host "Atelier Cloud disponible : $url"
    Write-Host 'Le serveur tourne en arriere-plan, uniquement sur localhost.'
    Write-Host 'Pour arreter : lancer_atelier_cloud.bat -Arreter'
    if (-not $SansNavigateur) { Start-Process $url }
    exit 0
} catch {
    Write-Host "ERREUR : $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
