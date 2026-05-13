@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0.."
echo Starting FastAPI on http://127.0.0.1:8756 ...
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8756 --reload
