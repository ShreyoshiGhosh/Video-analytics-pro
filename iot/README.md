# IoT Hardware Integration (Optional Setup)

This directory contains the firmware and python integration scripts to interface the **Video Analytics Pro** system with real-world IoT sensors.

---

## 🔌 Hardware Configuration

- **Microcontroller**: NodeMCU (ESP8266)
- **Sensor**: MQ-135 Gas / Air Quality / Smoke Sensor
- **Connection**:
  - `MQ-135 VCC` ➔ `NodeMCU 3V3` (or `Vin` if 5V is required)
  - `MQ-135 GND` ➔ `NodeMCU GND`
  - `MQ-135 A0` (Analog Out) ➔ `NodeMCU A0` (Analog Input Pin)

---

## 📂 File Breakdown

1. **`nodemcu_smoke_sensor/nodemcu_smoke_sensor.ino`**:
   The Arduino code to compile and upload to your NodeMCU using the Arduino IDE. It connects to Wi-Fi and reads analog signals from the MQ-135 sensor, outputting `"SMOKE"` or `"CLEAR"` to the Serial port.
   
2. **`serial_monitor.py`**:
   The Python script that runs concurrently or is imported in the backend to read NodeMCU's Serial outputs over USB (e.g. `COM3`) and dynamically update the global application state.

---

## ⚙️ How to Switch from Simulation to Real IoT Hardware

To use this physical setup instead of the default simulated background thread:

1. Connect your NodeMCU to your computer via USB.
2. In the Arduino IDE, verify that the serial port (e.g., `COM3`) matches the port specified in `serial_monitor.py`.
3. In `backend/sensor_manager.py` (or where the background sensor daemon is launched), replace the simulation thread logic with the thread inside `iot/serial_monitor.py`.
4. Run `pip install pyserial` in your python environment.
