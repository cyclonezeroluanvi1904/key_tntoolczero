#!/usr/bin/env python3
"""
Script so sánh các phiên bản tối ưu
"""

from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def show_comparison():
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]        XWORLD REDEEM - SO SÁNH CÁC PHIÊN BẢN              [/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Bảng so sánh tính năng
    table1 = Table(title="🔧 SO SÁNH TÍNH NĂNG", box=box.DOUBLE_EDGE)
    table1.add_column("Tính năng", style="cyan", width=30)
    table1.add_column("Original", justify="center", style="yellow")
    table1.add_column("Optimized", justify="center", style="green")
    table1.add_column("Ultra", justify="center", style="red")
    
    features = [
        ("Check Interval", "1.0s", "0.3s", "0.12s"),
        ("Monitor Threads", "2", "4", "6"),
        ("Threads/Account", "4", "8", "12-24"),
        ("Thread Delay", "0.1s", "0.05s", "0.02s"),
        ("Connection Pooling", "❌", "✅", "✅"),
        ("DNS Pre-resolve", "❌", "✅", "✅"),
        ("Predictive Trigger", "❌", "✅ Basic", "✅ Advanced"),
        ("Burst Mode", "❌", "❌", "✅"),
        ("Pre-warming", "❌", "❌", "✅"),
        ("Rate Tracking", "❌", "❌", "✅"),
        ("Retry Strategy", "Basic", "Smart", "Ultra"),
    ]
    
    for feature in features:
        table1.add_row(*feature)
    
    console.print(table1)
    
    # Bảng hiệu suất
    table2 = Table(title="\n⚡ HIỆU SUẤT DỰ KIẾN", box=box.DOUBLE_EDGE)
    table2.add_column("Metric", style="cyan", width=30)
    table2.add_column("Original", justify="center", style="yellow")
    table2.add_column("Optimized", justify="center", style="green")
    table2.add_column("Ultra", justify="center", style="red")
    
    performance = [
        ("Tỷ lệ thành công", "30-50%", "60-75%", "75-90%"),
        ("Latency trung bình", "~200ms", "~50ms", "~20ms"),
        ("Requests/giây", "~40", "~160", "~400+"),
        ("CPU Usage", "Thấp", "Trung bình", "Cao"),
        ("RAM Usage", "~50MB", "~100MB", "~200MB"),
        ("Network Usage", "Thấp", "Trung bình", "Cao"),
    ]
    
    for perf in performance:
        table2.add_row(*perf)
    
    console.print(table2)
    
    # Bảng khuyến nghị
    table3 = Table(title="\n🎯 KHUYẾN NGHỊ SỬ DỤNG", box=box.DOUBLE_EDGE)
    table3.add_column("Tình huống", style="cyan", width=30)
    table3.add_column("Phiên bản", justify="center", style="bold")
    table3.add_column("Cấu hình", style="dim")
    
    recommendations = [
        ("Code HOT (>100 người)", "[red]Ultra[/red]", "Threshold: 25-30, Threads: 15-20, Burst: ON"),
        ("Code Trung bình", "[green]Optimized[/green]", "Threshold: 15-20, Threads: 8-12"),
        ("Code Ít người", "[yellow]Original/Optimized[/yellow]", "Cấu hình mặc định"),
        ("Máy yếu", "[yellow]Original[/yellow]", "Cấu hình mặc định"),
        ("VPS mạnh", "[red]Ultra[/red]", "Max threads, Burst ON"),
        ("Lần đầu sử dụng", "[green]Optimized[/green]", "Cấu hình mặc định"),
    ]
    
    for rec in recommendations:
        table3.add_row(*rec)
    
    console.print(table3)
    
    # Ưu nhược điểm
    console.print("\n[bold yellow]═══ ƯU NHƯỢC ĐIỂM ═══[/bold yellow]\n")
    
    console.print("[bold yellow]📌 ORIGINAL VERSION[/bold yellow]")
    console.print("  [green]✓[/green] Ổn định nhất")
    console.print("  [green]✓[/green] Ít tốn tài nguyên")
    console.print("  [green]✓[/green] Dễ sử dụng")
    console.print("  [red]✗[/red] Tỷ lệ thành công thấp với code hot")
    console.print("  [red]✗[/red] Chậm hơn các version khác\n")
    
    console.print("[bold green]📌 OPTIMIZED VERSION[/bold green]")
    console.print("  [green]✓[/green] Cân bằng giữa tốc độ và ổn định")
    console.print("  [green]✓[/green] Tỷ lệ thành công cao")
    console.print("  [green]✓[/green] Dự đoán thông minh")
    console.print("  [green]✓[/green] Phù hợp đa số trường hợp")
    console.print("  [yellow]~[/yellow] Tốn tài nguyên trung bình\n")
    
    console.print("[bold red]📌 ULTRA VERSION[/bold red]")
    console.print("  [green]✓[/green] Tốc độ cực nhanh")
    console.print("  [green]✓[/green] Tỷ lệ thành công cao nhất")
    console.print("  [green]✓[/green] Burst mode cho code hot")
    console.print("  [green]✓[/green] Advanced prediction")
    console.print("  [green]✓[/green] Real-time rate tracking")
    console.print("  [red]✗[/red] Tốn nhiều tài nguyên")
    console.print("  [red]✗[/red] Có thể bị rate limit nếu lạm dụng")
    console.print("  [yellow]~[/yellow] Cần cấu hình đúng để tối ưu\n")
    
    # Tips
    console.print("[bold cyan]═══ TIPS QUAN TRỌNG ═══[/bold cyan]\n")
    console.print("1. [yellow]Chạy trên VPS Singapore/HK[/yellow] để giảm latency")
    console.print("2. [yellow]Tăng ulimit -n 4096[/yellow] nếu dùng Ultra version")
    console.print("3. [yellow]Test với code ít giá trị[/yellow] trước khi dùng thật")
    console.print("4. [yellow]Backup file accounts_code.json[/yellow] thường xuyên")
    console.print("5. [yellow]Không chạy quá nhiều threads[/yellow] nếu mạng yếu")
    console.print("6. [yellow]Monitor CPU/RAM[/yellow] khi chạy Ultra version")
    console.print("7. [yellow]Sử dụng Burst Mode[/yellow] chỉ khi thực sự cần\n")
    
    # Ví dụ thực tế
    console.print("[bold magenta]═══ VÍ DỤ THỰC TẾ ═══[/bold magenta]\n")
    
    console.print("[bold]Scenario 1: Code BUILD 100k, 500 người tranh[/bold]")
    console.print("  → Dùng: [red]Ultra Version[/red]")
    console.print("  → Cấu hình: Threshold=30, Threads=20, Burst=ON")
    console.print("  → Kết quả dự kiến: 80-90% thành công\n")
    
    console.print("[bold]Scenario 2: Code USDT 50, 100 người tranh[/bold]")
    console.print("  → Dùng: [green]Optimized Version[/green]")
    console.print("  → Cấu hình: Threshold=20, Threads=12")
    console.print("  → Kết quả dự kiến: 70-80% thành công\n")
    
    console.print("[bold]Scenario 3: Code BUILD 10k, 50 người tranh[/bold]")
    console.print("  → Dùng: [yellow]Original/Optimized[/yellow]")
    console.print("  → Cấu hình: Mặc định")
    console.print("  → Kết quả dự kiến: 60-70% thành công\n")
    
    # Kết luận
    console.print("[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold green]🎉 KHUYẾN NGHỊ CHUNG:[/bold green]")
    console.print("   • Người mới: Bắt đầu với [green]Optimized Version[/green]")
    console.print("   • Người có kinh nghiệm: Dùng [red]Ultra Version[/red]")
    console.print("   • Code cực hot: [red]Ultra[/red] + VPS + Burst Mode")
    console.print("[bold cyan]═══════════════════════════════════════════════════════════[/bold cyan]\n")

def show_technical_details():
    console.print("\n[bold cyan]═══ CHI TIẾT KỸ THUẬT ═══[/bold cyan]\n")
    
    console.print("[bold yellow]1. CONNECTION POOLING[/bold yellow]")
    console.print("   • Tái sử dụng TCP connections")
    console.print("   • Giảm latency từ 100-200ms → 10-20ms")
    console.print("   • Tránh TCP handshake + TLS handshake mỗi request\n")
    
    console.print("[bold yellow]2. PREDICTIVE TRIGGERING[/bold yellow]")
    console.print("   • Phân tích tốc độ giảm remaining codes")
    console.print("   • Tính toán: rate = (prev - current) / time_diff")
    console.print("   • Trigger sớm khi rate > threshold")
    console.print("   • Ví dụ: rate > 10/s → trigger ở remaining=40\n")
    
    console.print("[bold yellow]3. BURST MODE[/bold yellow]")
    console.print("   • Tạo thêm threads khi trigger")
    console.print("   • Normal: 12 threads/account")
    console.print("   • Burst: +24 threads/account")
    console.print("   • Total: 36 concurrent requests/account\n")
    
    console.print("[bold yellow]4. PRE-WARMING[/bold yellow]")
    console.print("   • Mở sẵn connections trước khi monitor")
    console.print("   • Gửi dummy requests để establish connection")
    console.print("   • Khi trigger: không cần handshake → nhanh hơn\n")
    
    console.print("[bold yellow]5. ZERO-DELAY TRIGGERING[/bold yellow]")
    console.print("   • Original: 0.1s delay giữa threads")
    console.print("   • Optimized: 0.05s delay")
    console.print("   • Ultra: 0.02s delay (gần như đồng thời)\n")

def show_benchmarks():
    console.print("\n[bold cyan]═══ BENCHMARK (Giả định) ═══[/bold cyan]\n")
    
    table = Table(title="⏱️ THỜI GIAN PHẢN ỨNG", box=box.DOUBLE_EDGE)
    table.add_column("Giai đoạn", style="cyan", width=30)
    table.add_column("Original", justify="center", style="yellow")
    table.add_column("Optimized", justify="center", style="green")
    table.add_column("Ultra", justify="center", style="red")
    
    benchmarks = [
        ("DNS Lookup", "50-100ms", "0ms (cached)", "0ms (cached)"),
        ("TCP Handshake", "50-100ms", "0ms (pooled)", "0ms (pre-warmed)"),
        ("TLS Handshake", "100-200ms", "0ms (pooled)", "0ms (pre-warmed)"),
        ("Request Send", "10-20ms", "10-20ms", "10-20ms"),
        ("Server Process", "50-100ms", "50-100ms", "50-100ms"),
        ("Response Receive", "10-20ms", "10-20ms", "10-20ms"),
        ("─────────────", "─────────", "─────────", "─────────"),
        ("TOTAL (1st req)", "270-560ms", "70-140ms", "70-140ms"),
        ("TOTAL (2nd+ req)", "220-460ms", "70-140ms", "70-140ms"),
    ]
    
    for bench in benchmarks:
        table.add_row(*bench)
    
    console.print(table)
    
    console.print("\n[dim]* Thời gian thực tế phụ thuộc vào: latency mạng, server load, ISP, etc.[/dim]\n")

if __name__ == "__main__":
    show_comparison()
    
    console.print("\n[bold]Xem thêm chi tiết?[/bold]")
    console.print("  [1] Chi tiết kỹ thuật")
    console.print("  [2] Benchmark")
    console.print("  [3] Thoát")
    
    choice = input("\nChọn (1/2/3): ").strip()
    
    if choice == "1":
        show_technical_details()
    elif choice == "2":
        show_benchmarks()
    
    console.print("\n[bold green]✨ Chúc bạn redeem thành công! ✨[/bold green]\n")
