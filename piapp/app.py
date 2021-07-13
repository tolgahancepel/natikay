'''
    File name: app.py
    Author: Tolgahan Cepel (tolgahan.cepel@gmail.com)
    Date created: 21/03/2021
    Date last modified: 14/07/2021
    Python Version: 3.8.5
'''

import RPi.GPIO as GPIO
import Adafruit_DHT
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import paho.mqtt.client as mqtt
import busio
import board
import pymongo
import time

GPIO.setmode(GPIO.BCM)

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  MQTT_TOPIC = [("topic/natikay",0)]
  client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    #print(msg.payload.decode())

    if(msg.payload.decode() == "l0"):
      switch_off(light_channel)
    
    elif(msg.payload.decode() == "l1"):
        switch_on(light_channel)
    
    if(msg.payload.decode() == "i0"):
      switch_off(water_pump_channel)
    
    elif(msg.payload.decode() == "i1"):
        switch_on(water_pump_channel)

    # client.disconnect()
    
client = mqtt.Client()
client.connect("mqtt.eclipseprojects.io", 1883, 60)

client.on_connect = on_connect
client.on_message = on_message


# -------------------------------------------------------------------------------
# MongoDB Atlas Configuration
# -------------------------------------------------------------------------------

mongo_client = pymongo.MongoClient("mongodb+srv://heroku_user:TravelMate5742@natikay.gnzmn.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
natikay_db = mongo_client['natikay-database']
sensor_history = natikay_db["sensor_history"]

# -------------------------------------------------------------------------------
# DHT11 Sensor Values
# -------------------------------------------------------------------------------

dht11_sensor=Adafruit_DHT.DHT11
gpio=26

# -------------------------------------------------------------------------------
# Soil Moisure Sensors
# -------------------------------------------------------------------------------

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan1 = AnalogIn(ads, ADS.P0)
chan2 = AnalogIn(ads, ADS.P1)
chan3 = AnalogIn(ads, ADS.P2)
chan4 = AnalogIn(ads, ADS.P3)

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def chan_to_percent(chn):
    somo = chn.voltage - 1.13
    somo = somo * 33.78
    somo = int(100 - somo)
    somo = clamp(somo, 0, 100)

    return somo

# ---------------------------------------------------------------------------
# Ultrasonic Distance Sensor
# ---------------------------------------------------------------------------

#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)


def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance



# -------------------------------------------------------------------------------
# Light Control
# -------------------------------------------------------------------------------

light_channel = 20


GPIO.setup(light_channel, GPIO.OUT)
GPIO.output(light_channel, GPIO.LOW)

def switch_on(pin):
      GPIO.output(pin, GPIO.LOW)

def switch_off(pin):
      GPIO.output(pin, GPIO.HIGH)


# -------------------------------------------------------------------------------
# Water Pump Control
# -------------------------------------------------------------------------------

water_pump_channel = 21

GPIO.setmode(GPIO.BCM)
GPIO.setup(water_pump_channel, GPIO.OUT)
GPIO.output(water_pump_channel, GPIO.LOW)


if __name__ == "__main__":

  switch_off(light_channel)
  switch_off(water_pump_channel)

  sensor_history.drop()
  counter = 0

  while(True):
      client.loop_start()
      client.publish("topic/natikay", ("l" + str(int(not GPIO.input(light_channel)))))

      somo1 = chan_to_percent(chan1)
      somo2 = chan_to_percent(chan2)
      somo3 = chan_to_percent(chan3)
      somo4 = chan_to_percent(chan4)

      # Water level calculation 4.0  - 11.0
      wlevel = distance() - 4
      wlevel = wlevel * 14.28
      wlevel = int(100 - wlevel)
      wlevel = clamp(wlevel, 0, 100)

      counter += 1

      if(counter > 100):
        sensor_history.delete_one(sensor_history.find_one())
        counter=1800

      humidity, temperature = Adafruit_DHT.read_retry(dht11_sensor, gpio)

      post = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": time.time(),
        "somo1": somo1,
        "somo2": somo2,
        "somo3": somo3,
        "somo4": somo4,
        "wlevel": wlevel

      }
      natikay_db["sensor_history"].insert_one(post).inserted_id

      # print("Temperature: ", temperature)
      # print("Humidity: \n", humidity)
      # print(wlevel)
      time.sleep(1)