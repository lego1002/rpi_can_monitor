#!/usr/bin/env python3
"""
CAN 測試數據發送器
自動發送 RTD 信號和輪速數據到 vcan0
"""

import can
import time
import sys

def send_vcu_signal(bus, vcu_state=0x20):
    """發送 VCU 狀態信號 (0x281)"""
    msg = can.Message(
        arbitration_id=0x281,
        data=[vcu_state, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
        is_extended_id=False
    )
    bus.send(msg)
    state_name = "RUNNING (0x20)" if vcu_state == 0x20 else "STOPPED (0x00)"
    print(f"📤 VCU Signal: {state_name}")

def send_wheel_speed(bus, left_kmh, right_kmh):
    """發送輪速數據"""
    # 左輪 (0x193)
    left_raw = int(left_kmh / 0.01)
    left_low = left_raw & 0xFF
    left_high = (left_raw >> 8) & 0xFF
    
    # 右輪 (0x194)
    right_raw = int(right_kmh / 0.01)
    right_low = right_raw & 0xFF
    right_high = (right_raw >> 8) & 0xFF
    
    # 發送左輪
    msg_left = can.Message(
        arbitration_id=0x193,
        data=[0x00, 0x00, 0x00, 0x00, left_low, left_high, 0x00, 0x00],
        is_extended_id=False
    )
    bus.send(msg_left)
    
    # 發送右輪
    msg_right = can.Message(
        arbitration_id=0x194,
        data=[0x00, 0x00, 0x00, 0x00, right_low, right_high, 0x00, 0x00],
        is_extended_id=False
    )
    bus.send(msg_right)
    
    print(f"📤 輪速: Left={left_kmh:.1f} km/h, Right={right_kmh:.1f} km/h")

def main():
    print("=" * 60)
    print("CAN 測試數據發送器")
    print("=" * 60)
    
    try:
        # 連接到 vcan0
        bus = can.interface.Bus(channel='vcan0', interface='socketcan')
        print("✅ 已連接到 vcan0\n")
    except Exception as e:
        print(f"❌ 無法連接到 vcan0: {e}")
        print("請先執行：sudo modprobe vcan && sudo ip link add dev vcan0 type vcan && sudo ip link set up vcan0")
        sys.exit(1)
    
    try:
        print("🚀 開始發送測試數據...\n")
        
        # 階段 1: 發送 VCU 啟動信號
        print("[階段 1] 發送 VCU 啟動信號 (RTD)")
        send_vcu_signal(bus, 0x20)  # RUNNING
        time.sleep(1)
        
        # 階段 2: 模擬加速
        print("\n[階段 2] 模擬加速 (0 → 50 km/h)")
        speeds = [0, 10, 20, 30, 40, 50]
        for speed in speeds:
            send_wheel_speed(bus, speed, speed)
            time.sleep(1)
        
        # 階段 3: 保持高速
        print("\n[階段 3] 保持高速 50 km/h (5 秒)")
        for i in range(5):
            send_wheel_speed(bus, 50, 50)
            time.sleep(1)
        
        # 階段 4: 模擬減速
        print("\n[階段 4] 模擬減速 (50 → 0 km/h)")
        speeds = [50, 40, 30, 20, 10, 0]
        for speed in speeds:
            send_wheel_speed(bus, speed, speed)
            time.sleep(1)
        
        # 階段 5: 停止 VCU
        print("\n[階段 5] 停止 VCU (RTD 結束)")
        time.sleep(1)
        send_vcu_signal(bus, 0x00)  # STOPPED
        time.sleep(1)
        
        print("\n" + "=" * 60)
        print("✅ 測試數據發送完成！")
        print("=" * 60)
        
        # 等待，方便用戶查看
        print("\n按 Ctrl+C 退出...")
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️  用戶中斷")
    except Exception as e:
        print(f"\n❌ 錯誤: {e}")
    finally:
        bus.shutdown()
        print("已關閉 CAN 連接")

if __name__ == '__main__':
    main()
