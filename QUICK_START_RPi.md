# RPi 快速部署指南

## 📁 文件放置位置

您需要把所有文件放到 RPi 上的這個位置：

```
~/Desktop/RPI_Desktop/
```

## 🚀 最快速的方法（一條命令）

在 **RPi 終端**上執行：

```bash
cd ~/Desktop && git clone https://github.com/Ktliu-Tyler/rpi_can_monitor.git RPI_Desktop && cd RPI_Desktop && mkdir -p scripts services LOGS && mv *.py scripts/ 2>/dev/null; mv *.sh scripts/ 2>/dev/null; mv *.service services/ 2>/dev/null; chmod +x scripts/setup-service.sh && sudo bash scripts/setup-service.sh setup-all
```

## 📋 分步驟安裝（推薦新手）

### 第 1 步：下載文件到 RPi

```bash
# 進入桌面
cd ~/Desktop

# 如果 RPI_Desktop 還不存在，克隆倉庫
git clone https://github.com/Ktliu-Tyler/rpi_can_monitor.git RPI_Desktop
cd RPI_Desktop
```

### 第 2 步：建立目錄結構

```bash
mkdir -p scripts
mkdir -p services
mkdir -p LOGS
```

### 第 3 步：移動文件到正確位置

```bash
# 移動 Python 腳本
mv canlogging-v4_lego.py scripts/ 2>/dev/null
mv wheel-speed-api.py scripts/ 2>/dev/null

# 移動 Shell 腳本
mv setup-service.sh scripts/ 2>/dev/null
chmod +x scripts/setup-service.sh

# 移動 systemd 服務文件
mv canlogging-lego.service services/ 2>/dev/null
mv wheel-speed-api.service services/ 2>/dev/null
```

### 第 4 步：安裝服務

```bash
# 一鍵安裝、啟用和啟動
sudo bash scripts/setup-service.sh setup-all
```

## ✅ 驗證安裝

### 檢查主服務

```bash
sudo systemctl status canlogging-lego.service
```

應該看到：`Active: active (running)`

### 檢查 API 服務

```bash
sudo systemctl status wheel-speed-api.service
```

### 測試 API

```bash
curl http://localhost:5000/api/status
```

### 查看實時日誌

```bash
sudo journalctl -u canlogging-lego.service -f
```

## 📊 目錄結構確認

執行這個命令驗證文件結構是否正確：

```bash
cd ~/Desktop/RPI_Desktop
tree -L 2
# 或者
find . -type f -name "*.py" -o -name "*.service" -o -name "*.sh" | sort
```

應該看到：

```
RPI_Desktop/
├── scripts/
│   ├── canlogging-v4_lego.py
│   ├── wheel-speed-api.py
│   └── setup-service.sh
├── services/
│   ├── canlogging-lego.service
│   └── wheel-speed-api.service
├── LOGS/
└── [文檔文件]
```

## 🔧 常用命令

### 查看服務狀態

```bash
systemctl status canlogging-lego.service
systemctl status wheel-speed-api.service
```

### 開啟/關閉服務

```bash
# 啟動
sudo systemctl start canlogging-lego.service

# 停止
sudo systemctl stop canlogging-lego.service

# 重啟
sudo systemctl restart canlogging-lego.service
```

### 查看日誌

```bash
# 最近 50 行
sudo journalctl -u canlogging-lego.service -n 50

# 實時跟蹤
sudo journalctl -u canlogging-lego.service -f

# 查看錯誤
sudo journalctl -u canlogging-lego.service -p err
```

## 🌐 遠程訪問輪速數據

### 獲取 RPi 的 IP 地址

```bash
hostname -I
```

### API 調用示例

#### 1. 檢查健康狀態
```bash
curl http://<RPi_IP>:5000/api/health
```

#### 2. 獲取實時輪速
```bash
curl http://<RPi_IP>:5000/api/wheel-speed
```

#### 3. 獲取累計里程
```bash
curl http://<RPi_IP>:5000/api/odometry
```

#### 4. 查看系統狀態
```bash
curl http://<RPi_IP>:5000/api/status
```

## 📂 日誌文件位置

所有日誌和數據文件都存放在：

```
~/Desktop/RPI_Desktop/LOGS/
```

主要文件：
- `can_log_*.csv` - CAN 原始數據
- `trip_distance_cumulative.csv` - 累計里程記錄

## 🐛 疑難排解

### 問題：服務無法啟動

```bash
# 查看詳細錯誤
sudo journalctl -u canlogging-lego.service -n 100

# 檢查文件是否存在
ls -la scripts/
ls -la services/

# 檢查權限
chmod +x scripts/*.py
chmod +x scripts/*.sh
```

### 問題：CAN 接口無法連接

```bash
# 檢查 CAN 接口
ip link show can0

# 手動啟動
sudo ip link set can0 up type can bitrate 1000000
```

### 問題：API 無法訪問

```bash
# 檢查端口是否開放
sudo netstat -tlnp | grep 5000

# 檢查防火牆
sudo ufw allow 5000
```

## 🔄 更新代碼

如果需要更新最新代碼：

```bash
cd ~/Desktop/RPI_Desktop
git pull https://github.com/Ktliu-Tyler/rpi_can_monitor.git main
sudo systemctl restart canlogging-lego.service
```

## 📞 獲取幫助

- 查看完整文檔：`less SERVICE_SETUP.md`
- 查看文件組織指南：`less FILE_ORGANIZATION.md`
- GitHub 倉庫：https://github.com/Ktliu-Tyler/rpi_can_monitor

---

**記住**：完整的文件結構是服務正確運行的關鍵！
