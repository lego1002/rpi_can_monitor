# 文件組織指南 - RPI_Desktop 目錄結構

## 目錄結構設置

在您的 RPi 上，您需要在 `~/Desktop/RPI_Desktop` 建立以下目錄結構：

```
~/Desktop/RPI_Desktop/
├── scripts/
│   ├── canlogging-v4_lego.py
│   ├── wheel-speed-api.py
│   └── setup-service.sh
├── services/
│   ├── canlogging-lego.service
│   └── wheel-speed-api.service
├── LOGS/
│   └── (日誌文件會自動生成在這裡)
└── SERVICE_SETUP.md
```

## 在 RPi 上快速設置

### 方式 1：從 GitHub 直接克隆（推薦）

```bash
# 1. 進入桌面
cd ~/Desktop

# 2. 克隆倉庫（如果 RPI_Desktop 目錄還不存在）
git clone https://github.com/Ktliu-Tyler/rpi_can_monitor.git RPI_Desktop
cd RPI_Desktop

# 3. 創建必要的目錄結構
mkdir -p scripts
mkdir -p services
mkdir -p LOGS

# 4. 移動文件到正確的位置
mv canlogging-v4_lego.py scripts/
mv wheel-speed-api.py scripts/
mv setup-service.sh scripts/
mv canlogging-lego.service services/
mv wheel-speed-api.service services/
chmod +x scripts/setup-service.sh

# 5. 運行安裝
sudo bash scripts/setup-service.sh setup-all
```

### 方式 2：手動複製（如果已有 RPI_Desktop 目錄）

```bash
# 假設您已經在 RPi 上有 RPI_Desktop 目錄

# 1. 進入 RPI_Desktop
cd ~/Desktop/RPI_Desktop

# 2. 從 GitHub 下載最新文件
git pull https://github.com/Ktliu-Tyler/rpi_can_monitor.git main

# 3. 創建必要的目錄
mkdir -p scripts
mkdir -p services
mkdir -p LOGS

# 4. 移動文件
mv canlogging-v4_lego.py scripts/ 2>/dev/null
mv wheel-speed-api.py scripts/ 2>/dev/null
mv setup-service.sh scripts/ 2>/dev/null
mv canlogging-lego.service services/ 2>/dev/null
mv wheel-speed-api.service services/ 2>/dev/null
chmod +x scripts/setup-service.sh

# 5. 運行安裝
sudo bash scripts/setup-service.sh setup-all
```

### 方式 3：使用複製腳本（適用於 Windows 和 Linux）

```bash
# 在本地計算機上執行
# Linux/Mac:
bash copy-to-rpi-desktop.sh

# Windows (PowerShell):
powershell -ExecutionPolicy Bypass -File copy-to-rpi-desktop.ps1
```

## 文件說明

### scripts/ 目錄
- **canlogging-v4_lego.py** - CAN 總線數據記錄主程序
- **wheel-speed-api.py** - REST API 服務器
- **setup-service.sh** - 服務安裝和管理腳本

### services/ 目錄
- **canlogging-lego.service** - 主 CAN 記錄服務配置
- **wheel-speed-api.service** - REST API 服務配置

### LOGS/ 目錄
- 自動生成的日誌文件存放位置
- 包括 CAN 原始數據和里程記錄

## 驗證安裝

安裝完成後，驗證服務是否正確運行：

```bash
# 查看主服務狀態
sudo systemctl status canlogging-lego.service

# 查看 API 服務狀態
sudo systemctl status wheel-speed-api.service

# 查看服務日誌
sudo journalctl -u canlogging-lego.service -f

# 測試 API（在另一個終端）
curl http://localhost:5000/api/status
```

## 常見問題

### Q: 為什麼文件要放在這些特定目錄？

A: 這是一個標準的 systemd 部署結構：
- `scripts/` - 存放可執行的 Python 和 Shell 腳本
- `services/` - 存放 systemd 服務配置文件
- `LOGS/` - 存放生成的日誌和數據文件

### Q: 如果 RPI_Desktop 目錄不存在怎麼辦？

A: 手動建立它：
```bash
mkdir -p ~/Desktop/RPI_Desktop
```

### Q: 我可以改變目錄結構嗎？

A: 可以，但需要修改 `canlogging-lego.service` 和 `wheel-speed-api.service` 中的路徑。

## 故障排除

如果服務無法啟動：

1. 檢查文件是否在正確的位置
2. 確認文件權限（Python 文件需要可讀執行權限）
3. 檢查 CAN 接口是否已啟動
4. 查看詳細日誌：`sudo journalctl -u canlogging-lego.service -n 100`

## 下一步

- [查看 SERVICE_SETUP.md](./SERVICE_SETUP.md) - 完整的服務設置指南
- [查看 GitHub 倉庫](https://github.com/Ktliu-Tyler/rpi_can_monitor) - 最新代碼和文檔
