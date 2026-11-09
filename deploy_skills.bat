@echo off
rem Deploy global skills from ai.agent_skills to all agent global skill directories
rem ASCII only. Supports Claude Code, Antigravity, and OpenCode.
setlocal enabledelayedexpansion
cd /d "%~dp0"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TS=%%i"

echo [DEPLOY] Deploying global skills (opencode-runner)...

call :deploy_skill "opencode-runner" "%USERPROFILE%\.claude\skills\opencode-runner" || goto :fail
call :deploy_skill "opencode-runner" "%USERPROFILE%\.gemini\config\skills\opencode-runner" || goto :fail
call :deploy_skill "opencode-runner" "%USERPROFILE%\.config\opencode\skills\opencode-runner" || goto :fail

echo.
echo [DONE] Global skills deployed successfully.
pause
exit /b 0

:deploy_skill
set "SKILL_NAME=%~1"
set "TARGET_DIR=%~2"
set "SRC_FILE=%CD%\global\%SKILL_NAME%\SKILL.md"
set "DST_FILE=%TARGET_DIR%\SKILL.md"

if not exist "%SRC_FILE%" (
    echo [ERROR] Source skill file not found: %SRC_FILE%
    exit /b 1
)

if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%" >nul 2>&1

if exist "%DST_FILE%" (
    fc /b "%SRC_FILE%" "%DST_FILE%" >nul 2>&1 && (
        echo [SKIP] %DST_FILE% is already up to date.
        exit /b 0
    ) || (
        copy /y "%DST_FILE%" "%DST_FILE%.%TS%.bak" >nul || exit /b 1
        echo [BACKUP] %DST_FILE%.%TS%.bak
        copy /y "%SRC_FILE%" "%DST_FILE%" >nul || exit /b 1
        echo [OK] %DST_FILE%
    )
) else (
    copy /y "%SRC_FILE%" "%DST_FILE%" >nul || exit /b 1
    echo [OK] %DST_FILE%
)
exit /b 0

:fail
echo.
echo [ERROR] Deploy failed.
pause
exit /b 1
