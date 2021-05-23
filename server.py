import paho.mqtt.client as mqtt

'''
MQTT support seems a bit fiddly -needs websockets.

This seems to happen by
- enabling websocket support on mosquitto by adding these lines to
/opt/local/etc/mosquitto/mosquitto.conf:
`
listener 9001
protocol websockets

listener 1883
protocol mqtt
`
- on the browser side, use the MQTT library: https://github.com/mqttjs/MQTT.js/#browser
'''


# https://pyserial.readthedocs.io/en/latest/shortintro.html
import serial


# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("leds")

# The callback function for received message
def mk_serial(port="/dev/cu.usbmodem54473601"):
    ser = serial.Serial(port)
    def on_message(client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        ser.write(msg.payload)
    return on_message


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = mk_serial("/dev/cu.usbmodem54473601")
client.connect("localhost", 1883, 60)
#client.connect("localhost", 9001, 60)
client.loop_forever()
