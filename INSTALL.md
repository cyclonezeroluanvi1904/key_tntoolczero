# 🚀 HƯỚNG DẪN CÀI ĐẶT VÀ SỬ DỤNG

## 📋 Yêu Cầu Hệ Thống

### Tối thiểu:
- Python 3.7+
- RAM: 512MB
- CPU: 1 core
- Internet: Ổn định, latency < 200ms

### Khuyến nghị (cho Ultra version):
- Python 3.9+
- RAM: 2GB+
- CPU: 2+ cores
- Internet: Tốc độ cao, latency < 50ms
- VPS Singapore/Hong Kong (tốt nhất)

---

## 📦 Cài Đặt

### Bước 1: Cài đặt Python
```bash
# Kiểm tra Python đã cài chưa
python3 --version

# Nếu chưa có, cài đặt:
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip

# CentOS/RHEL
sudo yum install python3 python3-pip

# macOS
brew install python3

# Windows: Tải từ python.org
```

### Bước 2: Cài đặt thư viện
```bash
# Cài đặt các thư viện cần thiết
pip3 install requests rich urllib3

# Hoặc dùng requirements.txt (nếu có)
pip3 install -r requirements.txt
```

### Bước 3: Tải code
```bash
# Clone hoặc download các file:
# - xworld_redeem_optimized.py
# - xworld_redeem_ultra.py
# - compare_versions.py

# Cấp quyền thực thi (Linux/Mac)
chmod +x *.py
```

---

## 🎯 Sử Dụng Lần Đầu

### 1. So sánh các phiên bản
```bash
python3 compare_versions.py
```
Xem so sánh chi tiết để chọn phiên bản phù hợp.

### 2. Chạy phiên bản Optimized (khuyến nghị cho người mới)
```bash
python3 xworld_redeem_optimized.py
```

### 3. Thêm accounts
Khi chương trình chạy, chọn:
- **[L]** - Nhập link nhanh (khuyến nghị)
- **[A]** - Thêm thủ công

**Ví dụ link:**
```
https://escapemaster.net/xworld?userId=12345678&secretKey=abcdef123456&language=vi-VN
```

Dán nhiều link cùng lúc (mỗi link 1 dòng), sau đó Enter 2 lần.

### 4. Lưu accounts
Chọn **[S]** để lưu vào file `accounts_code.json`

### 5. Thoát quản lý accounts
Chọn **[Q]** và chọn **y** để lưu

### 6. Nhập gift code
```
Nhập GIFT CODE để giám sát: 31025xw
```

### 7. Cấu hình
```
Ngưỡng còn lại để redeem (mặc định 15): 20
Số luồng mỗi account (mặc định 8): 10
Bật chế độ dự đoán thông minh? (y/n): y
```

### 8. Bắt đầu monitor
```
Bắt đầu monitor ngay? (y/n): y
```

Chương trình sẽ tự động theo dõi và redeem khi đến ngưỡng!

---

## 🔥 Sử Dụng Ultra Version

### Khi nào dùng Ultra?
- Code có giá trị cao
- Nhiều người tranh giành (>100 người)
- Bạn có VPS/máy mạnh
- Muốn tối đa hóa cơ hội

### Chạy Ultra:
```bash
python3 xworld_redeem_ultra.py
```

### Cấu hình Ultra (cho code HOT):
```
Ngưỡng trigger: 25-30
Threads/account: 15-20
Bật BURST MODE? (y/n): y
```

### Cấu hình Ultra (cho code bình thường):
```
Ngưỡng trigger: 20
Threads/account: 12
Bật BURST MODE? (y/n): n
```

---

## ⚙️ Tối Ưu Hệ Thống

### Linux/Mac:

#### 1. Tăng file descriptors limit
```bash
# Tạm thời (session hiện tại)
ulimit -n 4096

# Vĩnh viễn
echo "* soft nofile 4096" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 4096" | sudo tee -a /etc/security/limits.conf
```

#### 2. Tối ưu TCP (Linux)
```bash
# Tạm thời
sudo sysctl -w net.ipv4.tcp_tw_reuse=1
sudo sysctl -w net.ipv4.ip_local_port_range="1024 65535"
sudo sysctl -w net.ipv4.tcp_fin_timeout=30

# Vĩnh viễn
sudo tee -a /etc/sysctl.conf << EOF
net.ipv4.tcp_tw_reuse=1
net.ipv4.ip_local_port_range=1024 65535
net.ipv4.tcp_fin_timeout=30
EOF

sudo sysctl -p
```

#### 3. Kiểm tra latency
```bash
# Ping đến server XWorld
ping web3task.3games.io

# Traceroute
traceroute web3task.3games.io
```

### Windows:

#### 1. Chạy PowerShell as Administrator
```powershell
# Tăng connection limit
netsh int tcp set global autotuninglevel=normal
netsh int tcp set global chimney=enabled
```

#### 2. Kiểm tra latency
```cmd
ping web3task.3games.io
tracert web3task.3games.io
```

---

## 🖥️ Chạy Trên VPS

### Khuyến nghị VPS:
- **Vị trí**: Singapore, Hong Kong, Tokyo
- **RAM**: 1GB+ (2GB+ cho Ultra)
- **CPU**: 1+ cores (2+ cho Ultra)
- **Nhà cung cấp**: DigitalOcean, Vultr, Linode, AWS Lightsail

### Setup VPS:

#### 1. Kết nối SSH
```bash
ssh root@your-vps-ip
```

#### 2. Cài đặt Python và dependencies
```bash
# Ubuntu/Debian
apt update
apt install -y python3 python3-pip git screen

# CentOS
yum install -y python3 python3-pip git screen
```

#### 3. Upload code
```bash
# Cách 1: Git (nếu có repo)
git clone your-repo-url
cd your-repo

# Cách 2: SCP từ máy local
scp xworld_redeem_*.py root@your-vps-ip:/root/
```

#### 4. Cài đặt thư viện
```bash
pip3 install requests rich urllib3
```

#### 5. Chạy trong screen (để không bị ngắt khi đóng SSH)
```bash
# Tạo screen session
screen -S xworld

# Chạy script
python3 xworld_redeem_ultra.py

# Detach: Ctrl+A, D
# Reattach: screen -r xworld
# List sessions: screen -ls
```

#### 6. Tối ưu VPS
```bash
# Tăng limits
ulimit -n 4096

# Tối ưu TCP
sysctl -w net.ipv4.tcp_tw_reuse=1
sysctl -w net.ipv4.ip_local_port_range="1024 65535"
```

---

## 🐛 Xử Lý Lỗi Thường Gặp

### 1. ModuleNotFoundError: No module named 'requests'
```bash
pip3 install requests rich urllib3
```

### 2. Too many open files
```bash
ulimit -n 4096
```

### 3. Connection timeout
- Kiểm tra internet: `ping 8.8.8.8`
- Kiểm tra DNS: `nslookup web3task.3games.io`
- Giảm số threads
- Thử VPS khác

### 4. Permission denied
```bash
chmod +x xworld_redeem_*.py
```

### 5. JSON decode error
- File `accounts_code.json` bị lỗi
- Xóa file và thêm lại accounts

### 6. Server 503 (Service Unavailable)
- Server đang quá tải
- Đợi vài giây và thử lại
- Tool sẽ tự động retry

### 7. Code 1015 (Daily limit)
- Account đã hết lượt redeem trong ngày
- Thử account khác

---

## 📊 Monitoring

### Kiểm tra CPU/RAM usage:

#### Linux/Mac:
```bash
# Trong terminal khác
top
# hoặc
htop

# Xem process cụ thể
ps aux | grep python
```

#### Windows:
- Mở Task Manager (Ctrl+Shift+Esc)
- Tìm process Python

### Kiểm tra network:
```bash
# Linux
iftop
# hoặc
nethogs

# Xem connections
netstat -an | grep ESTABLISHED | wc -l
```

---

## 🔒 Bảo Mật

### 1. Bảo vệ file accounts
```bash
# Chỉ owner đọc được
chmod 600 accounts_code.json
```

### 2. Không chia sẻ secret key
- Không commit lên Git
- Không gửi cho người khác
- Không screenshot có chứa secret key

### 3. Backup accounts
```bash
# Backup định kỳ
cp accounts_code.json accounts_code.json.backup

# Hoặc tự động
crontab -e
# Thêm dòng:
0 0 * * * cp /path/to/accounts_code.json /path/to/backup/accounts_$(date +\%Y\%m\%d).json
```

---

## 📈 Tips Nâng Cao

### 1. Chạy nhiều instances
```bash
# Terminal 1
python3 xworld_redeem_ultra.py  # accounts 1-5

# Terminal 2
python3 xworld_redeem_ultra.py  # accounts 6-10
```

### 2. Auto-restart khi crash
```bash
# Tạo script restart.sh
cat > restart.sh << 'EOF'
#!/bin/bash
while true; do
    python3 xworld_redeem_ultra.py
    echo "Crashed! Restarting in 5s..."
    sleep 5
done
EOF

chmod +x restart.sh
./restart.sh
```

### 3. Log output
```bash
python3 xworld_redeem_ultra.py 2>&1 | tee output.log
```

### 4. Chạy background
```bash
nohup python3 xworld_redeem_ultra.py > output.log 2>&1 &

# Xem log
tail -f output.log

# Kill process
ps aux | grep python
kill <PID>
```

---

## 🎓 Best Practices

1. **Test trước**: Thử với code ít giá trị trước
2. **Backup**: Lưu file accounts thường xuyên
3. **Monitor**: Theo dõi CPU/RAM/Network
4. **Không lạm dụng**: Quá nhiều requests có thể bị ban
5. **Cập nhật**: Kiểm tra version mới thường xuyên
6. **VPS**: Dùng VPS gần server để giảm latency
7. **Cấu hình hợp lý**: Không set threads quá cao nếu mạng yếu

---

## 📞 Hỗ Trợ

### Kiểm tra trước khi hỏi:
1. ✅ Python version >= 3.7?
2. ✅ Đã cài đặt đủ thư viện?
3. ✅ Internet ổn định?
4. ✅ File accounts_code.json hợp lệ?
5. ✅ Đã đọc README_OPTIMIZATION.md?

### Debug:
```bash
# Chạy với verbose mode
python3 -u xworld_redeem_ultra.py

# Kiểm tra Python
python3 --version
pip3 list | grep -E "requests|rich|urllib3"

# Kiểm tra network
ping -c 5 web3task.3games.io
curl -I https://web3task.3games.io
```

---

## 🎉 Kết Luận

**Quy trình chuẩn:**
1. Cài đặt Python + thư viện
2. Chạy `compare_versions.py` để chọn version
3. Thêm accounts
4. Cấu hình phù hợp
5. Test với code ít giá trị
6. Sử dụng thực tế

**Khuyến nghị:**
- Người mới: **Optimized Version**
- Người có kinh nghiệm: **Ultra Version**
- Code cực hot: **Ultra + VPS Singapore + Burst Mode**

**Good luck! 🍀**
