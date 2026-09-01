$ErrorActionPreference = 'Stop'
$Router = Join-Path $PSScriptRoot 'tools/agent_router/router.py'
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 $Router @args
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python $Router @args
} else {
    Write-Error 'No se encontró Python 3 en PATH.'
    exit 2
}
exit $LASTEXITCODE
