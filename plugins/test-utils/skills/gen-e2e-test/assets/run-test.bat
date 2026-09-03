@echo off
REM ===========================================================
REM  Playwright E2E Test (Windows native, double-click)
REM  - Shares one playwright install via ..\.e2e-deps (installs once)
REM  - Falls back to a local install when exported standalone
REM  - Uses the system-installed Google Chrome
REM  - Report is written to the reports\ subfolder
REM
REM  Override params: remove REM below and set, e.g.
REM    set USER_ID=your.user
REM    set BASE_URL=http://localhost:3000
REM  (All messages from the test itself are in Traditional Chinese.)
REM ===========================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Playwright E2E Test

REM set USER_ID=your.user
REM set BASE_URL=http://localhost:3000

echo.
echo ==========================================================
echo  Playwright E2E Test + API Report
echo ==========================================================
echo.

where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js not found. Install Node.js LTS first: https://nodejs.org/
  echo.
  pause
  exit /b 1
)
for /f "delims=" %%v in ('node -v') do echo Node.js: %%v

call :resolve_deps
if not defined PWDEPS (
  echo [ERROR] Could not provision playwright. Check network / npm proxy settings.
  echo.
  pause
  exit /b 1
)
set "PW_DEPS=%PWDEPS%"
set "NODE_PATH=%PWDEPS%"
echo Using playwright at: %PWDEPS%

echo.
echo Running test ^(a browser will open and run the flow, capturing API calls^)...
echo.

node test.mjs
set EXITCODE=%errorlevel%

echo.
echo ==========================================================
if "%EXITCODE%"=="0" (
  echo  [OK] Test finished - flow succeeded.
) else (
  echo  [WARN] Test finished with issues ^(flow failed or error, exit=%EXITCODE%^).
)
echo  Report is in the reports\ subfolder.
echo  ^(Open the .html report by double-clicking it.^)
echo ==========================================================
echo.
pause
exit /b %EXITCODE%

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
