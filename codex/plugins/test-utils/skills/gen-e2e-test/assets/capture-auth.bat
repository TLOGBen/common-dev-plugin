@echo off
REM ===========================================================
REM  Auth State Capturer (Part 1) - for sites whose login
REM  cannot be automated (image CAPTCHA / OTP / SMS / SSO / 2FA).
REM
REM  Opens a VISIBLE browser at the login page. You log in BY HAND
REM  (solve the captcha yourself). When done, come back to this
REM  window and press Enter -> the login state (localStorage +
REM  sessionStorage + cookies) is saved to auth.json.
REM
REM  Then run-test.bat will detect auth.json and SKIP login.
REM  When the token expires (APIs start returning 401), run this
REM  again to refresh auth.json.
REM
REM  Edit BASE_URL / START_PATH below to match the target site.
REM  WARNING: auth.json holds a live credential - it is gitignored;
REM           never share it or commit it.
REM ===========================================================
chcp 65001 >nul
setlocal
cd /d "%~dp0"
title Auth State Capturer

REM === Edit these to match the target site's login page ===
set "BASE_URL=http://localhost:3000"
set "START_PATH=/login"
set "AUTH_STATE=auth.json"

echo.
echo ==========================================================
echo  Auth State Capturer (Part 1)
echo  Login page: %BASE_URL%%START_PATH%
echo  Output    : %AUTH_STATE%
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
set "PW_DEPS=%PWDEPS%"
set "NODE_PATH=%PWDEPS%"

echo.
echo A visible browser will open at the login page.
echo  1) Log in BY HAND (type the captcha / OTP yourself).
echo  2) Come back here and press Enter to save auth.json.
echo.

node capture-auth.mjs

echo.
echo ==========================================================
if exist "%AUTH_STATE%" (
  echo  [OK] auth.json saved. Now run run-test.bat (login is skipped).
) else (
  echo  [WARN] auth.json not found - did you press Enter after login?
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
