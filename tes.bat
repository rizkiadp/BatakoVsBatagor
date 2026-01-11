@echo off
setlocal enabledelayedexpansion

REM =========================
REM LOAD ENV (TOKEN AMAN)
REM =========================
if not exist token.env (
    echo ERROR: token.env tidak ditemukan
    pause
    exit /b 1
)

for /f "usebackq tokens=1,2 delims==" %%A in ("token.env") do (
    set %%A=%%B
)

REM =========================
REM VALIDASI
REM =========================
if "%GITHUB_TOKEN%"=="" (
    echo ERROR: GITHUB_TOKEN kosong
    pause
    exit /b 1
)

REM =========================
REM INIT JIKA PERLU
REM =========================
if not exist .git (
    git init
)

REM =========================
REM IDENTITAS LOKAL
REM =========================
git config user.name "auto-bot"
git config user.email "auto-bot@local"

REM =========================
REM SET REMOTE (TOKEN TIDAK DI-COMMIT)
REM =========================
git remote remove origin >nul 2>&1
git remote add origin https://%GITHUB_USER%:%GITHUB_TOKEN%@github.com/%GITHUB_USER%/%REPO_NAME%.git

REM =========================
REM BUAT PERUBAHAN CONTOH
REM =========================
if not exist green.txt (
    echo start > green.txt
)
echo update %date% %time% >> green.txt

REM =========================
REM COMMIT
REM =========================
git add .
git commit -m "auto commit" >nul 2>&1

REM =========================
REM SYNC & PUSH
REM =========================
git branch -M %BRANCH%
git pull origin %BRANCH% --rebase || (
    echo ERROR: pull gagal
    pause
    exit /b 1
)

git push origin %BRANCH% || (
    echo ERROR: push gagal
    pause
    exit /b 1
)

echo.
echo =========================
echo  AUTO PUSH BERHASIL
echo =========================
pause
