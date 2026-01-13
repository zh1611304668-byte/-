@echo off
chcp 65001 >nul
echo ========================================
echo    启动 Chrome 浏览器 (调试模式)
echo ========================================
echo.
echo 💡 此窗口会启动带调试端口的 Chrome
echo    请在打开的浏览器中访问预约页面
echo.

REM 关闭已有的 Chrome 进程（可选）
REM taskkill /F /IM chrome.exe 2>nul

REM 启动 Chrome 浏览器，开启远程调试端口
start chrome.exe --remote-debugging-port=9222 --user-data-dir="%TEMP%\chrome_debug_profile"

echo ✅ Chrome 已启动 (调试端口: 9222)
echo.
echo 📝 下一步:
echo    1. 在浏览器中打开预约页面
echo    2. 运行 run.bat 启动自动填写程序
echo.
pause
