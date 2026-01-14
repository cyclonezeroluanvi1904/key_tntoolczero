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

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

ACCOUNTS_FILE = "accounts_code.json"
DETAIL_URL = "https://web3task.3games.io/v1/task/redcode/detail"
EXCHANGE_URL = "https://web3task.3games.io/v1/task/redcode/exchange"

LOCK = threading.Lock()
TRIGGERED = threading.Event()

# ============ OPTIMIZED SETTINGS ============
DETAIL_INTERVAL = 0.3           # Giảm từ 1s xuống 0.3s - check nhanh hơn
DETAIL_TIMEOUT = 3.0            # Giảm timeout để phát hiện lỗi nhanh hơn
EXCHANGE_TIMEOUT = 4.0          # Timeout cho exchange
REMAINING_THRESHOLD = 15        # Tăng ngưỡng để trigger sớm hơn
RETRY_ON_FAIL = 3               # Tăng số lần retry
EXCHANGE_THREADS_PER_ACCOUNT = 8  # Tăng từ 4 lên 8 threads mỗi account
PREDICTIVE_TRIGGER = True       # Bật chế độ dự đoán
AGGRESSIVE_MODE = True          # Chế độ tấn công mạnh

# Connection pooling settings
MAX_POOL_CONNECTIONS = 50
MAX_POOL_SIZE = 100

REDEEM_TRIGGER = threading.Event()

# ============ CONNECTION POOL ============
class OptimizedSession:
    """Session với connection pooling và retry tối ưu"""
    _instances = {}
    _lock = threading.Lock()
    
    @classmethod
    def get_session(cls, session_type="detail"):
        with cls._lock:
            if session_type not in cls._instances:
                session = requests.Session()
                
                # Cấu hình retry strategy
                retry_strategy = Retry(
                    total=RETRY_ON_FAIL,
                    backoff_factor=0.1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["POST", "GET"]
                )
                
                adapter = HTTPAdapter(
                    max_retries=retry_strategy,
                    pool_connections=MAX_POOL_CONNECTIONS,
                    pool_maxsize=MAX_POOL_SIZE,
                    pool_block=False
                )
                
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                
                # Keep-alive
                session.headers.update({'Connection': 'keep-alive'})
                
                cls._instances[session_type] = session
            
            return cls._instances[session_type]

# ============ DNS PRE-RESOLUTION ============
def pre_resolve_dns():
    """Pre-resolve DNS để giảm latency"""
    try:
        domains = ["web3task.3games.io", "xworld-app.com", "xworld.info"]
        for domain in domains:
            socket.gethostbyname(domain)
        console.print("[green]✓ DNS pre-resolved[/green]")
    except Exception as e:
        console.print(f"[yellow]⚠ DNS pre-resolve warning: {e}[/yellow]")

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
    """Tách userId và secretKey từ link"""
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

# ============ OPTIMIZED REQUEST BUILDERS ============
def build_detail_headers(country_code="vn"):
    ts = str(int(time.time()))
    nonce = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5))
    headers = {
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
    return headers

def build_exchange_headers(account: Dict):
    ts = str(int(time.time()))
    nonce = "".join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=5))
    
    headers = {
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
    return headers

# ============ OPTIMIZED REQUEST FUNCTIONS ============
def detail_request(code: str, account_sample: Dict):
    """Request với connection pooling"""
    session = OptimizedSession.get_session("detail")
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
    except requests.RequestException as e:
        return None

def exchange_request(code: str, account: Dict):
    """Exchange request tối ưu với session pooling"""
    session = OptimizedSession.get_session(f"exchange_{account.get('user-id')}")
    headers = build_exchange_headers(account)
    payload = {"code": code}
    
    try:
        resp = session.post(EXCHANGE_URL, headers=headers, json=payload, timeout=EXCHANGE_TIMEOUT)
        return resp
    except requests.RequestException as e:
        return None

# ============ REDEEM RESULTS TRACKING ============
console = Console()
REDEEM_RESULTS = {}
REDEEM_LOCK = threading.Lock()

def render_redeem_table() -> Table:
    """Tạo bảng Rich hiển thị kết quả redeem"""
    table = Table(title="KẾT QUẢ REDEEM", box=box.SIMPLE_HEAVY, expand=True)
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
                    status = "[green]Thành công[/green]"
                elif code == 1015:
                    status = "[yellow]Giới hạn ngày[/yellow]"
                elif code is None:
                    status = "[magenta]Đang xử lý[/magenta]"
                else:
                    status = "[red]Thất bại[/red]"

                table.add_row(str(uid), val, status, msg[:60])

    return table

# ============ OPTIMIZED EXCHANGE WORKER ============
def exchange_wait_worker(account: Dict, code: str, delay_index: int):
    """Luồng redeem tối ưu - chờ trigger và thực thi ngay lập tức"""
    REDEEM_TRIGGER.wait()

    # Giảm delay giữa các thread xuống 0.05s để nhanh hơn
    time.sleep(delay_index * 0.05)

    uid = account.get("user-id")

    with REDEEM_LOCK:
        if uid not in REDEEM_RESULTS:
            REDEEM_RESULTS[uid] = {
                "uid": uid,
                "value": None,
                "code": None,
                "message": "Đang xử lý..."
            }

    # Thử nhiều lần với backoff
    max_attempts = RETRY_ON_FAIL + 2  # Tăng thêm 2 lần thử
    for attempt in range(max_attempts):
        try:
            resp = exchange_request(code, account)
            
            if resp is None:
                if attempt < max_attempts - 1:
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    continue
                else:
                    raise Exception("No response after retries")
            
            try:
                data = resp.json() if hasattr(resp, "json") else resp
            except Exception:
                data = {"raw": str(resp)}

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
            else:
                result["message"] = str(data)[:100]

            with REDEEM_LOCK:
                current_code = REDEEM_RESULTS[uid].get("code")
                # Cập nhật nếu thành công hoặc chưa có kết quả
                if result["code"] == 0 or current_code != 0:
                    REDEEM_RESULTS[uid] = result
            
            # Nếu thành công thì dừng
            if result["code"] == 0:
                break
                
        except Exception as e:
            if attempt == max_attempts - 1:
                with REDEEM_LOCK:
                    REDEEM_RESULTS[uid] = {
                        "uid": uid,
                        "value": None,
                        "code": -1,
                        "message": str(e),
                    }

def show_redeem_results_live():
    """Hiển thị bảng realtime kết quả redeem"""
    time.sleep(0.5)
    with Live(render_redeem_table(), console=console, refresh_per_second=4):
        while True:
            time.sleep(0.3)
            with REDEEM_LOCK:
                live_table = render_redeem_table()
            console.print(live_table, end="\r")
            
            if REDEEM_TRIGGER.is_set() and all(
                row.get("code") is not None for row in REDEEM_RESULTS.values()
            ):
                break
        time.sleep(2)

def start_redemption_for_all(accounts: List[Dict], code: str):
    console.print(f"\n⚡ [bold yellow]ĐANG CHUẨN BỊ REDEEM...[/bold yellow]")
    threading.Thread(target=show_redeem_results_live, daemon=True).start()
    REDEEM_TRIGGER.set()

def prepare_redeem_threads(accounts: List[Dict], code: str):
    console.print(f"\n🚀 [cyan]Khởi tạo các luồng redeem sẵn sàng...[/cyan]")
    total_threads = 0
    for acc in accounts:
        for i in range(EXCHANGE_THREADS_PER_ACCOUNT):
            t = threading.Thread(target=exchange_wait_worker, args=(acc, code, i), daemon=True)
            t.start()
            total_threads += 1
    console.print(f"✅ Đã khởi tạo {total_threads} luồng redeem sẵn sàng.")

# ============ PREDICTIVE MONITORING ============
class PredictiveMonitor:
    """Dự đoán thời điểm hết code dựa trên tốc độ giảm"""
    def __init__(self):
        self.history = []
        self.max_history = 10
        
    def add_sample(self, remaining: int, timestamp: float):
        self.history.append((remaining, timestamp))
        if len(self.history) > self.max_history:
            self.history.pop(0)
    
    def predict_trigger(self, current_remaining: int, threshold: int) -> bool:
        """Dự đoán xem có nên trigger sớm không"""
        if len(self.history) < 3:
            return current_remaining <= threshold
        
        # Tính tốc độ giảm trung bình
        rates = []
        for i in range(1, len(self.history)):
            prev_rem, prev_time = self.history[i-1]
            curr_rem, curr_time = self.history[i]
            time_diff = curr_time - prev_time
            if time_diff > 0:
                rate = (prev_rem - curr_rem) / time_diff
                rates.append(rate)
        
        if not rates:
            return current_remaining <= threshold
        
        avg_rate = sum(rates) / len(rates)
        
        # Nếu tốc độ giảm nhanh (>5 codes/giây), trigger sớm hơn
        if avg_rate > 5:
            adjusted_threshold = threshold + 10
            return current_remaining <= adjusted_threshold
        elif avg_rate > 2:
            adjusted_threshold = threshold + 5
            return current_remaining <= adjusted_threshold
        
        return current_remaining <= threshold

# ============ OPTIMIZED MONITOR LOOP ============
def monitor_loop(code: str, accounts: List[Dict]):
    sample = accounts[0] if accounts else {"country-code": "vn"}
    latest_info = {
        "progress": 0, 
        "user_cnt": 0, 
        "remaining": 0, 
        "value": 0.0, 
        "title": code,
        "currency": "BUILD"
    }
    
    predictor = PredictiveMonitor()

    def make_table() -> Table:
        table = Table(title="XWORLD CODE MONITOR [OPTIMIZED]", box=box.SIMPLE_HEAVY)
        table.add_column("CODE", justify="left", style="bold cyan")
        table.add_column("Currency", justify="left", style="white")
        table.add_column("PROGRESS", justify="right", style="white")
        table.add_column("USER_CNT", justify="right", style="white")
        table.add_column("REMAINING", justify="right", style="bold yellow")
        table.add_column("VALUE", justify="right", style="green")

        color = "red" if latest_info["remaining"] <= REMAINING_THRESHOLD else "green"
        table.add_row(
            str(code),
            str(latest_info.get("currency","-")),
            str(latest_info.get("progress", 0)),
            str(latest_info.get("user_cnt", 0)),
            f"[{color}]{latest_info.get('remaining', 0)}[/{color}]",
            f"{latest_info.get('value', 0.0):.2f}"
        )
        table.caption = f"[dim]Auto redeem when remaining ≤ {REMAINING_THRESHOLD} | Threads: {EXCHANGE_THREADS_PER_ACCOUNT}/acc[/dim]"
        return table

    # Tăng số luồng monitor lên 4 để check nhanh hơn
    check_interval = 0.15
    num_monitors = 4
    
    def monitor_thread(name, initial_delay):
        time.sleep(initial_delay)
        
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
                    
                    # Check new user only
                    new = d.get("only_new_user")
                    if new == 1:
                        latest_info["title"] += " (Chỉ dành cho user mới)"
                        time.sleep(2)
                        print("\n⚠️ [bold red]Code chỉ dành cho user mới! Không thể redeem.")
                        TRIGGERED.set()
                        exit()

                    # Thêm vào predictor
                    predictor.add_sample(latest_info["remaining"], time.time())
                    
                    # Kiểm tra trigger với prediction
                    should_trigger = False
                    if PREDICTIVE_TRIGGER:
                        should_trigger = predictor.predict_trigger(
                            latest_info["remaining"], 
                            REMAINING_THRESHOLD
                        )
                    else:
                        should_trigger = latest_info["remaining"] <= REMAINING_THRESHOLD
                    
                    if should_trigger and not TRIGGERED.is_set():
                        with LOCK:
                            if not TRIGGERED.is_set():
                                TRIGGERED.set()
                                live.stop()
                                console.print("\n⚡ [bold red]SẮP HẾT LƯỢT — BẮT ĐẦU REDEEM![/bold red]")
                                start_redemption_for_all(accounts, code)
                else:
                    console.print(f"[red]Response lỗi:[/red] {resp.text[:120]}")
            except Exception as e:
                pass  # Bỏ qua lỗi để không làm gián đoạn
            
            time.sleep(check_interval)

    # Khởi tạo nhiều monitor threads
    threads = []
    for i in range(num_monitors):
        t = threading.Thread(
            target=monitor_thread, 
            args=(f"Monitor-{i+1}", i * (check_interval / num_monitors)), 
            daemon=True
        )
        t.start()
        threads.append(t)

    with Live(make_table(), console=console, refresh_per_second=3) as live:
        try:
            while True:
                live.update(make_table())
                time.sleep(0.4)
        except KeyboardInterrupt:
            TRIGGERED.set()
            console.print("\n[bold yellow]Ngừng theo dõi.[/bold yellow]")

# ============ MAIN FUNCTION ============
def main():
    global REMAINING_THRESHOLD, EXCHANGE_THREADS_PER_ACCOUNT, PREDICTIVE_TRIGGER
    
    console.print("[bold cyan]╔═══════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║   XWORLD CODE REDEEM - OPTIMIZED v2.0    ║[/bold cyan]")
    console.print("[bold cyan]╚═══════════════════════════════════════════╝[/bold cyan]")
    
    # Pre-resolve DNS
    console.print("\n[yellow]Đang tối ưu kết nối...[/yellow]")
    pre_resolve_dns()
    
    accounts = manage_accounts()
    if not accounts:
        print("Không có account. Thoát.")
        return
    
    while True:
        code = input("\nNhập GIFT CODE để giám sát (ví dụ: 31025xw): ").strip()
        sample = accounts[0] if accounts else {"country-code": "vn"}

        res = detail_request(code, sample)
        try:
            new = res.json().get("data",{}).get("only_new_user",0)
            if new == 1:
                print("\n⚠️ Code chỉ dành cho user mới! Không thể redeem.")
            else:
                break
        except Exception:
            pass
    
    if not code:
        print("Không có code. Thoát.")
        return
    
    # Cấu hình nâng cao
    console.print("\n[bold yellow]═══ CẤU HÌNH NÂNG CAO ═══[/bold yellow]")
    
    threshold_input = input(f"Ngưỡng còn lại để redeem (mặc định {REMAINING_THRESHOLD}): ").strip()
    if threshold_input.isdigit():
        REMAINING_THRESHOLD = int(threshold_input)
    
    threads_input = input(f"Số luồng mỗi account (mặc định {EXCHANGE_THREADS_PER_ACCOUNT}, khuyến nghị 8-12): ").strip()
    if threads_input.isdigit():
        EXCHANGE_THREADS_PER_ACCOUNT = max(1, min(20, int(threads_input)))
    
    predictive_input = input("Bật chế độ dự đoán thông minh? (y/n, mặc định y): ").strip().lower()
    if predictive_input == "n":
        PREDICTIVE_TRIGGER = False
    
    print("\n=== Thiết lập hoàn tất ===")
    print(f"Số account: {len(accounts)} | Code: {code}")
    print(f"Ngưỡng: {REMAINING_THRESHOLD} | Threads/acc: {EXCHANGE_THREADS_PER_ACCOUNT}")
    print(f"Dự đoán thông minh: {'BẬT' if PREDICTIVE_TRIGGER else 'TẮT'}")
    
    yn = input("\nBắt đầu monitor ngay? (y/n): ").strip().lower()
    if yn != "y":
        print("Hủy. Bạn có thể chạy lại chương trình sau.")
        return
    
    # Khởi tạo threads sẵn sàng
    prepare_redeem_threads(accounts, code)
    save_accounts(accounts)
    
    console.print("\n[green]✓ Accounts đã được lưu[/green]")
    console.print("[green]✓ Khởi động monitor...[/green]")
    time.sleep(1)
    clear_terminal()
    
    monitor_loop(code, accounts)

if __name__ == "__main__":
    main()
