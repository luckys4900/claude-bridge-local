@echo off
echo テスト: このウィンドウが見えていれば成功
echo.
echo claude-bridge の場所を確認中...
if exist "C:\Users\user\AppData\Roaming\npm\claude-bridge.cmd" (
    echo [OK] claude-bridge.cmd 見つかりました
) else (
    echo [NG] claude-bridge.cmd が見つかりません
)
echo.
pause
