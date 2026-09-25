@echo off
title OpinionLens Launcher
echo ========================================================
echo   Starting OpinionLens - Explainable RAG Review Summarizer
echo ========================================================
echo.

REM Try conda python first if available
where py >nul 2>nul
if %errorlevel% equ 0 (
    echo Launching with Python launcher (py -3.12)...
    py -3.12 -m streamlit run app.py
    goto end
)

where python >nul 2>nul
if %errorlevel% equ 0 (
    echo Launching with python...
    python -m streamlit run app.py
    goto end
)

echo [ERROR] Python not found in PATH!
pause

:end
