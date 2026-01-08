import can
import csv
import os
import time
from datetime import datetime, timedelta

import subprocess
lego = 10
vcu_instruction = False
vcu_state = 0x00  # 追蹤 VCU state
rtd_active = False  # 追蹤 RTD 狀態
trip_distance = 0.0  # 本次行程里程
wheel_speed_data = []  # 收集輪速數據用於里程計算

def check_vcu_running():
    return vcu_instruction

def get_vcu_state():
    """獲取當前 VCU state"""
    return vcu_state

def calculate_wheel_speed(byte4, byte5):
    """
    根據 byte4 和 byte5 計算輪速 (km/h)
    輪速編碼方式：(byte5 << 8 | byte4) * 0.01 km/h
    """
    speed_raw = (byte5 << 8) | byte4
    speed_kmh = speed_raw * 0.01
    return speed_kmh

def estimate_distance_from_speeds(current_speed_kmh, previous_speed_kmh, time_delta_s):
    """
    使用梯形積分計算距離
    梯形積分公式：距離 = (當前速度 + 上一速度) / 2 * 時間差
    
    Args:
        current_speed_kmh: 當前輪速 (km/h)
        previous_speed_kmh: 上一次輪速 (km/h)
        time_delta_s: 時間差 (秒)
    
    Returns:
        距離 (km)
    """
    # 梯形積分：(v1 + v2) / 2 * t
    average_speed = (current_speed_kmh + previous_speed_kmh) / 2
    distance_km = (average_speed / 3600) * time_delta_s
    return distance_km

def read_cumulative_distance(base_dir):
    """
    讀取累計里程
    """
    cumulative_file = os.path.join(base_dir, "trip_distance_cumulative.csv")
    cumulative_distance = 0.0
    
    if os.path.exists(cumulative_file):
        try:
            with open(cumulative_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                lines = list(reader)
                # 找到 "Cumulative Distance (km)" 那行
                for line in lines:
                    if len(line) >= 2 and line[0] == "Cumulative Distance (km)":
                        cumulative_distance = float(line[1])
                        break
        except Exception as e:
            print(f"Failed to read cumulative distance: {e}")
    
    return cumulative_distance

def write_trip_log(base_dir, new_distance_km, cumulative_distance_km, duration_s, start_time, end_time, wheel_speed_events):
    """
    將里程數據寫入 log 文件（單一累計文件）
    
    Args:
        base_dir: 日誌目錄
        new_distance_km: 本次行程距離（km）
        cumulative_distance_km: 累計總里程（km）
        duration_s: 行程時長（秒）
        start_time: 開始時間
        end_time: 結束時間
        wheel_speed_events: 輪速事件列表
    """
    cumulative_file = os.path.join(base_dir, "trip_distance_cumulative.csv")
    
    try:
        with open(cumulative_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Trip Distance Cumulative Log"])
            writer.writerow(["Last Updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
            writer.writerow([])
            writer.writerow(["Cumulative Distance (km)", f"{cumulative_distance_km:.6f}"])
            writer.writerow(["Cumulative Distance (m)", f"{cumulative_distance_km * 1000:.2f}"])
            writer.writerow([])
            writer.writerow(["Latest Trip Information"])
            writer.writerow(["Trip Start Time", start_time.strftime("%Y-%m-%d %H:%M:%S.%f")])
            writer.writerow(["Trip End Time", end_time.strftime("%Y-%m-%d %H:%M:%S.%f")])
            writer.writerow(["Trip Distance (km)", f"{new_distance_km:.6f}"])
            writer.writerow(["Trip Distance (m)", f"{new_distance_km * 1000:.2f}"])
            writer.writerow(["Trip Duration (seconds)", f"{duration_s:.2f}"])
            
            # 計算平均速度
            if duration_s > 0:
                avg_speed_kmh = (new_distance_km / duration_s) * 3600
                writer.writerow(["Trip Average Speed (km/h)", f"{avg_speed_kmh:.2f}"])
            
            writer.writerow([])
            writer.writerow(["Wheel Speed Events Sample (前100筆)"])
            writer.writerow(["Left Wheel Speed (km/h)", "Right Wheel Speed (km/h)", "Time (s from start)"])
            
            for i, (left_speed, right_speed, time_offset) in enumerate(wheel_speed_events[:100]):
                writer.writerow([f"{left_speed:.2f}", f"{right_speed:.2f}", f"{time_offset:.3f}"])
        
        print(f"Trip log updated: {cumulative_distance_km:.6f}km total")
        return True
    except Exception as e:
        print(f"Failed to write trip log: {e}")
        return False

def start_can_interface():
    try:
        subprocess.run(
            ["sudo", "ip", "link", "set", "can0", "up", "type", "can", "bitrate", "1000000"],
            check=True
        )
        print("CAN0 interface started.")
    except subprocess.CalledProcessError:
        print("Failed to start CAN0 interface.")
    
    try:
        subprocess.run(
            ["sudo", "ip", "link", "set", "can1", "up", "type", "can", "bitrate", "1000000"],
            check=True
        )
        print("CAN1 interface started.")
    except subprocess.CalledProcessError:
        print("Failed to start CAN1 interface.")

def connect_can(bus_channel='can0'):
    while True:
        try:
            return can.interface.Bus(channel=bus_channel, bustype='socketcan')
        except OSError:
            print("CAN not available, retrying in 5 sec...")
            time.sleep(5)

def new_csv_writer(base_dir, base_name):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(base_dir, f"{base_name}_{timestamp}.csv")
    f = open(filename, 'w', newline='')
    writer = csv.writer(f)
    writer.writerow(["Time Stamp", "ID", "Extended", "Dir", "Bus", "LEN", "D1",
                     "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10",
                     "D11", "D12"])
    return f, writer

def main():
    global vcu_instruction, vcu_state, rtd_active, trip_distance
    
    base_dir = "/home/pi/Desktop/RPI_Desktop/LOGS"
    os.makedirs(base_dir, exist_ok=True)

    bus0 = connect_can('can0')
    bus1 = connect_can('can1')
    
    # 讀取上次的累計里程
    cumulative_distance_km = read_cumulative_distance(base_dir)
    print(f"Cumulative distance from previous records: {cumulative_distance_km:.6f}km")
    
    recording = False
    recording_start_time = datetime.now()
    file, writer = new_csv_writer(base_dir, "can_log")
    rotate_at = recording_start_time + timedelta(minutes=20)
    last_status_send = 0
    
    print("CAN Logger started for CAN0 and CAN1 and wait for recording!")
    print("Wait for VCU running!")
    print("You can still use control commands (0x420: 01=start, 02=stop)...")

    vcu_last = check_vcu_running()
    rtd_start_time = None
    trip_distance_km = 0.0
    last_left_wheel_speed = 0.0
    last_right_wheel_speed = 0.0
    last_wheel_speed_time = None
    wheel_speed_events = []  # 記錄 (左輪速, 右輪速, 時間偏移)
    
    while True:
        # 從兩個 CAN bus 接收訊息
        msg0 = bus0.recv(timeout=0.001)  # 使用較短的 timeout
        msg1 = bus1.recv(timeout=0.001)
        
        # 檢查 VCU 指令和狀態 (從 can0)
        if msg0 is not None and hasattr(msg0, 'arbitration_id') and msg0.arbitration_id == 0x281 and len(msg0.data) > 1:
            vcu_instruction = msg0.data[0] & 0x20
            global vcu_state
            vcu_state = msg0.data[0]  # 完整的 VCU state
            
            # 檢查 RTD 狀態變化（VCU state = 0x20 表示 RUNNING）
            is_running_now = (msg0.data[0] == 0x20)
            
            # RTD 開始：state 變為 0x20
            if is_running_now and not rtd_active:
                print("[RTD START] VCU state changed to RUNNING (0x20)")
                rtd_active = True
                rtd_start_time = datetime.now()
                trip_distance_km = 0.0
                last_left_wheel_speed = 0.0
                last_right_wheel_speed = 0.0
                last_wheel_speed_time = datetime.now()
                wheel_speed_events = []
            
            # RTD 結束：state 從 0x20 變為其他
            elif not is_running_now and rtd_active:
                print("[RTD END] VCU state changed from RUNNING, saving trip log...")
                rtd_active = False
                rtd_end_time = datetime.now()
                
                # 計算行程時長
                duration_s = (rtd_end_time - rtd_start_time).total_seconds() if rtd_start_time else 0
                
                # 累加到總里程
                cumulative_distance_km += trip_distance_km
                
                # 寫入 log 檔案（會覆蓋之前的內容）
                if rtd_start_time:
                    write_trip_log(base_dir, trip_distance_km, cumulative_distance_km, duration_s, rtd_start_time, rtd_end_time, 
                                 wheel_speed_events)
                
                print(f"Trip Summary: Distance={trip_distance_km:.6f}km, Cumulative={cumulative_distance_km:.6f}km, Duration={duration_s:.2f}s")
                
                # 重置資料
                trip_distance_km = 0.0
                last_left_wheel_speed = 0.0
                last_right_wheel_speed = 0.0
                last_wheel_speed_time = None
                wheel_speed_events = []
        
        # 也檢查 can1 的 VCU 指令
        if msg1 is not None and hasattr(msg1, 'arbitration_id') and msg1.arbitration_id == 0x281 and len(msg1.data) > 1:
            vcu_instruction = msg1.data[0] & 0x20
            vcu_state = msg1.data[0]
            
            # 檢查 RTD 狀態變化
            is_running_now = (msg1.data[0] == 0x20)
            
            if is_running_now and not rtd_active:
                print("[RTD START] VCU state changed to RUNNING (0x20)")
                rtd_active = True
                rtd_start_time = datetime.now()
                trip_distance_km = 0.0
                last_left_wheel_speed = 0.0
                last_right_wheel_speed = 0.0
                last_wheel_speed_time = datetime.now()
                wheel_speed_events = []
            
            elif not is_running_now and rtd_active:
                print("[RTD END] VCU state changed from RUNNING, saving trip log...")
                rtd_active = False
                rtd_end_time = datetime.now()
                
                duration_s = (rtd_end_time - rtd_start_time).total_seconds() if rtd_start_time else 0
                
                cumulative_distance_km += trip_distance_km
                
                if rtd_start_time:
                    write_trip_log(base_dir, trip_distance_km, cumulative_distance_km, duration_s, rtd_start_time, rtd_end_time, 
                                 wheel_speed_events)
                
                print(f"Trip Summary: Distance={trip_distance_km:.6f}km, Cumulative={cumulative_distance_km:.6f}km, Duration={duration_s:.2f}s")
                
                trip_distance_km = 0.0
                last_left_wheel_speed = 0.0
                last_right_wheel_speed = 0.0
                last_wheel_speed_time = None
                wheel_speed_events = []
        
        # 當 RTD 活躍時，收集輪速數據並計算里程
        if rtd_active:
            current_time = datetime.now()
            current_left_speed = None
            current_right_speed = None
            
            # 收集左後輪速 (0x193, byte 4-5)
            if msg0 is not None and hasattr(msg0, 'arbitration_id') and msg0.arbitration_id == 0x193 and len(msg0.data) >= 5:
                current_left_speed = calculate_wheel_speed(msg0.data[4], msg0.data[5] if len(msg0.data) > 5 else 0)
            
            if msg1 is not None and hasattr(msg1, 'arbitration_id') and msg1.arbitration_id == 0x193 and len(msg1.data) >= 5:
                current_left_speed = calculate_wheel_speed(msg1.data[4], msg1.data[5] if len(msg1.data) > 5 else 0)
            
            # 收集右後輪速 (0x194, byte 4-5)
            if msg0 is not None and hasattr(msg0, 'arbitration_id') and msg0.arbitration_id == 0x194 and len(msg0.data) >= 5:
                current_right_speed = calculate_wheel_speed(msg0.data[4], msg0.data[5] if len(msg0.data) > 5 else 0)
            
            if msg1 is not None and hasattr(msg1, 'arbitration_id') and msg1.arbitration_id == 0x194 and len(msg1.data) >= 5:
                current_right_speed = calculate_wheel_speed(msg1.data[4], msg1.data[5] if len(msg1.data) > 5 else 0)
            
            # 使用梯形積分計算里程
            if current_left_speed is not None and current_right_speed is not None:
                if last_wheel_speed_time is not None:
                    time_delta = (current_time - last_wheel_speed_time).total_seconds()
                    
                    if time_delta > 0:  # 避免除以零
                        # 左輪里程
                        left_distance = estimate_distance_from_speeds(current_left_speed, last_left_wheel_speed, time_delta)
                        # 右輪里程
                        right_distance = estimate_distance_from_speeds(current_right_speed, last_right_wheel_speed, time_delta)
                        # 平均里程
                        avg_distance = (left_distance + right_distance) / 2
                        trip_distance_km += avg_distance
                
                # 記錄事件
                time_offset = (current_time - rtd_start_time).total_seconds()
                wheel_speed_events.append((current_left_speed, current_right_speed, time_offset))
                
                # 更新上一次速度
                last_left_wheel_speed = current_left_speed
                last_right_wheel_speed = current_right_speed
                last_wheel_speed_time = current_time

        vcu_running = check_vcu_running()
        # VCU 狀態 edge: False -> True，強制新開檔記錄
        if vcu_running and not vcu_last:
            print("VCU狀態由False變True，強制新開檔記錄！")
            if file:
                file.close()
            recording_start_time = datetime.now()
            file, writer = new_csv_writer(base_dir, "can_log_vcu")
            rotate_at = recording_start_time + timedelta(minutes=20)
            recording = True
            print(f"Recording started at {recording_start_time}")
        # VCU 狀態 edge: True -> False，自動關閉記錄
        elif not vcu_running and vcu_last:
            print("VCU狀態由True變False，自動關閉記錄！")
            if recording and file:
                file.close()
                file = None
                writer = None
            recording = False
            recording_start_time = None
            print(f"Recording stopped at {datetime.now()}")
            print("Waiting for VCU or manual start...")
        vcu_last = vcu_running

        # VCU True: 只能自動記錄，不能被0x420打斷
        if vcu_running:
            if not recording:
                print("VCU running, auto start recording!")
                recording_start_time = datetime.now()
                file, writer = new_csv_writer(base_dir, "can_log")
                rotate_at = recording_start_time + timedelta(minutes=20)
                recording = True
                print(f"Recording started at {recording_start_time}")
        else:
            # VCU False: 0x420可控制記錄 (檢查兩個 CAN bus)
            for msg in [msg0, msg1]:
                if msg is not None and hasattr(msg, 'arbitration_id') and msg.arbitration_id == 0x420:
                    data_bytes = list(msg.data)
                    if len(data_bytes) > 0:
                        first_byte = data_bytes[0]
                        if first_byte == 0x01:
                            if not recording:
                                print("Start recording command received!")
                                recording_start_time = datetime.now()
                                file, writer = new_csv_writer(base_dir, "can_log")
                                rotate_at = recording_start_time + timedelta(minutes=20)
                                recording = True
                                print(f"Recording started at {recording_start_time}")
                            else:
                                print("Already recording, ignoring start command")
                        elif first_byte == 0x02:
                            if recording:
                                print("Stop recording command received!")
                                if file:
                                    file.close()
                                    file = None
                                    writer = None
                                recording = False
                                recording_start_time = None
                                print(f"Recording stopped at {datetime.now()}")
                                print("Waiting for next start command...")
                            else:
                                print("Not recording, ignoring stop command")
                    break  # 只處理一次控制指令

        try:
            # 2. 保留原本的 CAN 指令控制（已在主邏輯處理，這裡只處理寫檔與狀態訊息）
            current_time = time.time()
            if current_time - last_status_send >= 1.0:
                try:
                    if recording and recording_start_time:
                        timestamp = int(recording_start_time.timestamp())
                        data = [0x01]
                        data.extend([
                            (timestamp >> 0) & 0xFF,
                            (timestamp >> 8) & 0xFF,
                            (timestamp >> 16) & 0xFF,
                            (timestamp >> 24) & 0xFF,
                            0x00, 0x00, 0x00
                        ])
                        status_msg = can.Message(arbitration_id=0x421, data=data, is_extended_id=False)
                        bus0.send(status_msg)  # 從 can0 發送狀態
                    else:
                        data = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
                        status_msg = can.Message(arbitration_id=0x421, data=data, is_extended_id=False)
                        bus0.send(status_msg)  # 從 can0 發送狀態
                    last_status_send = current_time
                except Exception as e:
                    print(f"Failed to send status message: {e}")

            # 記錄 can0 的訊息
            if recording and writer and msg0 is not None and hasattr(msg0, 'arbitration_id'):
                timestamp = int(time.time() * 1000000)
                can_id = f"{msg0.arbitration_id:08X}"
                extended = 'true' if msg0.is_extended_id else 'false'
                direction = 'Rx' if not msg0.is_remote_frame else 'Tx'
                bus_num = 0  # can0
                dlc = msg0.dlc
                data_bytes = [f"{byte:02X}" for byte in msg0.data]
                data_bytes += ['00'] * (8 - len(data_bytes))
                writer.writerow([timestamp, can_id, extended, direction, bus_num, dlc] + data_bytes)

            # 記錄 can1 的訊息
            if recording and writer and msg1 is not None and hasattr(msg1, 'arbitration_id'):
                timestamp = int(time.time() * 1000000)
                can_id = f"{msg1.arbitration_id:08X}"
                extended = 'true' if msg1.is_extended_id else 'false'
                direction = 'Rx' if not msg1.is_remote_frame else 'Tx'
                bus_num = 1  # can1
                dlc = msg1.dlc
                data_bytes = [f"{byte:02X}" for byte in msg1.data]
                data_bytes += ['00'] * (8 - len(data_bytes))
                writer.writerow([timestamp, can_id, extended, direction, bus_num, dlc] + data_bytes)

            # 檢查是否需要輪換日誌檔案
            if recording and writer and datetime.now() >= rotate_at:
                print("Rotating log file...")
                file.close()
                recording_start_time = datetime.now()
                file, writer = new_csv_writer(base_dir, "can_log")
                rotate_at = recording_start_time + timedelta(minutes=20)
                print(f"New log file created at {recording_start_time}")

        except can.CanError as e:
            print(f"CAN Error: {e}")
            if recording and file:
                file.close()
                file = None
                writer = None
                recording = False
                recording_start_time = None
            # 重新連接兩個 CAN bus
            try:
                bus0 = connect_can('can0')
                print("CAN0 connection restored")
            except:
                print("Failed to restore CAN0")
            try:
                bus1 = connect_can('can1')
                print("CAN1 connection restored")
            except:
                print("Failed to restore CAN1")
        except Exception as e:
            print(f"Unexpected error: {e}")
            if recording and file:
                file.close()
                file = None
                writer = None
                recording = False
                recording_start_time = None

if __name__ == "__main__":
    try: 
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"Program error: {e}")
        with open("/tmp/can_logger_error.log", "w") as f:
            f.write(f"Error at {datetime.now()}: {str(e)}")
    finally:
        print("CAN Logger stopped")


