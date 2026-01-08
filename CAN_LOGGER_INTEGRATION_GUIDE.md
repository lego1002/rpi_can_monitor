# CAN Logger v4 LEGO 功能集成指南

## 📋 文檔版本
- **版本**: 1.0
- **日期**: 2026年1月8日
- **適用對象**: 系統集成人員、運維人員

---

## 🎯 功能概述

### 核心功能
新的 CAN Logger v4 LEGO 版本具備以下功能：

1. **實時 CAN 總線監控**
   - 監聽 CAN ID: 0x281 (VCU 狀態)、0x193 (左後輪速)、0x194 (右後輪速)
   - 支持雙 CAN 總線 (can0, can1) 或虛擬 CAN (vcan0) 測試

2. **RTD 自動啟停檢測**
   - 監測 VCU 狀態從 0x00→0x20 (RUNNING) 自動開始記錄
   - 監測 VCU 狀態從 0x20→0x00 自動停止記錄
   - 自動計算行程里程並保存

3. **輪速里程計算**
   - 使用梯形積分算法計算行程距離
   - 精度: ±0.01 km/h (基於輪速編碼: 0.01 km/h per 1 unit)
   - 自動累計總里程

4. **日誌管理**
   - 所有 CAN 訊息記錄到 CSV 文件
   - 20 分鐘自動輪換日誌文件
   - 累計里程單獨保存

---

## 📦 系統要求

### 硬體要求
- Raspberry Pi 3B+ 或更高版本
- CAN 通訊模塊（MCP2515 或類似）或虛擬 CAN 用於測試
- SD 卡 (至少 8GB)

### 軟體要求
```bash
# Python 3.7+
python3 --version

# 必需的 Python 模塊
pip install python-can
pip install flask  # 如果使用 API 服務

# CAN 工具
sudo apt-get install can-utils
```

### 目錄結構要求
```
~/Desktop/RPI_Desktop/
├── scripts/
│   ├── canlogging-v4_lego.py      # 主程序
│   ├── setup-service.sh             # 服務管理腳本
│   └── test_can_sender.py           # 測試數據發送器
├── services/
│   ├── canlogging-lego.service      # systemd 服務配置
│   └── wheel-speed-api.service      # API 服務配置
├── LOGS/                             # 日誌目錄（自動創建）
└── templates/ & static/              # Web 界面文件
```

---

## 🚀 安裝步驟

### 第 1 步：準備環境
```bash
cd ~/Desktop/RPI_Desktop

# 創建必需的目錄
mkdir -p scripts services LOGS

# 確保虛擬 CAN 模塊已加載（測試用）
sudo modprobe vcan
```

### 第 2 步：複製文件
確保以下文件在正確位置：
```bash
# 複製主程序到 scripts
cp canlogging-v4_lego.py scripts/

# 複製服務配置到 services
cp canlogging-lego.service services/
cp wheel-speed-api.service services/

# 複製管理腳本
cp setup-service.sh scripts/
chmod +x scripts/setup-service.sh
```

### 第 3 步：配置 systemd 服務

編輯 `services/canlogging-lego.service`：
```ini
[Unit]
Description=CAN Logger for LEGO Vehicle Monitoring
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Desktop/RPI_Desktop/scripts
ExecStart=/usr/bin/python3 canlogging-v4_lego.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### 第 4 步：安裝服務
```bash
# 安裝 systemd 服務
sudo bash scripts/setup-service.sh install

# 啟用開機自啟
sudo bash scripts/setup-service.sh enable

# 啟動服務
sudo bash scripts/setup-service.sh start

# 檢查狀態
sudo systemctl status canlogging-lego.service
```

---

## ⚙️ 配置說明

### CAN 接口配置

#### 實際硬體設置 (MCP2515 或類似)
```bash
# 啟動 CAN 接口（1Mbps）
sudo ip link set can0 up type can bitrate 1000000
sudo ip link set can1 up type can bitrate 1000000

# 驗證
ip link show can0
```

#### 虛擬 CAN 設置 (測試用)
```bash
# 創建虛擬 CAN 接口
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# 驗證
ip link show vcan0
```

### 程序自適應
程序會自動按以下優先級連接：
1. 虛擬 CAN (vcan0) - 優先用於測試
2. 實際 CAN (can0)
3. 實際 CAN (can1)

如果連接失敗，程序會自動重新嘗試並切換介面。

### 日誌位置
所有日誌保存在：
```
~/Desktop/RPI_Desktop/LOGS/
```

主要文件：
- `trip_distance_cumulative.csv` - 累計里程和最新行程信息
- `can_log_[TIMESTAMP].csv` - CAN 訊息原始記錄
- `can_logger_error.log` - 錯誤日誌

---

## 📊 數據格式規範

### 輪速編碼標準
```
輪速 (km/h) = (byte5 << 8 | byte4) × 0.01

例子：
- 10 km/h   → 1000   (0x03E8) → byte4=0xE8, byte5=0x03
- 50 km/h   → 5000   (0x1388) → byte4=0x88, byte5=0x13
- 100 km/h  → 10000  (0x2710) → byte4=0x10, byte5=0x27
```

### CAN 訊號定義

| CAN ID | 名稱 | 用途 | Byte 說明 |
|--------|------|------|---------|
| 0x281 | VCU 狀態 | RTD 控制 | byte0: 0x20=RUNNING, 0x00=STOPPED |
| 0x193 | 左後輪速 | 里程計算 | byte4-5: 輪速 (見上表) |
| 0x194 | 右後輪速 | 里程計算 | byte4-5: 輪速 (見上表) |
| 0x420 | 控制命令 | 手動控制 | 0x01=開始, 0x02=停止 |
| 0x421 | 狀態反饋 | 系統狀態 | byte0: 0x01=記錄中, 0x00=空閒 |

### 里程計算算法
使用梯形積分：
```
距離 = (左輪速 + 右輪速) / 2 × Δt / 3600

其中：
- 左輪速、右輪速: km/h
- Δt: 時間差 (秒)
- 結果: 公里 (km)
```

---

## 🧪 測試方法

### 方法 1：自動化測試 (推薦)

**終端 1** - 啟動主程序：
```bash
cd ~/Desktop/RPI_Desktop/scripts
python3 canlogging-v4_lego.py
```

**終端 2** - 運行測試發送器：
```bash
cd ~/Desktop/RPI_Desktop
python3 test_can_sender.py
```

測試發送器將自動執行：
1. 發送 VCU 啟動信號 (0x20)
2. 模擬加速 (0→50 km/h)
3. 保持高速 (50 km/h × 5秒)
4. 模擬減速 (50→0 km/h)
5. 發送 VCU 停止信號 (0x00)

### 方法 2：手動發送 CAN 訊號
```bash
# 發送 VCU 啟動
cansend vcan0 281#2000000000000000

# 發送輪速 50 km/h (左輪)
cansend vcan0 193#00000000881300000

# 發送輪速 50 km/h (右輪)
cansend vcan0 194#00000000881300000

# 監聽 CAN 訊號
candump vcan0
```

### 驗證結果
```bash
# 檢查日誌是否生成
ls -la ~/Desktop/RPI_Desktop/LOGS/

# 查看累計里程
cat ~/Desktop/RPI_Desktop/LOGS/trip_distance_cumulative.csv

# 查看原始 CAN 訊息
head -50 ~/Desktop/RPI_Desktop/LOGS/can_log_*.csv
```

---

## 📈 預期測試結果

### 標準測試
運行 `test_can_sender.py` 後預期的結果：

| 指標 | 期望值 | 容差 |
|------|--------|------|
| 累計里程 | ~0.147 km | ±5% |
| 行程時間 | ~19 秒 | ±1秒 |
| 平均速度 | ~27.9 km/h | ±10% |
| 輪速序列 | 0→50→0 | 精確 |

### 可靠性指標
- **里程計算精度**: 使用梯形積分，誤差 < 2%
- **時間精度**: 基於系統時鐘，精確到毫秒
- **丟包率**: < 0.1% (在正常 CAN 總線上)

---

## 🔧 故障排除

### 問題 1: "Network is down [Error Code 100]"
**原因**: CAN 接口未正確初始化
**解決方案**:
```bash
# 重置虛擬 CAN
sudo modprobe vcan
sudo ip link del vcan0 2>/dev/null || true
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

# 驗證
ip link show vcan0
```

### 問題 2: 沒有接收到 CAN 訊號
**原因**: 接收器和發送器使用了不同的 CAN 接口
**解決方案**:
- 確保都用 vcan0 進行測試
- 或都連接到 can0/can1

### 問題 3: 日誌文件為空
**原因**: VCU 狀態訊號沒有被正確識別
**檢查**:
```bash
# 監聽 CAN 訊號看是否有 0x281
candump vcan0 | grep 281

# 檢查發送的數據格式
cansend vcan0 281#2000000000000000
```

### 問題 4: 里程計算不正確
**原因**: 輪速編碼格式不對
**檢查**:
- 輪速應該在 byte4-5，不是 byte0-1
- 低位在 byte4，高位在 byte5

### 問題 5: 服務無法自動啟動
**原因**: 權限問題或路徑不對
**解決方案**:
```bash
# 檢查服務狀態
sudo systemctl status canlogging-lego.service

# 查看詳細日誌
sudo journalctl -u canlogging-lego.service -n 50

# 重新安裝服務
sudo bash ~/Desktop/RPI_Desktop/scripts/setup-service.sh install
sudo bash ~/Desktop/RPI_Desktop/scripts/setup-service.sh enable
```

---

## 📱 API 服務集成 (選項)

如果需要遠程訪問數據，可使用 wheel-speed-api.py：

```bash
# 啟動 API 服務
python3 ~/Desktop/RPI_Desktop/wheel-speed-api.py
```

### API 端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/health` | GET | 健康檢查 |
| `/api/wheel-speed` | GET | 當前輪速 |
| `/api/odometry` | GET | 累計里程 |
| `/api/status` | GET | 系統狀態 |
| `/api/config` | GET | 配置信息 |

### 測試 API
```bash
# 從 RPi 上
curl http://localhost:5000/api/status

# 從其他設備（替換 IP）
curl http://192.168.1.100:5000/api/status
```

---

## 📝 日常運維

### 啟動/停止服務
```bash
# 啟動
sudo systemctl start canlogging-lego.service

# 停止
sudo systemctl stop canlogging-lego.service

# 重啟
sudo systemctl restart canlogging-lego.service

# 查看狀態
sudo systemctl status canlogging-lego.service
```

### 查看實時日誌
```bash
# 實時跟蹤服務日誌
sudo journalctl -u canlogging-lego.service -f

# 查看最近 100 行
sudo journalctl -u canlogging-lego.service -n 100

# 只查看錯誤
sudo journalctl -u canlogging-lego.service -p err
```

### 清除舊日誌
```bash
# 刪除超過 7 天的日誌
find ~/Desktop/RPI_Desktop/LOGS -name "can_log_*.csv" -mtime +7 -delete

# 但保留 trip_distance_cumulative.csv
ls ~/Desktop/RPI_Desktop/LOGS/trip_distance_cumulative.csv
```

---

## 🔐 安全性考慮

1. **日誌文件權限**
   ```bash
   chmod 644 ~/Desktop/RPI_Desktop/LOGS/*.csv
   ```

2. **API 訪問控制** (如果使用 API 服務)
   - 建議在內網使用
   - 或添加認證機制

3. **系統日誌**
   - 定期檢查 `/var/log/syslog` 的異常

---

## 📞 支持信息

### 關鍵文件位置
```
主程序: ~/Desktop/RPI_Desktop/scripts/canlogging-v4_lego.py
服務配置: ~/Desktop/RPI_Desktop/services/canlogging-lego.service
日誌: ~/Desktop/RPI_Desktop/LOGS/
測試工具: ~/Desktop/RPI_Desktop/test_can_sender.py
```

### 快速命令參考
```bash
# 一鍵安裝
sudo bash ~/Desktop/RPI_Desktop/scripts/setup-service.sh setup-all

# 檢查所有組件
sudo systemctl status canlogging-lego.service
sudo systemctl status wheel-speed-api.service

# 完整診斷
ip link show | grep vcan
curl http://localhost:5000/api/status
tail -20 ~/Desktop/RPI_Desktop/LOGS/trip_distance_cumulative.csv
```

---

## 版本更新歷史

| 版本 | 日期 | 更改 |
|------|------|------|
| 1.0 | 2026-01-08 | 初始版本：RTD 檢測、里程計算、梯形積分 |

---

**文檔結束**

有任何問題歡迎聯繫開發團隊。
