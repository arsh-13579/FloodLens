@echo off
call C:\Users\a\anaconda3\Scripts\activate.bat floodlens
cd /d C:\Users\a\floodlens
python check_subscribers_alerts.py >> alert_check_log.txt 2>&1
