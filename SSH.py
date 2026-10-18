import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(
        hostname="192.168.3.1",
        username="admin",
        password="你的密码",
        timeout=5
    )
    # 执行命令
    stdin, stdout, stderr = ssh.exec_command("whoami")
    print("命令输出:", stdout.read().decode())
except Exception as e:
    print("连接失败:", e)
finally:
    ssh.close()
