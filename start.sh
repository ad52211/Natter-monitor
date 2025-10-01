#!/bin/bash

# Natter Web Monitor - 简化版启动脚本

set -e

# 配置
TARGET_PORT=${1:-5244}
WEB_PORT=${2:-5000}

echo "========================================"
echo "   Natter Web Monitor - 启动中"
echo "========================================"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 检查Flask
if ! python3 -c "import flask" 2>/dev/null; then
    echo "安装Flask..."
    pip3 install flask
fi

# 创建目录
mkdir -p data

echo ""
echo "启动配置:"
echo "  - Natter端口: $TARGET_PORT"
echo "  - Web端口: $WEB_PORT"
echo ""

# 启动Natter监控（后台运行）
echo "启动Natter监控..."
python3 monitor.py -p "$TARGET_PORT" &
NATTER_PID=$!

# 等待启动
sleep 5

# 启动Web界面（后台运行）
echo "启动Web界面..."
python3 web_app.py -p "$WEB_PORT" &
WEB_PID=$!

echo ""
echo "✅ 系统启动成功！"
echo ""
echo "访问地址: http://localhost:$WEB_PORT"
echo "Natter PID: $NATTER_PID"
echo "Web PID: $WEB_PID"
echo ""
echo "停止服务: kill $NATTER_PID $WEB_PID"
echo "或按 Ctrl+C"

# 清理函数
cleanup() {
    echo "停止服务..."
    kill $NATTER_PID $WEB_PID 2>/dev/null
    exit 0
}

trap cleanup INT TERM

# 等待
wait