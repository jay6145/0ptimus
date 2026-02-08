import argparse, re, time, json
import serial
import requests

RE = re.compile(r"Humidity:\s*([\d.]+)%\s*Temperature:\s*([\d.]+)°C\s*([\d.]+)°F")

def post(api_url, store_id, sensor, value, unit=None):
    payload = {"store_id": store_id, "sensor": sensor, "value": float(value)}
    if unit: payload["unit"] = unit
    requests.post(api_url, json=payload, timeout=3)  # JSON POST pattern [web:292]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default="/dev/cu.usbmodem101")
    ap.add_argument("--baud", type=int, default=9600)
    ap.add_argument("--store-id", type=int, default=1)
    ap.add_argument("--api", default="http://localhost:8000/api/telemetry")
    args = ap.parse_args()

    ser = serial.Serial(args.port, args.baud, timeout=2)  # typical pySerial usage [web:287]
    time.sleep(2)  # let Arduino reset

    while True:
        line = ser.readline().decode(errors="ignore").strip()  # read line loop [web:287]
        if not line:
            continue

        # If you later switch Arduino to JSON output, this will just work:
        if line.startswith("{") and line.endswith("}"):
            obj = json.loads(line)
            post(args.api, obj.get("store_id", args.store_id), obj["sensor"], obj["value"], obj.get("unit"))
            continue

        m = RE.search(line)
        if not m:
            continue

        humidity, temp_c, temp_f = m.groups()
        post(args.api, args.store_id, "cooler_humidity_pct", humidity, "pct")
        post(args.api, args.store_id, "cooler_temp_c", temp_c, "celsius")
        post(args.api, args.store_id, "cooler_temp_f", temp_f, "fahrenheit")

if __name__ == "__main__":
    main()
