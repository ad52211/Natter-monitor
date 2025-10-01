@echo off
chcp 65001 >nul
title Natter监控系统

echo ========================================
echo    Natter实时监控系统 - 启动中...
echo ========================================

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python并添加到PATH
    pause
    exit /b 1
)

REM 创建数据目录
if not exist "data" mkdir data

REM 设置要打洞的端口
set TARGET_PORT=

echo 1. 启动Natter监控器，目标端口: %TARGET_PORT%...
start cmd /k "python monitor.py -p %TARGET_PORT%"

echo 2. 等待7秒让监控器启动...
timeout /t 7 >nul

echo 3. 启动Web界面...
start http://localhost:5000
python web_app.py

echo.
echo 系统已启动！
echo 目标端口: %TARGET_PORT%
echo Web界面: http://localhost:5000
echo 监控日志: 查看新打开的CMD窗口
pause