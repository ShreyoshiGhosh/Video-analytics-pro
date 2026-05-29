import threading
import time
from .shared_state import SmokeStatus

def simulate_smoke_sensor():
    while True:
        SmokeStatus.is_smoke_detected = not SmokeStatus.is_smoke_detected
        state = "!!! SMOKE !!!" if SmokeStatus.is_smoke_detected else "No Smoke"
        print(f"[IOT SIMULATOR] {state}")
        time.sleep(30)

def start_sensor_thread():
    thread = threading.Thread(target = simulate_smoke_sensor, daemon = True)
    thread.start()
