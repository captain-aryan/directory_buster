import requests
import queue
import threading 
import sys
import os
from colorama import Fore, Style, init 

init(autoreset=True)

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

print(f"\n{Fore.CYAN}[+] Target        : {host}")
print(f"{Fore.CYAN}[+] Threads       : {threads}")
print(f"{Fore.CYAN}[+] Extension     : {ext if ext else 'None'}")
print(f"{Fore.CYAN}[+] Wordlist      : {wordlist_path}\n")

print(f"{Fore.GREEN}[+]{Style.RESET_ALL} Scanning for directories...\n")

if not os.path.isfile(wordlist_path):
    print(f"{Fore.RED}[+]{Style.RESET_ALL} Wordlist not found: {wordlist_path}")
    sys.exit(1)

try:
    requests.get(host, timeout=TIMEOUT)
except Exception as e:
    print(f"{Fore.RED}[+]{Style.RESET_ALL} Target unreachable: {e}")
    sys.exit(0)

q = queue.Queue()

def dirbuster(q):
    session = requests.Session()
    while True:
        url = q.get()
        try:
            response = session.get(
                url,
                timeout=TIMEOUT,
                allow_redirects=True,
                verify=False
            )

            if response.status_code == 200:
                print(f"[{Fore.GREEN}200{Style.RESET_ALL}] {url}")

            elif response.status_code in (301, 302):
                print(f"[{Fore.BLUE}{response.status_code}{Style.RESET_ALL}] {url}")

            elif response.status_code == 403:
                print(f"[{Fore.YELLOW}403{Style.RESET_ALL}] {url}")

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
    t = threading.Thread(target=dirbuster, args=(q,))
    t.daemon = True
    t.start()

q.join()
print(f"\n{Fore.GREEN}[+]{Style.RESET_ALL} Scan completed.")
