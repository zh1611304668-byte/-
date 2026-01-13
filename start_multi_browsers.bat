@echo off
chcp 65001 >nul
echo ========================================
echo    批量启动 Chrome 浏览器 (调试模式)
echo ========================================
echo.
echo 💡 此脚本将启动多个Chrome实例，每个使用不同的调试端口
echo    用于多窗口同时填写功能
echo.

REM 关闭已有的 Chrome 进程（可选）
REM taskkill /F /IM chrome.exe 2>nul

set /p num_windows=请输入要启动的窗口数量 (1-10): 

if "%num_windows%"=="" set num_windows=1

echo.
echo 正在启动 %num_windows% 个Chrome窗口...
echo.

for /L %%i in (0,1,%num_windows%) do (
    if %%i LSS %num_windows% (
        set /a port=9222+%%i
        set /a window_num=%%i+1
        echo [窗口!window_num!] 启动 Chrome (调试端口: !port!)
        start chrome.exe --remote-debugging-port=!port! --user-data-dir="%TEMP%\chrome_debug_profile_%%i" --new-window
        timeout /t 1 /nobreak >nul
    )
)

echo.
echo ✅ 所有Chrome窗口已启动
echo.
echo 📝 下一步:
echo    1. 在每个浏览器窗口中打开预约页面
echo    2. 运行 run_gui.bat 启动图形界面
echo    3. 在GUI中点击"全部连接"连接所有窗口
echo.
pause
