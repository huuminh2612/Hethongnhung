import time
import ubinascii
import machine
from umqtt.simple import MQTTClient
import dht
import network
from machine import Pin
import BlynkLib

SSID = "Shin"
SSID_PASSWORD = "26122002"

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSID_PASSWORD)
        while not sta_if.isconnected():
            print("Attempting to connect....")
            time.sleep(1)
    print('Connected! Network config:', sta_if.ifconfig())

print("Connecting to your wifi...")
do_connect()

auth = "cXW-Q4knUJJHsdFFgbQr-vDJjKXuE5Q2"
blynk = BlynkLib.Blynk(auth)

SERVER = "mqtt-dashboard.com"
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC_TEMP = b"temperature"
TOPIC_HUMID = b"humidity"
TOPIC_GAS = b"gas"

sensor = dht.DHT11(Pin(4))
mq2 = machine.ADC(machine.Pin(34))
relay1 = Pin(12, Pin.OUT)
coi1 = Pin(14, Pin.OUT)
led = Pin(13, Pin.OUT)

@blynk.on("V0")
def v0_h(value):
    if int(value[0]) == 1:
        led.on()
        print('Bật đèn')
    else:
        led.off()
        print('Tắt đèn')

manual_control = 0

@blynk.on("V1")
def v1_h(value):
    global manual_control
    manual_control = int(value[0])
    if manual_control == 1:
        relay1.on()
        print('Bật Relay')
    else:
        relay1.off()
        print('Tắt Relay')

def reset():
    print("Resetting...")
    time.sleep(5)
    machine.reset()

def read_dht():
    sensor.measure()
    temperature = sensor.temperature()
    humidity = sensor.humidity()
    blynk.virtual_write(5, humidity)
    blynk.virtual_write(6, temperature)
    return temperature, humidity

def read_gas():
    gas_value = mq2.read()
    blynk.virtual_write(2, gas_value)
    if manual_control == 0:
        if gas_value > 4000:
            relay1.on()
            coi1.on()
        else:
            relay1.off()
            coi1.off()
    return gas_value

def main():
    mqttClient = MQTTClient(CLIENT_ID, SERVER, keepalive=60)
    mqttClient.connect()
    print(f"Connected to MQTT Broker :: {SERVER}")
    while True:
        temperature, humidity = read_dht()
        gas_value = read_gas()
        print(f"Publishing temperature: {temperature}°C")
        mqttClient.publish(TOPIC_TEMP, str(temperature).encode())
        time.sleep(1)
        print(f"Publishing humidity: {humidity}%")
        mqttClient.publish(TOPIC_HUMID, str(humidity).encode())
        time.sleep(1)
        print(f"Publishing gas value: {gas_value}")
        mqttClient.publish(TOPIC_GAS, str(gas_value).encode())
        time.sleep(3)
        blynk.run()

if __name__ == "__main__":
    try:
        main()
    except OSError as e:
        print("Error: " + str(e))
        reset()