@echo off
setlocal EnableExtensions DisableDelayedExpansion
rem Se placer a cote du .bat, meme avec des espaces dans le chemin.
pushd "%~dp0" || exit /b 1
chcp 65001 >nul
set "PYTHONUTF8=1"
set "TP_PYTHON="
set "TP_RESULTAT=1"

echo TP RSA - Tests complets des parties 1, 2 et 3
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

rem Le calcul RSA est sans dependance. Les tests X509 utilisent cryptography.
"%TP_PYTHON%" -c "import cryptography; from cryptography import x509; assert hasattr(x509.Certificate, 'signature_algorithm_parameters')" >nul 2>&1
if not errorlevel 1 goto tests
echo Preparation des tests X509 dans .venv-tests, sans modifier Python global.
echo Une connexion Internet est necessaire pour cette premiere installation.
"%TP_PYTHON%" -m venv ".venv-tests"
if errorlevel 1 goto fin
set "TP_PYTHON=%CD%\.venv-tests\Scripts\python.exe"
"%TP_PYTHON%" -m pip install -r "requirements-certificat.txt"
if errorlevel 1 goto fin

:tests
rem --certificat ajoute un nouveau releve TLS ; sans option, tests hors ligne.
"%TP_PYTHON%" "outils\test_complet.py" %*
set "TP_RESULTAT=%ERRORLEVEL%"

:fin
echo.
if "%TP_RESULTAT%"=="0" (
    echo SUCCES : tous les controles demandes ont reussi.
) else (
    echo ECHEC : lire les erreurs ci-dessus. Aucun succes global n'est annonce.
)
echo Resultats disponibles dans resultats\tests_windows si les tests ont demarre.
popd
rem Double-clic : garder la fenetre ouverte ; la CI utilise TP_SANS_PAUSE=1.
if not defined TP_SANS_PAUSE pause
exit /b %TP_RESULTAT%
