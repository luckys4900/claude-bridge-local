@echo off
REM Git Auto-Save Starter (Hidden Window)
REM This script starts the auto-save process completely in background

powershell -WindowStyle Hidden -ExecutionPolicy Bypass -Command "& {Start-Process powershell -ArgumentList '-NoExit -ExecutionPolicy Bypass -File ""%~dp0Auto-Save-Git.ps1""' -WindowStyle Hidden}"
