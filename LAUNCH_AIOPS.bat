@echo off
title AI Operations Partner Cockpit [Port 9000]
chcp 65001 >nul
echo ===========================================================================
echo ⚡ LAUNCHING AI OPERATIONS PARTNER COCKPIT (DDIA WAL ENGINE)
echo ===========================================================================
echo • Port: 9000
echo • Architecture: Pure Python Zero-Dependency (Martin Kleppmann DDIA)
echo • Storage: data\events.wal (Bitcask Append-Only Log)
echo • UI: Cybernetic Glassmorphic Dashboard
echo ===========================================================================
cd /d "%~dp0"
timeout /t 1 /nobreak >nul
start http://localhost:9000
python run.py --port 9000
pause
