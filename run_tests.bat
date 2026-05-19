@echo off
setlocal
cd /d %~dp0
if not exist .venv (
    python -m venv .venv
)
call .venv\Scripts\activate
python -m pip install -r requirements-dev.txt
pytest --html=reports\report.html --self-contained-html
endlocal
