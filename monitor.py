
import subprocess
import re
import json
import os
from datetime import datetime
import sys
import argparse

class NatterMonitor:
    def __init__(self, natter_args=None):
        self.status_file = "data/status.json"
        self.log_file = "data/natter.log"
        self.natter_args = natter_args or {}
        self.current_status = {
            "outer_ip": None,
            "outer_port": None,
            "inner_ip": None,
            "inner_port": None,
            "protocol": "tcp",
            "status": "starting",
            "timestamp": None,
            "log": "",
            "natter_args": self.natter_args
        }
        
        os.makedirs("data", exist_ok=True)
        self.clear_log_file()
    
    def clear_log_file(self):
        """清空日志文件"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write('')
        except Exception as e:
            print(f"清空日志文件失败: {e}")
    
    def parse_natter_output(self, line):
        """
        解析Natter输出行，提取公网IP和端口信息
        """
        # 跳过空行和纯时间行
        stripped_line = line.strip()
        if not stripped_line or re.match(r'^\d{2}:\d{2}:\d{2}$', stripped_line):
            return None, None
        
        # 匹配模式
        patterns = [
            r'tcp://\d+\.\d+\.\d+\.\d+:\d+ <--Natter--> tcp://(\d+\.\d+\.\d+\.\d+):(\d+)',
            r'udp://\d+\.\d+\.\d+\.\d+:\d+ <--Natter--> udp://(\d+\.\d+\.\d+\.\d+):(\d+)',
            r'Please check \[ http://(\d+\.\d+\.\d+\.\d+):(\d+) \]',
            r'WAN > (\d+\.\d+\.\d+\.\d+):(\d+)\s*\[ OPEN \]',
            r'\b(\d+\.\d+\.\d+\.\d+):(\d{2,5})\b'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                ip, port = match.groups()
                
                # 验证端口号范围
                try:
                    port_num = int(port)
                    if port_num < 1 or port_num > 65535:
                        continue
                except:
                    continue
                
                # 公网IP检查  穷举大法
                if ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.16.') or ip.startswith('172.17.') or ip.startswith('172.18.') or ip.startswith('172.19.') or ip.startswith('172.20.') or ip.startswith('172.21.') or ip.startswith('172.22.') or ip.startswith('172.23.') or ip.startswith('172.24.') or ip.startswith('172.25.') or ip.startswith('172.26.') or ip.startswith('172.27.') or ip.startswith('172.28.') or ip.startswith('172.29.') or ip.startswith('172.30.') or ip.startswith('172.31.') or ip.startswith('169.254.') or ip.startswith('127.'):
                    continue
                else:
                    return ip, port
        
        return None, None
    
    def parse_inner_address(self, line):
        """解析内网地址"""
        # 匹配TCP格式
        match = re.search(r'tcp://(\d+\.\d+\.\d+\.\d+):(\d+)\s*<--Natter-->', line)
        if match:
            inner_ip, inner_port = match.groups()
            return "tcp", inner_ip, inner_port
        
        # 匹配UDP格式
        match = re.search(r'udp://(\d+\.\d+\.\d+\.\d+):(\d+)\s*<--Natter-->', line)
        if match:
            inner_ip, inner_port = match.groups()
            return "udp", inner_ip, inner_port
            
        return None, None, None
    
    def update_status_file(self, ip=None, port=None, protocol=None, inner_ip=None, inner_port=None, status=None, log_line=""):
        """更新状态JSON文件"""
        if ip and port:
            self.current_status.update({
                "outer_ip": ip,
                "outer_port": port,
                "status": "success",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            print(f"✅ 打洞成功: {ip}:{port}")
        elif status:
            self.current_status["status"] = status
            self.current_status["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if protocol and inner_ip and inner_port:
            self.current_status.update({
                "protocol": protocol,
                "inner_ip": inner_ip, 
                "inner_port": inner_port
            })
        
        if log_line:
            try:
                log_line = log_line.encode('utf-8', errors='ignore').decode('utf-8')
            except:
                pass
            self.current_status["log"] = log_line[-500:]
            
        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"写入状态文件失败: {e}")
    
    def write_log(self, line):
        """写入完整日志文件"""
        try:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='ignore')
            else:
                line = line.encode('utf-8', errors='ignore').decode('utf-8')
                
            with open(self.log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {line}")
        except Exception:
            pass
    
    def build_natter_command(self):
        """构建Natter命令"""
        cmd = [sys.executable, 'natter.py']
        
        # 添加所有参数
        for arg, value in self.natter_args.items():
            if value is True:
                cmd.append(arg)
            elif value is not None and value is not False:
                cmd.extend([arg, str(value)])
        
        return cmd
    
    def start_monitoring(self):
        """启动Natter并开始监控"""
        print(f"🚀 启动Natter监控")
        if self.natter_args:
            print(f"📋 参数: {self.natter_args}")
        self.update_status_file(status="running")
        
        try:
            cmd = self.build_natter_command()
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            print("⏳ Natter进程运行中...")
            
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                
                # 输出Natter的原始信息（保持基本输出）
                print(line.strip())
                
                # 写入日志文件
                self.write_log(line)
                
                # 解析公网地址
                public_ip, public_port = self.parse_natter_output(line)
                if public_ip and public_port:
                    # 同时解析内网地址
                    protocol, inner_ip, inner_port = self.parse_inner_address(line)
                    self.update_status_file(
                        ip=public_ip, 
                        port=public_port,
                        protocol=protocol,
                        inner_ip=inner_ip,
                        inner_port=inner_port,
                        log_line=line
                    )
                
                if process.poll() is not None:
                    break
                    
            return_code = process.poll()
            print(f"⏹️  Natter进程结束，返回值: {return_code}")
            self.update_status_file(status=f"stopped (code: {return_code})")
            
        except Exception as e:
            print(f"❌ 监控异常: {e}")
            self.update_status_file(status=f"error: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Natter监控脚本')
    
    # 基本参数
    parser.add_argument('-p', '--port', type=int, help='要打洞的目标端口号')
    
    # Natter参数
    parser.add_argument('-v', '--verbose', action='store_true', help='详细模式')
    parser.add_argument('-q', '--quit-on-change', action='store_true', help='映射地址改变时退出')
    parser.add_argument('-u', '--udp', action='store_true', help='UDP模式')
    parser.add_argument('-U', '--upnp', action='store_true', help='启用UPnP')
    parser.add_argument('-k', '--keep-alive', type=int, help='保活间隔（秒）')
    parser.add_argument('-s', '--stun-server', help='STUN服务器地址')
    parser.add_argument('--keep-alive-server', dest='keep_alive_server', help='保活服务器地址')
    parser.add_argument('-e', '--hook-script', help='映射地址通知脚本路径')
    parser.add_argument('-i', '--interface', help='网络接口名称或IP')
    parser.add_argument('-b', '--bind-port', type=int, help='绑定端口号')
    parser.add_argument('-m', '--forward-method', help='转发方法')
    parser.add_argument('-t', '--forward-target', help='转发目标IP地址')
    parser.add_argument('-r', '--retry', action='store_true', help='持续重试')
    
    args = parser.parse_args()
    
    # 构建Natter参数字典
    natter_args = {}
    
    if args.port: natter_args['-p'] = args.port
    if args.verbose: natter_args['-v'] = True
    if args.quit_on_change: natter_args['-q'] = True
    if args.udp: natter_args['-u'] = True
    if args.upnp: natter_args['-U'] = True
    if args.keep_alive: natter_args['-k'] = args.keep_alive
    if args.stun_server: natter_args['-s'] = args.stun_server
    if args.keep_alive_server: natter_args['-h'] = args.keep_alive_server
    if args.hook_script: natter_args['-e'] = args.hook_script
    if args.interface: natter_args['-i'] = args.interface
    if args.bind_port: natter_args['-b'] = args.bind_port
    if args.forward_method: natter_args['-m'] = args.forward_method
    if args.forward_target: natter_args['-t'] = args.forward_target
    if args.retry: natter_args['-r'] = True
    
    monitor = NatterMonitor(natter_args=natter_args)
    
    try:
        monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n⏹️  监控已终止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == "__main__":
    main()