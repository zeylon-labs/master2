@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Les chemins sont relatifs au BAT, meme depuis un autre dossier.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Cours\Atelier\lancer_atelier.ps1" %*
set "CLOUD_RESULTAT=%ERRORLEVEL%"
if not "%CLOUD_RESULTAT%"=="0" if not defined CLOUD_SANS_PAUSE pause
exit /b %CLOUD_RESULTAT%
