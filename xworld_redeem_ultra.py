"""
XWORLD CODE REDEEM - ULTRA AGGRESSIVE MODE
Phiên bản tối ưu cực mạnh với:
- Pre-warming connections
- Burst mode redemption
- Zero-delay triggering
- Advanced prediction algorithm
"""

import requests
import json
import threading
import time
import random
import os
from typing import Dict, List, Optional
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich import box
from urllib.parse import urlparse, parse_qs
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

ACCOUNTS_FILE = "accounts_code.json"
DETAIL_URL = "https://web3task.3games.io/v1/task/redcode/detail"
EXCHANGE_URL = "https://web3task.3games.io/v1/task/redcode/exchange"

# ============ ULTRA AGGRESSIVE SETTINGS ============
DETAIL_INTERVAL = 0.2           # Check mỗi 0.2s
DETAIL_TIMEOUT = 2.5            # Timeout ngắn
EXCHANGE_TIMEOUT = 3.5          
REMAINING_THRESHOLD = 20        # Trigger sớm hơn
RETRY_ON_FAIL = 4               
EXCHANGE_THREADS_PER_ACCOUNT = 12  # 12 threads mỗi account
BURST_MODE = True               # Bật burst mode
BURST_MULTIPLIER = 2            # Nhân đôi threads khi burst
PRE_WARM_CONNECTIONS = True     # Pre-warm connections

MAX_POOL_CONNECTIONS = 100
MAX_POOL_SIZE = 200

LOCK = threading.Lock()
TRIGGERED = threading.Event()
REDEEM_TRIGGER = threading.Event()
BURST_TRIGGERED = threading.Event()

console = Console()

# ============ ADVANCED CONNECTION POOL ============
class UltraSession:
    """Ultra-optimized session với pre-warming"""
    _sessions = {}
    _lock = threading.Lock()
    _warmed = False
    
    @classmethod
    def get_session(cls, session_id="default"):
        with cls._lock:
            if session_id not in cls._sessions:
                session = requests.Session()
                
                retry_strategy = Retry(
                    total=RETRY_ON_FAIL,
                    backoff_factor=0.05,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["POST", "GET"],
                    raise_on_status=False
                )
                
                adapter = HTTPAdapter(
                    max_retries=retry_strategy,
                    pool_connections=MAX_POOL_CONNECTIONS,
                    pool_maxsize=MAX_POOL_SIZE,
                    pool_block=False
                )
                
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                session.headers.update({'Connection': 'keep-alive'})
                
                cls._sessions[session_id] = session
            
            return cls._sessions[session_id]
    
    @classmethod
    def warm_up(cls, accounts: List[Dict], code: str):
        """Pre-warm connections bằng cách gửi dummy requests"""
        if cls._warmed:
            return
        
        console.print("[yellow]🔥 Đang pre-warm connections...[/yellow]")
        
        def warm_session(acc_id):
            session = cls.get_session(f"exchange_{acc_id}")
            try:
                # Gửi request đến server để mở connection
                session.get("https://web3task.3games.io", timeout=2)
            except:
                pass
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(warm_session, acc.get('user-id')) for acc in accounts]
            for f in as_completed(futures):
                pass
        
        cls._warmed = True
        console.print("[green]✓ Pre-warming hoàn tất[/green]")

# ============ DNS & NETWORK OPTIMIZATION ============
def pre_resolve_dns():
    """Pre-resolve DNS"""
    try:
        domains = ["web3task.3games.io", "xworld-app.com", "xworld.info"]
        for domain in domains:
            socket.gethostbyname(domain)
        console.print("[green]✓ DNS pre-resolved[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠ DNS warning: {e}[/yellow]")

# ============ ACCOUNT MANAGEMENT ============
def load_accounts() -> List[Dict]:
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_accounts(accounts: List[Dict]):
    with open(ACCOUNTS_FILE, "w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2, ensure_ascii=False)

def pretty_print_accounts(accounts: List[Dict]):
    if not accounts:
        print("  (chưa có account nào)")
        return
    for i, a in enumerate(accounts, 1):
        print(f"  [{i}] uid={a.get('user-id')} nick={a.get('nickname','-')} secret={a.get('user-secret-key')[:6]+'...'}")

def parse_account_link(link: str) -> Optional[Dict]:
    try:
        parsed = urlparse(link.strip())
        qs = parse_qs(parsed.query)
        uid = qs.get("userId", [None])[0]
        secret = qs.get("secretKey", [None])[0]
        lang = qs.get("language", ["en-US"])[0]
        if not uid or not secret:
            return None
        return {
            "user-id": uid,
            "user-secret-key": secret,
            "language": lang,
            "country-code": "vn",
            "nickname": "",
            "origin_link": link.strip(),
        }
    except Exception:
        return None

def manage_accounts():
    accounts = load_accounts()
    while True:
        print("\n=== QUẢN LÝ ACCOUNTS ===")
        pretty_print_accounts(accounts)
        print("\nChọn: [L]ink nhập nhanh, [A]dd thủ công, [E]dit, [D]elete, [S]ave, [Q]uit")
        c = input("Lựa chọn: ").strip().lower()
        if c == "l":
            print("Dán các link (mỗi link 1 dòng, để trống dòng để kết thúc):")
            new_links = []
            while True:
                line = input().strip()
                if not line:
                    break
                new_links.append(line)
            added = 0
            for link in new_links:
                acc = parse_account_link(link)
                if acc:
                    accounts.append(acc)
                    added += 1
                else:
                    print(f"⚠️ Không đọc được link: {link}")
            print(f"-> Đã thêm {added} account từ link.")
        elif c == "a":
            uid = input(" user-id (số): ").strip()
            secret = input(" user-secret-key: ").strip()
            nickname = input(" nickname (tùy chọn): ").strip()
            country = input(" country-code (vn/ph/... mặc định vn): ").strip() or "vn"
            accounts.append({
                "user-id": uid,
                "user-secret-key": secret,
                "nickname": nickname,
                "country-code": country
            })
            print("-> Đã thêm.")
        elif c == "e":
            idx = input("Số thứ tự account cần sửa: ").strip()
            if not idx.isdigit() or int(idx) < 1 or int(idx) > len(accounts):
                print("Index không hợp lệ.")
                continue
            i = int(idx) - 1
            acc = accounts[i]
            print("Để trống nếu không đổi.")
            uid = input(f" user-id [{acc.get('user-id')}]: ").strip() or acc.get('user-id')
            secret = input(f" user-secret-key [{acc.get('user-secret-key')[:6]+'...'}]: ").strip() or acc.get('user-secret-key')
            nickname = input(f" nickname [{acc.get('nickname','')}]: ").strip() or acc.get('nickname')
            country = input(f" country-code [{acc.get('country-code','vn')}]: ").strip() or acc.get('country-code','vn')
            acc.update({"user-id": uid, "user-secret-key": secret, "nickname": nickname, "country-code": country})
            accounts[i] = acc
            print("-> Đã cập nhật.")
        elif c == "d":
            idx = input("Số thứ tự account cần xóa: ").strip()
            if not idx.isdigit() or int(idx) < 1 or int(idx) > len(accounts):
                print("Index không hợp lệ.")
                continue
            i = int(idx) - 1
            removed = accounts.pop(i)
            print(f"-> Đã xóa account uid={removed.get('user-id')}")
        elif c == "s":
            save_accounts(accounts)
            print("-> Đã lưu vào", ACCOUNTS_FILE)
        elif c == "q":
            yn = input("Lưu trước khi thoát? (y/n) ").strip().lower()
            if yn == "y":
                save_accounts(accounts)
                print("Đã lưu.")
            return accounts
        else:
            print("Lựa chọn không hợp lệ.")

# ============ REQUEST BUILDERS ============
def build_detail_headers(country_code="vn"):
    ts = str(int(time.time()))
    nonce = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5))
    return {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'app-ver': '',
        'content-type': 'application/json',
        'country-code': country_code,
        'nonce': nonce,
        'origin': 'https://xworld-app.com',
        'platform': 'h5',
        'priority': 'u=1, i',
        'referer': 'https://xworld-app.com/',
        'ts': ts,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'xb-language': 'en-US',
    }

def build_exchange_headers(account: Dict):
    ts = str(int(time.time()))
    nonce = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5))
    return {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'app-ver': '',
        'Connection': 'keep-alive',
        'content-type': 'application/json',
        'country-code': account.get('country-code', 'vn'),
        'Host': 'web3task.3games.io',
        'nonce': nonce,
        'Origin': 'https://xworld.info',
        'platform': 'h5',
        'Referer': 'https://xworld.info/',
        'ts': ts,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'user-id': str(account.get('user-id','')),
        'user-secret-key': str(account.get('user-secret-key','')),
        'xb-language': 'vi-VN',
    }

# ============ REQUEST FUNCTIONS ============
def detail_request(code: str, account_sample: Dict):
    session = UltraSession.get_session("detail")
    headers = build_detail_headers(country_code=account_sample.get('country-code','vn'))
    json_data = {
        'code': code,
        'os_ver': 'pc',
        'platform': 'h5',
        'appname': 'app',
    }
    try:
        resp = session.post(DETAIL_URL, headers=headers, json=json_data, timeout=DETAIL_TIMEOUT)
        return resp
    except:
        return None

def exchange_request_ultra(code: str, account: Dict, attempt: int = 0):
    """Ultra-fast exchange request với zero delay"""
    session = UltraSession.get_session(f"exchange_{account.get('user-id')}")
    headers = build_exchange_headers(account)
    payload = {"code": code}
    
    try:
        resp = session.post(EXCHANGE_URL, headers=headers, json=payload, timeout=EXCHANGE_TIMEOUT)
        return resp
    except:
        return None

# ============ RESULTS TRACKING ============
REDEEM_RESULTS = {}
REDEEM_LOCK = threading.Lock()
SUCCESS_COUNT = 0

def render_redeem_table() -> Table:
    table = Table(title="KẾT QUẢ REDEEM [ULTRA MODE]", box=box.SIMPLE_HEAVY, expand=True)
    table.add_column("USER ID", justify="center", style="cyan", no_wrap=True)
    table.add_column("VALUE", justify="right", style="green")
    table.add_column("TRẠNG THÁI", justify="left", style="bold")
    table.add_column("THÔNG BÁO", justify="left", style="dim")

    with REDEEM_LOCK:
        if not REDEEM_RESULTS:
            table.add_row("-", "-", "[yellow]Đang chờ kết quả...[/yellow]", "")
        else:
            for uid, row in REDEEM_RESULTS.items():
                val = f"{row.get('value', 0):.4f}" if row.get("value") else "-"
                msg = row.get("message", "") or ""
                code = row.get("code", None)

                if code == 0:
                    status = "[green]✓ Thành công[/green]"
                elif code == 1015:
                    status = "[yellow]Giới hạn ngày[/yellow]"
                elif code is None:
                    status = "[magenta]⚡ Đang xử lý[/magenta]"
                else:
                    status = "[red]✗ Thất bại[/red]"

                table.add_row(str(uid), val, status, msg[:60])

    return table

# ============ ULTRA EXCHANGE WORKER ============
def ultra_exchange_worker(account: Dict, code: str, worker_id: int, is_burst: bool = False):
    """Ultra-aggressive exchange worker với zero delay"""
    REDEEM_TRIGGER.wait()
    
    # Zero delay cho burst mode
    if not is_burst:
        time.sleep(worker_id * 0.02)  # Chỉ 0.02s delay
    
    uid = account.get("user-id")

    with REDEEM_LOCK:
        if uid not in REDEEM_RESULTS:
            REDEEM_RESULTS[uid] = {
                "uid": uid,
                "value": None,
                "code": None,
                "message": "⚡ Đang xử lý..."
            }

    max_attempts = RETRY_ON_FAIL + 3
    for attempt in range(max_attempts):
        try:
            resp = exchange_request_ultra(code, account, attempt)
            
            if resp is None:
                if attempt < max_attempts - 1:
                    time.sleep(0.05 * (attempt + 1))
                    continue
                else:
                    raise Exception("No response")
            
            try:
                data = resp.json()
            except:
                data = {"raw": str(resp)[:100]}

            result = {
                "uid": uid,
                "value": None,
                "message": None,
                "code": None,
            }

            if isinstance(data, dict):
                result["code"] = data.get("code")
                result["message"] = data.get("message", "")
                if isinstance(data.get("data"), dict):
                    result["value"] = data["data"].get("value", 0)

            with REDEEM_LOCK:
                current_code = REDEEM_RESULTS[uid].get("code")
                if result["code"] == 0 or current_code != 0:
                    REDEEM_RESULTS[uid] = result
                    if result["code"] == 0:
                        global SUCCESS_COUNT
                        SUCCESS_COUNT += 1
            
            if result["code"] == 0:
                break
                
        except Exception as e:
            if attempt == max_attempts - 1:
                with REDEEM_LOCK:
                    if REDEEM_RESULTS[uid].get("code") != 0:
                        REDEEM_RESULTS[uid] = {
                            "uid": uid,
                            "value": None,
                            "code": -1,
                            "message": str(e)[:50],
                        }

def show_redeem_results_live():
    time.sleep(0.3)
    with Live(render_redeem_table(), console=console, refresh_per_second=5):
        while True:
            time.sleep(0.2)
            with REDEEM_LOCK:
                live_table = render_redeem_table()
            console.print(live_table, end="\r")
            
            if REDEEM_TRIGGER.is_set() and all(
                row.get("code") is not None for row in REDEEM_RESULTS.values()
            ):
                break
        time.sleep(2)

def start_redemption_ultra(accounts: List[Dict], code: str):
    console.print(f"\n⚡ [bold red]ULTRA MODE ACTIVATED - REDEEMING NOW![/bold red]")
    threading.Thread(target=show_redeem_results_live, daemon=True).start()
    REDEEM_TRIGGER.set()

def prepare_ultra_threads(accounts: List[Dict], code: str):
    console.print(f"\n🚀 [cyan]Khởi tạo ULTRA threads...[/cyan]")
    
    total_threads = 0
    threads_per_acc = EXCHANGE_THREADS_PER_ACCOUNT
    
    # Tạo normal threads
    for acc in accounts:
        for i in range(threads_per_acc):
            t = threading.Thread(
                target=ultra_exchange_worker, 
                args=(acc, code, i, False), 
                daemon=True
            )
            t.start()
            total_threads += 1
    
    # Tạo burst threads nếu bật
    if BURST_MODE:
        burst_threads = threads_per_acc * BURST_MULTIPLIER
        for acc in accounts:
            for i in range(burst_threads):
                t = threading.Thread(
                    target=ultra_exchange_worker, 
                    args=(acc, code, i, True), 
                    daemon=True
                )
                t.start()
                total_threads += 1
    
    console.print(f"✅ Đã khởi tạo {total_threads} ULTRA threads!")
    if BURST_MODE:
        console.print(f"   └─ Bao gồm {len(accounts) * burst_threads} burst threads")

# ============ ADVANCED PREDICTION ============
class UltraPredictor:
    def __init__(self):
        self.history = []
        self.max_history = 15
        
    def add_sample(self, remaining: int, timestamp: float):
        self.history.append((remaining, timestamp))
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def should_trigger(self, current_remaining: int, threshold: int) -> tuple:
        """Trả về (should_trigger, confidence, reason)"""
        if len(self.history) < 3:
            return (current_remaining <= threshold, 0.5, "Insufficient data")
        
        # Tính tốc độ giảm
        rates = []
        for i in range(1, len(self.history)):
            prev_rem, prev_time = self.history[i-1]
            curr_rem, curr_time = self.history[i]
            time_diff = curr_time - prev_time
            if time_diff > 0:
                rate = (prev_rem - curr_rem) / time_diff
                rates.append(rate)
        
        if not rates:
            return (current_remaining <= threshold, 0.5, "No rate data")
        
        avg_rate = sum(rates) / len(rates)
        recent_rate = sum(rates[-3:]) / min(3, len(rates))
        
        # Tính acceleration (tăng tốc)
        acceleration = recent_rate - avg_rate
        
        # Dự đoán thời gian còn lại
        if recent_rate > 0:
            time_to_zero = current_remaining / recent_rate
        else:
            time_to_zero = float('inf')
        
        # Quyết định trigger
        confidence = 0.0
        reason = ""
        
        # Case 1: Tốc độ cực nhanh (>10/s)
        if recent_rate > 10:
            adjusted_threshold = threshold + 20
            should = current_remaining <= adjusted_threshold
            confidence = 0.95
            reason = f"Extreme speed: {recent_rate:.1f}/s"
            return (should, confidence, reason)
        
        # Case 2: Tốc độ nhanh (>5/s)
        elif recent_rate > 5:
            adjusted_threshold = threshold + 15
            should = current_remaining <= adjusted_threshold
            confidence = 0.85
            reason = f"High speed: {recent_rate:.1f}/s"
            return (should, confidence, reason)
        
        # Case 3: Đang tăng tốc
        elif acceleration > 2:
            adjusted_threshold = threshold + 10
            should = current_remaining <= adjusted_threshold
            confidence = 0.75
            reason = f"Accelerating: +{acceleration:.1f}/s²"
            return (should, confidence, reason)
        
        # Case 4: Sắp hết trong 2 giây
        elif time_to_zero < 2:
            should = True
            confidence = 0.9
            reason = f"Critical: {time_to_zero:.1f}s left"
            return (should, confidence, reason)
        
        # Case 5: Normal
        else:
            should = current_remaining <= threshold
            confidence = 0.6
            reason = f"Normal: {recent_rate:.1f}/s"
            return (should, confidence, reason)

# ============ ULTRA MONITOR ============
def ultra_monitor_loop(code: str, accounts: List[Dict]):
    sample = accounts[0] if accounts else {"country-code": "vn"}
    latest_info = {
        "progress": 0,
        "user_cnt": 0,
        "remaining": 0,
        "value": 0.0,
        "title": code,
        "currency": "BUILD",
        "rate": 0.0,
        "confidence": 0.0
    }
    
    predictor = UltraPredictor()

    def make_table() -> Table:
        table = Table(title="⚡ XWORLD ULTRA MONITOR ⚡", box=box.DOUBLE_EDGE)
        table.add_column("CODE", justify="left", style="bold cyan")
        table.add_column("CURRENCY", justify="left", style="white")
        table.add_column("PROGRESS", justify="right", style="white")
        table.add_column("REMAINING", justify="right", style="bold yellow")
        table.add_column("RATE", justify="right", style="magenta")
        table.add_column("VALUE", justify="right", style="green")

        color = "red" if latest_info["remaining"] <= REMAINING_THRESHOLD else "green"
        rate_str = f"{latest_info['rate']:.1f}/s" if latest_info['rate'] > 0 else "-"
        
        table.add_row(
            str(code),
            str(latest_info.get("currency","-")),
            f"{latest_info['progress']}/{latest_info['user_cnt']}",
            f"[{color}]{latest_info['remaining']}[/{color}]",
            rate_str,
            f"{latest_info['value']:.2f}"
        )
        
        conf = latest_info.get('confidence', 0)
        conf_color = "green" if conf > 0.8 else "yellow" if conf > 0.6 else "red"
        table.caption = f"[dim]Threshold: {REMAINING_THRESHOLD} | Threads: {EXCHANGE_THREADS_PER_ACCOUNT}/acc | Confidence: [{conf_color}]{conf:.0%}[/{conf_color}][/dim]"
        return table

    check_interval = 0.12
    num_monitors = 6  # 6 monitor threads
    
    def monitor_thread(name, initial_delay):
        time.sleep(initial_delay)
        last_remaining = None
        last_time = time.time()
        
        while not TRIGGERED.is_set():
            try:
                resp = detail_request(code, sample)
                if not resp:
                    time.sleep(check_interval)
                    continue
                    
                j = resp.json()
                if "data" in j:
                    d = j["data"]
                    latest_info["progress"] = d.get("progress", 0)
                    latest_info["user_cnt"] = d.get("user_cnt", 0)
                    latest_info["remaining"] = d["user_cnt"] - d["progress"]
                    latest_info["value"] = d.get("value", 0.0)
                    latest_info["title"] = d.get("title", code)
                    latest_info["currency"] = d.get("currency","-")
                    
                    # Tính rate
                    current_time = time.time()
                    if last_remaining is not None:
                        time_diff = current_time - last_time
                        if time_diff > 0:
                            rate = (last_remaining - latest_info["remaining"]) / time_diff
                            latest_info["rate"] = max(0, rate)
                    
                    last_remaining = latest_info["remaining"]
                    last_time = current_time
                    
                    # Check new user only
                    new = d.get("only_new_user")
                    if new == 1:
                        console.print("\n⚠️ [bold red]Code chỉ dành cho user mới!")
                        TRIGGERED.set()
                        exit()

                    # Prediction
                    predictor.add_sample(latest_info["remaining"], current_time)
                    should_trigger, confidence, reason = predictor.should_trigger(
                        latest_info["remaining"],
                        REMAINING_THRESHOLD
                    )
                    
                    latest_info["confidence"] = confidence
                    
                    if should_trigger and not TRIGGERED.is_set():
                        with LOCK:
                            if not TRIGGERED.is_set():
                                TRIGGERED.set()
                                live.stop()
                                console.print(f"\n⚡ [bold red]TRIGGER! {reason}[/bold red]")
                                start_redemption_ultra(accounts, code)
                                
            except Exception as e:
                pass
            
            time.sleep(check_interval)

    threads = []
    for i in range(num_monitors):
        t = threading.Thread(
            target=monitor_thread,
            args=(f"Monitor-{i+1}", i * (check_interval / num_monitors)),
            daemon=True
        )
        t.start()
        threads.append(t)

    with Live(make_table(), console=console, refresh_per_second=4) as live:
        try:
            while True:
                live.update(make_table())
                time.sleep(0.3)
        except KeyboardInterrupt:
            TRIGGERED.set()
            console.print("\n[bold yellow]Ngừng theo dõi.[/bold yellow]")

# ============ MAIN ============
def main():
    global REMAINING_THRESHOLD, EXCHANGE_THREADS_PER_ACCOUNT, BURST_MODE
    
    console.print("[bold red]╔═══════════════════════════════════════════╗[/bold red]")
    console.print("[bold red]║   XWORLD ULTRA REDEEM - AGGRESSIVE v3.0  ║[/bold red]")
    console.print("[bold red]╚═══════════════════════════════════════════╝[/bold red]")
    
    console.print("\n[yellow]⚡ Đang tối ưu hệ thống...[/yellow]")
    pre_resolve_dns()
    
    accounts = manage_accounts()
    if not accounts:
        print("Không có account. Thoát.")
        return
    
    # Pre-warm connections
    if PRE_WARM_CONNECTIONS:
        UltraSession.warm_up(accounts, "")
    
    while True:
        code = input("\nNhập GIFT CODE để giám sát: ").strip()
        sample = accounts[0] if accounts else {"country-code": "vn"}
        res = detail_request(code, sample)
        try:
            new = res.json().get("data",{}).get("only_new_user",0)
            if new == 1:
                print("\n⚠️ Code chỉ dành cho user mới!")
            else:
                break
        except:
            pass
    
    if not code:
        return
    
    console.print("\n[bold yellow]═══ CẤU HÌNH ULTRA MODE ═══[/bold yellow]")
    
    threshold_input = input(f"Ngưỡng trigger (mặc định {REMAINING_THRESHOLD}): ").strip()
    if threshold_input.isdigit():
        REMAINING_THRESHOLD = int(threshold_input)
    
    threads_input = input(f"Threads/account (mặc định {EXCHANGE_THREADS_PER_ACCOUNT}, max 20): ").strip()
    if threads_input.isdigit():
        EXCHANGE_THREADS_PER_ACCOUNT = max(1, min(20, int(threads_input)))
    
    burst_input = input("Bật BURST MODE? (y/n, mặc định y): ").strip().lower()
    if burst_input == "n":
        BURST_MODE = False
    
    total_threads = len(accounts) * EXCHANGE_THREADS_PER_ACCOUNT
    if BURST_MODE:
        total_threads += len(accounts) * EXCHANGE_THREADS_PER_ACCOUNT * BURST_MULTIPLIER
    
    console.print(f"\n[bold green]═══ THIẾT LẬP HOÀN TẤT ═══[/bold green]")
    console.print(f"Accounts: {len(accounts)} | Code: {code}")
    console.print(f"Ngưỡng: {REMAINING_THRESHOLD} | Threads/acc: {EXCHANGE_THREADS_PER_ACCOUNT}")
    console.print(f"Burst Mode: {'✓ BẬT' if BURST_MODE else '✗ TẮT'}")
    console.print(f"Tổng threads: [bold cyan]{total_threads}[/bold cyan]")
    
    yn = input("\n🚀 Bắt đầu ULTRA MODE? (y/n): ").strip().lower()
    if yn != "y":
        return
    
    prepare_ultra_threads(accounts, code)
    save_accounts(accounts)
    
    console.print("\n[green]✓ Sẵn sàng chiến đấu![/green]")
    time.sleep(1)
    clear_terminal()
    
    ultra_monitor_loop(code, accounts)
    
    # Hiển thị kết quả cuối
    console.print(f"\n[bold]Tổng kết: {SUCCESS_COUNT}/{len(accounts)} accounts thành công[/bold]")

if __name__ == "__main__":
    main()
