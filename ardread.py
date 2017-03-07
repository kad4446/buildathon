import serial
import pygame
from time import *
import requests
import json

def manual():
	pass

port = "/dev/cu.usbmodem1411"
ser = serial.Serial(port, 115200, timeout=5)
sleep(1)

counter = 0

temp_threshold = 1.0 #will change later
values = ["a", 0, 0, 0, 0, 0.0, 0.0] # values [home, win_open, door_open, light_on, temp, humidity]
flag_something_changed = False
while True:

	if counter%1000 == 0:
		# Be sure URL is in JSON, api key will change per user
		api_key = '745ba33d1bf59284f45453e6030d89c9'
		url = 'http://api.openweathermap.org/data/2.5/weather?q=Austin,us&mode=json&appid=' + api_key
		# possible bug where values don't exist
		r = requests.get(url).json()
		sky_status = r["weather"][0]["main"] #clear or rainy etc
		cur_temp = r["main"]["temp"]
		cur_hum = r["main"]["humidity"]

	data = ser.readline().split(" ")
	data = data[:-1]

	# weird bug where first 4 data points are stupid
	counter += 1
	if counter > 10:

		#House logic using variables below
		if len(data) == 0:
			continue
		data_dict = {"home": bool(int(data[0])),
				"win_open": bool(int(data[1])),
				"door_open": bool(int(data[2])),
				"light_on": bool(int(data[3])),
				"temp": float(data[4]),
				"humidity": float(data[5]),
				"auto": bool(1),
				"energy_saver": bool(0)
				}

		ret = {"buffer": "a",
				"home": "0",
				"win_open": "0",
				"door_open": "0",
				"light_on": "1",
				"temp": "0",
				"humidity": "0"
				}

		# number = "a00000"
		# the first value MUST be an "a"
		while not data_dict["home"]:
			
			if sky_status == "Clear":
				flag_something_changed = True
				ret["win_open"] = "1"
				ret["door_open"] = "1"
			else:
				flag_something_changed = True
				ret["door_open"] = "1"

			if flag_something_changed:
				# writing to arduino
				ser.flush()
				#this somehow works
				number = ret["buffer"] + ret["home"] + ret["win_open"] + ret["door_open"] + ret["light_on"] + ret["temp"] + ret["humidity"]
				# number = "".join([ret[key] for key in ret.keys()])
				for char in list(number):
					ser.write(number)
				#ser.write(number)
				print number
				sleep(.1)


		# while data_dict["home"]:

		# 	if data_dict["energy_saver"]:
		# 		if data_dict["auto"]:
		# 			flag_something_changed = True
		# 			ret["home"] = 0
		# 		else:
		# 			flag_something_changed = True
		# 			ret["auto"] = 0












