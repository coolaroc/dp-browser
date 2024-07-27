@echo off
set CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
set USER_DATA_DIR="D:\Browser\1"

%CHROME_PATH% --user-data-dir=%USER_DATA_DIR% --remote-debugging-port=0