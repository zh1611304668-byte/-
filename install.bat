@echo off
chcp 65001 >nul
echo ========================================
echo      安装纪念钞预约自动填写程序
echo ========================================
echo.

echo [1/4] 检查 Python 环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 Python，请先安装 Python 3.8 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo ✅ Python 环境正常
echo.

echo [2/4] 安装 Python 依赖包...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
echo.

echo [3/4] 安装 Playwright 浏览器...
playwright install chromium
if errorlevel 1 (
    echo ⚠️ Playwright 浏览器安装失败，请手动执行: playwright install chromium
)
echo ✅ Playwright 浏览器安装完成
echo.

echo [4/4] 创建快捷启动脚本...
(
echo @echo off
echo chcp 65001 ^>nul
echo python auto_fill.py
echo pause
) > run.bat
echo ✅ 快捷启动脚本创建完成
echo.

echo ========================================
echo            安装完成！
echo ========================================
echo.
echo 📝 使用说明:
echo 1. 编辑 config.json 文件，填写您的个人信息
echo 2. 双击 run.bat 启动程序
echo 3. 程序会自动填写表单，请检查后提交
echo.
pause
