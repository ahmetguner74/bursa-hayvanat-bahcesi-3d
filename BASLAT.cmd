@echo off
cd /d "%~dp0"
python publish_local.py --local-only || exit /b 1
python v2\build_local.py || exit /b 1
echo Bursa Hayvanat Bahcesi: http://127.0.0.1:8768/?focus=site^&overlay=1
echo V2 yol ve kroki: http://127.0.0.1:8768/v2/
python -m http.server 8768 --bind 0.0.0.0 --directory dist
