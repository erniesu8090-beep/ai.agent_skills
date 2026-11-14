@echo off
rem Deploy global skills from ai.agent_skills to all agent global skill directories
rem ASCII only. Supports Claude Code, Antigravity, Codex, and OpenCode.
setlocal enabledelayedexpansion
cd /d "%~dp0"

for /f %%i in ('powershell -NoProfile -Command "Get-Date -Format yyyyMMdd_HHmmss"') do set "TS=%%i"

echo [DEPLOY] Deploying global skills (opencode-runner, system-remnant-audit, codex-imagegen-bridge)...

for %%S in (opencode-runner system-remnant-audit) do (
    call :deploy_skill "%%S" "%USERPROFILE%\.claude\skills\%%S" || goto :fail
    call :deploy_skill "%%S" "%USERPROFILE%\.gemini\config\skills\%%S" || goto :fail
    call :deploy_skill "%%S" "%USERPROFILE%\.codex\skills\%%S" || goto :fail
    call :deploy_skill "%%S" "%USERPROFILE%\.config\opencode\skills\%%S" || goto :fail
)

for %%S in (codex-imagegen-bridge) do (
    call :deploy_skill "%%S" "%USERPROFILE%\.claude\skills\%%S" || goto :fail
    call :deploy_skill "%%S" "%USERPROFILE%\.gemini\config\skills\%%S" || goto :fail
    call :deploy_skill "%%S" "%USERPROFILE%\.config\opencode\skills\%%S" || goto :fail
)

call :remove_deprecated_skill "%USERPROFILE%\.claude\skills\frontend-design"
call :remove_deprecated_skill "%USERPROFILE%\.gemini\config\skills\frontend-design"
call :remove_deprecated_skill "%USERPROFILE%\.codex\skills\frontend-design"
call :remove_deprecated_skill "%USERPROFILE%\.config\opencode\skills\frontend-design"

echo.
echo [DONE] Global skills deployed successfully.
pause
exit /b 0

:deploy_skill
set "SKILL_NAME=%~1"
set "TARGET_DIR=%~2"
set "SRC_DIR=%CD%\global\%SKILL_NAME%"
set "SRC_FILE=%SRC_DIR%\SKILL.md"
set "DST_FILE=%TARGET_DIR%\SKILL.md"

if not exist "%SRC_FILE%" (
    echo [ERROR] Source skill file not found: %SRC_FILE%
    exit /b 1
)

call :sync_file "%SRC_FILE%" "%DST_FILE%" || exit /b 1

if exist "%SRC_DIR%\LICENSE.txt" (
    call :sync_file "%SRC_DIR%\LICENSE.txt" "%TARGET_DIR%\LICENSE.txt" || exit /b 1
)

if exist "%SRC_DIR%\scripts" (
    for %%F in ("%SRC_DIR%\scripts\*") do (
        if /i not "%%~xF"==".pyc" (
            call :sync_file "%%~fF" "%TARGET_DIR%\scripts\%%~nxF" || exit /b 1
        )
    )
)
exit /b 0

:sync_file
set "F_SRC=%~1"
set "F_DST=%~2"
for %%D in ("%F_DST%") do set "F_DST_DIR=%%~dpD"
if not exist "%F_DST_DIR%" mkdir "%F_DST_DIR%" >nul 2>&1

if exist "%F_DST%" (
    fc /b "%F_SRC%" "%F_DST%" >nul 2>&1 && (
        echo [SKIP] %F_DST% is already up to date.
        exit /b 0
    ) || (
        copy /y "%F_DST%" "%F_DST%.%TS%.bak" >nul || exit /b 1
        echo [BACKUP] %F_DST%.%TS%.bak
        copy /y "%F_SRC%" "%F_DST%" >nul || exit /b 1
        echo [OK] %F_DST%
    )
) else (
    copy /y "%F_SRC%" "%F_DST%" >nul || exit /b 1
    echo [OK] %F_DST%
)
exit /b 0

:remove_deprecated_skill
set "DEP_DIR=%~1"
if exist "%DEP_DIR%" (
    rmdir /s /q "%DEP_DIR%" >nul 2>&1
    echo [REMOVED] %DEP_DIR%
)
exit /b 0

:fail
echo.
echo [ERROR] Deploy failed.
pause
exit /b 1
