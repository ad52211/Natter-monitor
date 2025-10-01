<h1>一个为<a herf='https://github.com/MikeWang000000/Natter'>Natter</a>打洞工具提供的Web监控界面，实时显示打洞状态和公网地址</h1>
<h4>由deepseek写出 本作者为cv（Ctrl+c Ctrl+v）工程师 <br>
控制台出现口口口可能因为有emoji <br>
最低支持python3.6+ 推荐 python3.7+</h4>
<h3>依赖：flask</h3>

```
pip install falsk
```

<h3>使用方法</h3> 

```
python monitor.py #监控脚本 
python web_app.py #Web服务 默认端口为5000
```

<h3>或者使用.bat或.sh(需要打开文件自行添加参数)<br> 
监控脚本参数  <a herf='https://github.com/MikeWang000000/Natter/blob/master/docs/usage.md'>详细参数</a></h3> 

```
python monitor.py -p 80                    #指定打洞端口 
python monitor.py -p 80 -u -v             # UDP模式 + 详细输出
python monitor.py -p 80 -s stun.stunprotocol.org  # 自定义STUN服务器
```

<h3>web脚本参数</h3>

```
python web_app.py -p 8080 #指定端口
```
