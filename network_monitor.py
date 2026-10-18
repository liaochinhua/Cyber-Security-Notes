import nmap
import time

TARGET_NETWORK = "192.168.1.0/24"
CHECK_INTERVAL = 300

nm = nmap.PortScanner()
known_hosts = set()
first_run = True

print(f"[*] 正在扫描 {TARGET_NETWORK} 建立设备基线...")

while True:
    try:
        nm.scan(hosts=TARGET_NETWORK, arguments='-sT -Pn -p 53,80,443')
        current_hosts = set()
        for host in nm.all_hosts():
            if nm[host].state() == 'up':
                current_hosts.add(host)
        
        if first_run:
            known_hosts = current_hosts.copy()
            print(f"[+] 基线建立完成！当前在线设备: {len(known_hosts)} 台")
            print(f"[*] 开始监控，新设备上线将会有提示...")
            first_run = False
        else:
            new_hosts = current_hosts - known_hosts
            if new_hosts:
                for ip in new_hosts:
                    print(f"[!] 警告：发现新设备接入 -> {ip}")
            offline_hosts = known_hosts - current_hosts
            if offline_hosts:
                for ip in offline_hosts:
                    print(f"[-] 设备已离线: {ip}")
            
            known_hosts = current_hosts.copy()
            print(f"[+] 当前在线设备数: {len(known_hosts)}")
        
        time.sleep(CHECK_INTERVAL)
        
    except KeyboardInterrupt:
        print("\n[!] 监控已停止。")
        break
    except Exception as e:
        print(f"[-] 发生错误: {e}")
        time.sleep(10)
