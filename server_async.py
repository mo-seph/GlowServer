import asyncio
from contextlib import AsyncExitStack, asynccontextmanager
from random import randrange
from asyncio_mqtt import Client, MqttError
from concurrent.futures import ThreadPoolExecutor
import serial_asyncio
import json

command_channel="leds/commands"
state_channel="leds/state"



async def listen_for_mqtt(wr,port='/dev/cu.usbmodem54473601'):
    async with Client("glowserver.local") as client:
        print("Connected to MQTT")
        async with client.filtered_messages(command_channel) as messages:
            await client.subscribe(command_channel)
            print(f"Subscribed to LED Command Channel ({command_channel}) on MQTT")
            #_, writer = await serial_asyncio.open_serial_connection(url=port)
            async for message in messages:
                #await send(writer,message.payload)
                await send(wr,message.payload)

async def send(w, msg):
    print(f'MQTT->Serial: {msg}')
    w.write(msg)
    w.write(b"\n")
    await asyncio.sleep(0.005)

async def mqtt_listener():
    print("Listening for MQTT messages")
    # Run the advanced_example indefinitely. Reconnect automatically
    # if the connection is lost.
    reconnect_interval = 3  # [seconds]
    while True:
        try:
            await listen_for_mqtt()
        except MqttError as error:
            print(f'Error "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)

async def serial_listener(rd,wr,port='/dev/cu.usbmodem54473601'):
    print("Listening for serial messages")
    reconnect_interval = 0.3  # [seconds]
    while True:
        try:
            await listen_for_serial(rd,wr,port)
        except Exception as error:
            print(f'Error with serial: "{error}". Reconnecting in {reconnect_interval} seconds.')
        finally:
            await asyncio.sleep(reconnect_interval)

async def listen_for_serial(rd,writer,port='/dev/cu.usbmodem54473601'):
    #reader, writer = await serial_asyncio.open_serial_connection(url=port)
    print("Got serial connection")
    #writer.write(b'{"state":1}')
    async with Client("glowserver.local") as client:
        print("Connected MQTT sending from serial")
        writer.write(b'{"state":1}\n')
        while True:
            #msg = await reader.readuntil(b'\n')
            msg = await rd.readline()
            msg = msg.rstrip()
            try:
                md = json.loads(msg)
                print(f'Serial->MQTT [{state_channel}]: {msg}')
                await client.publish(state_channel,msg)
            except json.JSONDecodeError as j:
                print(f'> {msg}')



async def main(port='/dev/cu.usbmodem54473601'):
    reader, writer = await serial_asyncio.open_serial_connection(url=port)
    #boo = asyncio.create_task(mqtt_listener() )
    await asyncio.wait([serial_listener(reader,writer,port=port),listen_for_mqtt(writer)])

import sys
port = '/dev/cu.usbmodem54473601'
if len(sys.argv) > 1:
    port = sys.argv[1]
asyncio.run(main(port))
