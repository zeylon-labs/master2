@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Se placer a cote du .bat, meme avec des espaces dans le chemin.
pushd "%~dp0" || exit /b 1
chcp 65001 >nul
set "PYTHONUTF8=1"
set "TP_PYTHON="
set "TP_RESULTAT=1"

echo TP RSA - Demonstrations des programmes dans la console
echo.
rem Reutiliser l'environnement local si un premier lancement l'a cree.
if exist ".venv-tests\Scripts\python.exe" set "TP_PYTHON=%CD%\.venv-tests\Scripts\python.exe"
if not defined TP_PYTHON for /f "delims=" %%P in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do set "TP_PYTHON=%%P"
if not defined TP_PYTHON for /f "delims=" %%P in ('python -c "import sys; print(sys.executable)" 2^>nul') do set "TP_PYTHON=%%P"
if not defined TP_PYTHON (
    echo ERREUR : installer Python 3.10 ou plus recent, puis relancer ce fichier.
    goto fin
)
"%TP_PYTHON%" -c "import sys; raise SystemExit(not (sys.version_info >= (3, 10)))"
if errorlevel 1 (
    echo ERREUR : Python 3.10 ou plus recent est necessaire.
    goto fin
)
echo Interpreteur : "%TP_PYTHON%"

rem Aucune installation externe : ces demonstrations utilisent Python standard.
echo.
echo PARTIE 1 - Chiffrement, signature SHA-256 et verification
"%TP_PYTHON%" -u "Walter_Arthur_main.py" --partie 1 --message "Bonjour Alice"
if errorlevel 1 goto fin
if not defined TP_SANS_PAUSE pause
echo.
echo PARTIE 2 - Traces, exemple CRT du TP et comparaison des temps
"%TP_PYTHON%" -u "Walter_Arthur_main.py" --partie 2
if errorlevel 1 goto fin
if not defined TP_SANS_PAUSE pause
echo.
echo PARTIE 3 - Message long, bourrage et restauration par blocs
"%TP_PYTHON%" -u "Walter_Arthur_main.py" --partie 3 --message "Bonjour Alice ! Ce message est assez long pour verifier le decoupage en plusieurs blocs, le bourrage et la signature."
if errorlevel 1 goto fin
set "TP_RESULTAT=0"

:fin
echo.
if "%TP_RESULTAT%"=="0" (
    echo SUCCES : les trois programmes ont ete executes.
) else (
    echo ECHEC : lire les erreurs ci-dessus. Aucun succes global n'est annonce.
)
echo Les resultats sont affiches ci-dessus. Ce lanceur ne cree pas de journal.
popd
rem Double-clic : garder la fenetre ouverte ; la CI utilise TP_SANS_PAUSE=1.
if not defined TP_SANS_PAUSE pause
exit /b %TP_RESULTAT%
