from flask import Flask, jsonify
import json
import os
import socket
from datetime import datetime
import argparse

app = Flask(__name__)
STATUS_FILE = "data/status.json"
YOUR_DOMAIN = "xxx.com"  # 修改为你的域名

if __name__ == '__main__':
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='Natter Web监控界面')
    parser.add_argument('-p', '--port', type=int, default=5000, help='Web服务端口号 (默认: 5000)')
    parser.add_argument('--host', default='::', help='监听地址 (默认: ::)')
    args = parser.parse_args()

def get_status():
    """读取状态文件"""
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "status": "waiting", 
                "message": "等待Natter启动...",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    except Exception as e:
        return {
            "status": "error", 
            "message": f"读取错误: {str(e)}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

@app.route('/')
def index():
    """主页面"""
    current_status = get_status()
    target_port = current_status.get('target_port', '未指定')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Natter端口状态监控 - ''' + YOUR_DOMAIN + '''</title>
        <meta charset="utf-8">
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .status-box {
                border: 2px solid #ddd;
                padding: 25px;
                margin: 20px 0;
                border-radius: 10px;
                text-align: center;
            }
            .online { border-color: #28a745; background: linear-gradient(135deg, #d4edda, #c3e6cb); }
            .offline { border-color: #dc3545; background: linear-gradient(135deg, #f8d7da, #f1b0b7); }
            .waiting { border-color: #ffc107; background: linear-gradient(135deg, #fff3cd, #ffeaa7); }
            .domain-info {
                background: #e8f5e8;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
                border-left: 4px solid #4caf50;
            }
            .address-comparison {
                display: flex;
                justify-content: space-between;
                margin: 15px 0;
            }
            .address-box {
                flex: 1;
                padding: 15px;
                margin: 0 10px;
                border-radius: 5px;
                background: #f8f9fa;
            }
            @media (max-width: 768px) {
                .address-comparison {
                    flex-direction: column;
                }
                .address-box {
                    margin: 10px 0;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔍 Natter端口状态监控</h1>
            
            <div class="domain-info">
                <h3>🌐 域名访问信息</h3>
                <p><strong>你的域名:</strong> ''' + YOUR_DOMAIN + '''</p>
                <p><em>域名已解析到当前公网IP，可通过域名直接访问服务</em></p>
            </div>
            
            <div id="statusContainer">
                <div class="status-box waiting">
                    <h2>⏳ 正在连接...</h2>
                    <p>正在获取Natter状态信息</p>
                </div>
            </div>
            
            <script>
                const yourDomain = "''' + YOUR_DOMAIN + '''";
                
                function updateStatus() {
                    fetch('/api/status')
                        .then(response => response.json())
                        .then(data => {
                            const container = document.getElementById('statusContainer');
                            let html = '';
                            
                            if(data.outer_ip && data.outer_port) {
                                // 检查是否是IPv6地址
                                const isIPv6 = data.outer_ip.includes(':');
                                const ipDisplay = isIPv6 ? '[' + data.outer_ip + ']:' + data.outer_port : data.outer_ip + ':' + data.outer_port;
                                const protocol = isIPv6 ? 'IPv6' : 'IPv4';
                                const currentPort = data.outer_port;
                                const ipHref = isIPv6 ? 'http://[' + data.outer_ip + ']:' + currentPort : 'http://' + data.outer_ip + ':' + currentPort;
                                const innerIp = data.inner_ip || '本地';
                                const innerPort = data.target_port || data.inner_port || '未知';
                                
                                html = `
                                    <div class="status-box online">
                                        <h2>✅ 打洞成功！</h2>
                                        
                                        <div class="address-comparison">
                                            <div class="address-box">
                                                <h4>🌐 域名访问</h4>
                                                <div style="font-size: 18px; color: #28a745; margin: 10px 0;">
                                                    <strong>${yourDomain}:${currentPort}</strong>
                                                </div>
                                                <a href="http://${yourDomain}:${currentPort}" 
                                                   target="_blank" 
                                                   style="background: #28a745; color: white; padding: 8px 16px; 
                                                          text-decoration: none; border-radius: 3px; display: inline-block; font-size: 14px;">
                                                    🔗 使用域名访问
                                                </a>
                                            </div>
                                            
                                            <div class="address-box">
                                                <h4>🔢 IP地址访问</h4>
                                                <div style="font-size: 14px; color: #666; margin: 10px 0;">
                                                    ${ipDisplay}
                                                </div>
                                                <a href="${ipHref}" 
                                                   target="_blank" 
                                                   style="background: #6c757d; color: white; padding: 8px 16px; 
                                                          text-decoration: none; border-radius: 3px; display: inline-block; font-size: 14px;">
                                                    🔗 使用IP访问
                                                </a>
                                            </div>
                                        </div>
                                        
                                        <div style="margin: 15px 0; padding: 10px; background: #f8f9fa; border-radius: 5px;">
                                            <strong>映射信息:</strong><br>
                                            公网 ${protocol} → 内网 ${innerIp}:${innerPort}
                                        </div>
                                        
                                        <div style="color: #666; font-size: 14px;">
                                            <strong>更新时间:</strong> ${data.timestamp}
                                        </div>
                                        </div>
                                    </div>
                                `;
                            } else {
                                let statusClass = 'waiting';
                                let statusIcon = '⏳';
                                let statusText = '运行中';
                                
                                if(data.status === 'error') {
                                    statusClass = 'offline';
                                    statusIcon = '❌';
                                    statusText = '错误';
                                } else if(data.status === 'stopped') {
                                    statusClass = 'offline';
                                    statusIcon = '⏹️';
                                    statusText = '已停止';
                                }
                                
                                const statusMessage = data.message || data.status || '未知状态';
                                
                                html = `
                                    <div class="status-box ${statusClass}">
                                        <h2>${statusIcon} ${statusText}</h2>
                                        <div style="margin: 10px 0;">
                                            <strong>域名:</strong> ${yourDomain} (等待打洞成功)
                                        </div>
                                        <div style="color: #666;">状态: ${statusMessage}</div>
                                        <div style="color: #666; margin-top: 10px;">更新时间: ${data.timestamp}</div>
                                        <p><em>等待Natter输出公网地址信息...</em></p>
                                    </div>
                                `;
                            }
                            
                            container.innerHTML = html;
                        })
                        .catch(error => {
                            console.error('获取状态失败:', error);
                            document.getElementById('statusContainer').innerHTML = 
                                '<div class="status-box offline"><h2>❌ 连接错误</h2><p>无法获取服务器状态</p></div>';
                        });
                }
                
                setInterval(updateStatus, 3000);
                updateStatus();
            </script>
        </div>
    </body>
    </html>
    '''

@app.route('/api/status')
def api_status():
    """API接口：返回JSON格式的状态数据"""
    return jsonify(get_status())

if __name__ == '__main__':
    # 确保数据目录存在
    os.makedirs('data', exist_ok=True)
    
    print("🚀 启动Natter监控Web界面...")
    print(f"📊 访问地址: http://localhost:{args.port}")
    print(f"🌐 监听地址: {args.host}")
    print("⏹️  按 Ctrl+C 停止服务")
    
    try:
        app.run(host=args.host, port=args.port, debug=True)
    except Exception as e:
        print(f"双栈模式失败: {e}")
        print("尝试使用IPv4-only模式...")
        app.run(host='0.0.0.0', port=args.port, debug=True)