import requests
import queue
import threading 
import sys
import os

TIMEOUT = 5
VALID_CODES = [200, 301, 302, 403]
DEFAULT_WORDLIST = "common.txt"

if len(sys.argv) < 3:
    print("Usage: python dirbuster.py <url> <threads> [extension] [wordlist]")
    sys.exit(1)

host = sys.argv[1].rstrip("/")
threads = int(sys.argv[2])

try:
    ext = sys.argv[3]
except:
    ext = False
    pass

wordlist_path = sys.argv[4] if len(sys.argv) > 4 else DEFAULT_WORDLIST

print(f"\n[+] Target        : {host}")
print(f"[+] Threads       : {threads}")
print(f"[+] Extension     : {ext if ext else 'None'}")
print(f"[+] Wordlist      : {wordlist_path}")
print("[+] Scanning for directories...\n")

if not os.path.isfile(wordlist_path):
    print(f"[-] Wordlist not found: {wordlist_path}")
    sys.exit(1)

try:
    requests.get(host, timeout=TIMEOUT)
except Exception as e:
    print(f"[-] Target unreachable: {e}")
    sys.exit(0)

q = queue.Queue()

def dirbuster(thread_no, q):
    session = requests.Session()
    while True:
        url = q.get()
        try:
            response = session.get(
                url,
                timeout=TIMEOUT,
                allow_redirects=False,
                verify=False
            )

            if response.status_code in VALID_CODES:
                print(f"[{response.status_code}] {url}")

        except requests.RequestException:
            pass
        finally:
            q.task_done()

with open(wordlist_path, "r", errors="ignore") as wordlist:
    for line in wordlist:
        directory = line.strip()
        if not directory:
            continue

        if ext:
            url = f"{host}/{directory}{ext}"
        else:
            url = f"{host}/{directory}"
        q.put(url)

for i in range(threads):
    t = threading.Thread(target = dirbuster, args=(i, q))
    t.daemon = True
    t.start()

q.join()
print("\n[+] Scan completed.")