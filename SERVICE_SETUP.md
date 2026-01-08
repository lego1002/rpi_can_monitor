# CAN Logger Lego Service Setup Guide

## 概述

本指南說明如何在 Raspberry Pi 上設置 `canlogging-lego` 服務，使其能夠自動啟動並監控 CAN 總線上的輪速數據。

## 文件說明

### 1. `canlogging-lego.service`
- 主要的 CAN 數據記錄服務
- 監控 CAN ID 0x281（VCU 狀態）、0x193（左後輪速）、0x194（右後輪速）
- 自動計算里程並保存到 log 文件
- 在系統啟動時自動運行

### 2. `setup-service.sh`
- 服務安裝和管理腳本
- 提供 enable、start、stop、restart、logs 等命令

### 3. `wheel-speed-api.py`
- REST API 服務器
- 提供 HTTP 接口遠程調用輪速數據
- 監聽 0.0.0.0:5000

### 4. `wheel-speed-api.service`
- API 服務的 systemd 配置
- 依賴於 canlogging-lego.service

## 安裝步驟

### 在 RPi 上執行以下命令：

```bash
# 1. 進入項目目錄
cd /home/pi/Desktop/RPI_Desktop

# 2. 下載最新的服務文件（如果還沒有）
# 確保以下文件存在：
#   - canlogging-lego.service
#   - wheel-speed-api.service
#   - setup-service.sh
#   - canlogging-v4_lego.py
#   - wheel-speed-api.py

# 3. 安裝服務（需要 sudo）
sudo bash setup-service.sh setup-all

# 4. 檢查服務狀態
sudo systemctl status canlogging-lego.service

# 5. 查看實時日誌
sudo journalctl -u canlogging-lego.service -f
```

## 使用命令

### 使用 `setup-service.sh` 管理服務

```bash
# 安裝服務文件
sudo bash setup-service.sh install

# 啟用服務（開機自動啟動）
sudo bash setup-service.sh enable

# 啟動服務
sudo bash setup-service.sh start

# 停止服務
sudo bash setup-service.sh stop

# 重啟服務
sudo bash setup-service.sh restart

# 查看服務狀態
sudo bash setup-service.sh status

# 查看服務日誌（實時跟蹤）
sudo bash setup-service.sh logs

# 一鍵安裝、啟用和啟動
sudo bash setup-service.sh setup-all

# 卸載服務
sudo bash setup-service.sh uninstall
```

## API 使用

### 啟動 API 服務

```bash
# 安裝 Flask（如果還沒安裝）
pip install flask

# 手動啟動 API
python3 wheel-speed-api.py

# 或使用 systemd 服務（推薦）
sudo systemctl start wheel-speed-api.service
```

### API 端點

#### 1. 健康檢查
```
GET http://<RPi_IP>:5000/api/health

Response:
{
  "status": "ok",
  "service": "CAN Bus Wheel Speed API",
  "timestamp": "2026-01-08T22:30:45.123456"
}
```

#### 2. 獲取實時輪速
```
GET http://<RPi_IP>:5000/api/wheel-speed

Response:
{
  "left_rear_speed_kmh": 25.50,
  "right_rear_speed_kmh": 25.48,
  "average_speed_kmh": 25.49,
  "timestamp": "2026-01-08T22:30:45.654321",
  "rtd_active": true
}
```

#### 3. 獲取累計里程
```
GET http://<RPi_IP>:5000/api/odometry

Response:
{
  "cumulative_distance_km": 12.456789,
  "cumulative_distance_m": 12456.79,
  "timestamp": "2026-01-08T22:30:45.123456"
}
```

#### 4. 系統狀態
```
GET http://<RPi_IP>:5000/api/status

Response:
{
  "system_status": "running",
  "rtd_active": true,
  "left_rear_speed_kmh": 25.50,
  "right_rear_speed_kmh": 25.48,
  "cumulative_distance_km": 12.456789,
  "logs_directory": "/home/pi/Desktop/RPI_Desktop/LOGS",
  "timestamp": "2026-01-08T22:30:45.123456"
}
```

#### 5. 配置信息
```
GET http://<RPi_IP>:5000/api/config

Response:
{
  "can_bus": {
    "can0": "enabled",
    "can1": "enabled",
    "bitrate": 1000000
  },
  "wheel_speed_ids": {
    "left_rear": "0x193",
    "right_rear": "0x194"
  },
  "vcu_status_id": "0x281",
  "logs_location": "/home/pi/Desktop/RPI_Desktop/LOGS"
}
```

## 日誌文件位置

- **主服務日誌**：`journalctl -u canlogging-lego.service`
- **CAN 數據日誌**：`/home/pi/Desktop/RPI_Desktop/LOGS/`
- **里程記錄**：`/home/pi/Desktop/RPI_Desktop/LOGS/trip_distance_cumulative.csv`

## 疑難排解

### 服務無法啟動

```bash
# 查看詳細錯誤信息
sudo systemctl status canlogging-lego.service
sudo journalctl -u canlogging-lego.service -n 50
```

### CAN 接口無法連接

```bash
# 檢查 CAN 接口是否已啟動
ip link show can0
ip link show can1

# 如果沒有啟動，手動啟動
sudo ip link set can0 up type can bitrate 1000000
sudo ip link set can1 up type can bitrate 1000000
```

### API 無法連接

```bash
# 檢查 API 服務是否運行
sudo systemctl status wheel-speed-api.service

# 檢查端口是否開放
sudo netstat -tlnp | grep 5000
```

## 開機自啟設置

完整安裝後，服務會自動在系統啟動時運行：

```bash
# 確認服務已啟用
systemctl is-enabled canlogging-lego.service  # 應顯示 enabled
systemctl is-enabled wheel-speed-api.service   # 應顯示 enabled

# 重啟 RPi 驗證
sudo reboot

# 重啟後檢查服務
systemctl status canlogging-lego.service
systemctl status wheel-speed-api.service
```

## 手動啟動（不使用 systemd）

如果不想使用 systemd 服務，也可以手動運行：

```bash
cd /home/pi/Desktop/RPI_Desktop

# 啟動 CAN 接口
sudo ip link set can0 up type can bitrate 1000000
sudo ip link set can1 up type can bitrate 1000000

# 運行主程序
python3 canlogging-v4_lego.py

# 在另一個終端運行 API（可選）
python3 wheel-speed-api.py
```

## 網絡訪問 API

### 本地訪問
```bash
curl http://localhost:5000/api/status
```

### 遠程訪問（同一網絡）
```bash
curl http://<RPi_IP>:5000/api/status
```

其中 `<RPi_IP>` 是樹莓派的 IP 地址。

## 相關文件

- `canlogging-v4_lego.py` - 主 CAN 數據記錄程序
- `wheel-speed-api.py` - REST API 服務器
- `canlogging-lego.service` - 主服務配置
- `wheel-speed-api.service` - API 服務配置
- `setup-service.sh` - 服務管理腳本

## 支持

如有問題，請檢查：
1. 日誌文件
2. CAN 接口狀態
3. 文件權限
4. Python 依賴項
