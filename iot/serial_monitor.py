import serial
import threading
import time
from backend.shared_state import SmokeStatus  # Import the shared state singleton

def read_sensor(port='COM3', baudrate=115200):
    try:
        ser = serial.Serial(port, baudrate, timeout=2)  # Match this with your NodeMCU baud rate
        print(f"[Serial Monitor] Serial port {port} opened. Listening...")
    except Exception as e:
        print(f"[Serial Monitor] Failed to open serial port: {e}")
        return

    previous_status = None  # For change detection

    while True:
        try:
            line = ser.readline().decode(errors='ignore').strip()
            if not line:
                continue

            print(f"[Serial Monitor] Received: {line}")

            if "SMOKE" in line.upper():
                SmokeStatus.smoke_detected = True
            elif "CLEAR" in line.upper():
                SmokeStatus.smoke_detected = False

            # Only print when status changes
            if SmokeStatus.smoke_detected != previous_status:
                print(f"[Serial Monitor] Smoke Detected: {SmokeStatus.smoke_detected}")
                previous_status = SmokeStatus.smoke_detected

            time.sleep(0.1)

        except Exception as e:
            print(f"[Serial Monitor] Error reading serial: {e}")
            time.sleep(1)

def start_monitor_thread():
    sensor_thread = threading.Thread(target=read_sensor, daemon=True)
    sensor_thread.start()
    print("[Serial Monitor] Background thread started.")

if __name__ == '__main__':
    # Run standalone to test connection
    read_sensor()
