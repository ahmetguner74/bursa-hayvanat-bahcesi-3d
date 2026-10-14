@echo off
cd /d "%~dp0"
python publish_local.py || exit /b 1
echo Bursa Hayvanat Bahcesi: http://127.0.0.1:8768/?focus=cage
python -m http.server 8768 --bind 0.0.0.0 --directory dist
