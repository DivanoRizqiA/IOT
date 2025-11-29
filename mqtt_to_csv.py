import paho.mqtt.client as mqtt
import json
import pandas as pd
import time
import ssl
from datetime import datetime
import threading

MQTT_HOST = "ade2fe102fc3463e823867c330ef9dfd.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "aldopratama123"
MQTT_PASS = "Aldopratama123!@#"
MQTT_TOPIC = "aldo/fitness"

# ------- STATE -------
CSV_FILE = None
stop_written = False
last_message_time = time.time()
STOP_TIMEOUT = 5  # detik

# ------- BUAT FILE BARU -------
def create_new_csv():
    global CSV_FILE
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    CSV_FILE = f"fitness_log_{timestamp}.csv"

    df = pd.DataFrame(columns=["timestamp", "steps", "hr", "calories", "ax", "ay", "az"])
    df.to_csv(CSV_FILE, index=False)

    print(f"\n📁 FILE BARU: {CSV_FILE}\n")

create_new_csv()

# ------- TULIS STOP -------
def write_stop_flag():
    global stop_written
    if stop_written:
        return

    stop_row = pd.DataFrame([{
        "timestamp": time.time(),
        "steps": "STOP",
        "hr": "",
        "calories": "",
        "ax": "",
        "ay": "",
        "az": ""
    }])

    stop_row.to_csv(CSV_FILE, mode="a", index=False, header=False)
    stop_written = True

    print("🚫 STOP terdeteksi — STOP ditulis ke CSV")

# ------- MONITOR MQTT STOP -------
def monitor_stop():
    global last_message_time
    while True:
        if time.time() - last_message_time > STOP_TIMEOUT:
            write_stop_flag()
        time.sleep(1)

threading.Thread(target=monitor_stop, daemon=True).start()

# ------- MQTT CALLBACK -------
def on_message(client, userdata, msg):
    global last_message_time, stop_written, CSV_FILE

    last_message_time = time.time()

    # Jika sebelumnya STOP → sekarang START lagi → buat file baru
    if stop_written:
        print("▶️ START baru terdeteksi — membuat file baru…")
        stop_written = False
        create_new_csv()

    payload = msg.payload.decode()
    data = json.loads(payload)

    row = {
        "timestamp": time.time(),
        "steps": data.get("steps", 0),
        "hr": data.get("hr", 0),
        "calories": data.get("calories", 0),
        "ax": data.get("ax", 0),
        "ay": data.get("ay", 0),
        "az": data.get("az", 0),
    }

    df = pd.DataFrame([row])
    df.to_csv(CSV_FILE, mode="a", index=False, header=False)

    print("Data masuk:", row)

# ------- MQTT SETUP -------
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)

client.on_message = on_message
client.connect(MQTT_HOST, MQTT_PORT, 60)
client.subscribe(MQTT_TOPIC)

print("Terhubung ke HiveMQ… menunggu data...")
client.loop_forever()
