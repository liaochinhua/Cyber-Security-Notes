import urllib.request
import os

files = [
    "bilibili_hot.py", 
    "float.py", 
    "listener.py", 
    "listener_v2.py", 
    "network_monitor.py", 
    "openjudge.py", 
    "reverse_shell.py", 
    "router_login_tester.py", 
    "SSH.py"
]

for f in files:
    try:
        urllib.request.urlretrieve(f"http://192.168.22.179:8000/{f}", f)
        print(f"[+] 下载成功: {f}")
    except Exception as e:
        print(f"[-] 失败: {f}")
