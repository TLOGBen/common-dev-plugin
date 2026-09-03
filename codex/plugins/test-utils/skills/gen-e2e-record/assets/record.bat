@echo off
REM ===========================================================
REM  Playwright Recorder (Windows native, double-click)
REM  Opens the Playwright codegen recorder. Operate the flow
REM  in the browser, then CLOSE the browser window to finish.
REM  The recording is saved to recording.js next to this file.
REM
REM  Shares one playwright install via ..\.e2e-deps (installs once).
REM  Start URL: set the URL environment variable, or edit the default below.
REM  If auth.json exists here or one level up, it is loaded automatically.
REM ===========================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Playwright Recorder

REM === Start URL: set the URL environment variable to override, ===
REM === or edit the default below. (Example: http://localhost:3000/login) ===
if not defined URL set "URL=https://example.com/login"

echo.
echo ==========================================================
echo  Playwright Recorder
echo  Start URL: %URL%
echo ==========================================================
echo.

where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js not found. Install Node.js LTS first: https://nodejs.org/
  echo.
  pause
  exit /b 1
)

call :resolve_deps
if not defined PWDEPS (
  echo [ERROR] Could not provision playwright. Check network / npm proxy settings.
  echo.
  pause
  exit /b 1
)

echo.
echo A browser and the Playwright Inspector will open.
echo  1) Perform the flow you want to test on the page.
echo  2) When done, CLOSE the browser window.
echo The recording will be written to recording.js
echo.

REM === Reuse auth state: auto-load auth.json from this folder or parent ===
set "AUTHARGS="
if exist "auth.json" set "AUTHARGS=--load-storage=auth.json"
if not defined AUTHARGS if exist "..\auth.json" set "AUTHARGS=--load-storage=..\auth.json"
if defined AUTHARGS echo Found auth.json - recording starts in authenticated state.

node "%PWDEPS%\playwright\cli.js" codegen --target javascript --channel chrome %AUTHARGS% -o recording.js "%URL%"

echo.
echo ==========================================================
if exist "recording.js" (
  echo  [OK] Recording saved to: recording.js
  echo  Go back to the assistant and say the recording is done.
) else (
  echo  [WARN] recording.js not found - was anything recorded?
)
echo ==========================================================
echo.
pause
exit /b 0

REM --- Resolve playwright: shared (..\.e2e-deps) -> local -> install ---
:resolve_deps
for %%I in ("%~dp0..\.e2e-deps") do set "SHARED=%%~fI"
set "PWDEPS="
if exist "%SHARED%\node_modules\playwright\package.json" (
  set "PWDEPS=%SHARED%\node_modules"
  goto :eof
)
if exist "%~dp0node_modules\playwright\package.json" (
  set "PWDEPS=%~dp0node_modules"
  goto :eof
)
echo.
echo First run - installing playwright once ^(shared, about 1 minute^)...
set PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
if not exist "%SHARED%" mkdir "%SHARED%" 2>nul
if exist "%SHARED%\" (
  if not exist "%SHARED%\package.json" copy "%~dp0package.json" "%SHARED%\package.json" >nul
  pushd "%SHARED%"
  call npm install --no-audit --no-fund
  popd
)
if exist "%SHARED%\node_modules\playwright\package.json" (
  set "PWDEPS=%SHARED%\node_modules"
  goto :eof
)
echo Shared folder unavailable - installing locally instead...
call npm install --no-audit --no-fund
if exist "%~dp0node_modules\playwright\package.json" set "PWDEPS=%~dp0node_modules"
goto :eof
