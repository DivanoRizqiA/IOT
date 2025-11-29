import json
import threading
import paho.mqtt.client as mqtt

MQTT_HOST = "ade2fe102fc3463e823867c330ef9dfd.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_USER = "aldopratama123"
MQTT_PASS = "Aldopratama123!@#"
MQTT_TOPIC = "aldo/fitness"

latest_data = {
    "steps": 0,
    "hr": 0,
    "calories": 0.0,
    "ax": 0,
    "ay": 0,
    "az": 0
}

def on_connect(client, userdata, flags, rc):
    print("Connected RC:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global latest_data
    try:
        payload = json.loads(msg.payload.decode())
        latest_data.update(payload)
    except:
        pass

def mqtt_thread():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.tls_set()

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_HOST, MQTT_PORT, 60)
    client.loop_forever()

def start_mqtt():
    thread = threading.Thread(target=mqtt_thread)
    thread.daemon = True
    thread.start()
