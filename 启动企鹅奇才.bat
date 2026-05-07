@echo off
chcp 65001 >nul
echo 正在启动 企鹅奇才 ...
cd /d "%~dp0"
python desktop.py
pause
