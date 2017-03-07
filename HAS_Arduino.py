# import serial
# import requests
# import json
from time import *
from State import *
import requests
import json
import serial

# # # Replace with the correct URL
# api_key = '745ba33d1bf59284f45453e6030d89c9'
# url = 'http://api.openweathermap.org/data/2.5/forecast?q=Austin,us&mode=json&appid=' + api_key

# r = requests.get(url).json()
# sky_status = r["weather"][0]["main"]#clear or rainy etc
# cur_temp = r["main"]["temp"]
# cur_hum = r["main"]["humidity"]



# ser = serial.Serial('COM4', 9600)
# ser.readline()
# print "hello"
# # self.counter = 32 # Below 32 everything in ASCII is gibberish
# # while True:
# #     self.counter +=1
# #     ser.write(str(chr(self.counter))) # Convert the decimal number to ASCII then send it to the Arduino
# #     print ser.readline() # Read the newest output from the Arduino
# #     sleep(.1) # Delay for one tenth of a second
# #     if self.counter == 255:
# #     	self.counter = 32
class Card():

	def __init__(self, y, icon):
		self.x = 10
		self.y = y
		self.width = 280
		self.height = 88
		self.icon = icon
		self.color = (197, 0, 123)#change to fix palete of buildation
		self.font_color = (255, 255, 255)
		self.rect = Rect(self.x, self.y, self.width, self.height)
		self.on = False

	def draw_box(self):
		#draw corners
		draw.circle(screen, self.color, (20, self.y + 10), 10, 0)
		draw.circle(screen, self.color, (20, self.y + self.height - 10), 10, 0)
		draw.circle(screen, self.color, (280, self.y + 10), 10, 0)
		draw.circle(screen, self.color, (280, self.y + self.height - 10), 10, 0)
		#draw sides
		draw.rect(screen, self.color, Rect(10, self.y + 10, 20, self.height - 20), 0)
		draw.rect(screen, self.color, Rect(20, self.y, 260, 20), 0)
		draw.rect(screen, self.color, Rect(270, self.y + 10, 20, self.height - 20), 0)
		draw.rect(screen, self.color, Rect(20, self.y + self.height - 20, 260, 20), 0)
		#fill in center
		draw.rect(screen, self.color, Rect(30, self.y + 20, 240, self.height - 40), 0)

	def draw_icon(self):
		screen.blit(self.icon, (self.x + 12, self.y + 12))

	def draw_text(self):
		screen.blit(myfont.render("Status:" + str(self.on), 1, self.font_color), (110, self.y + 12))

	#draw square with rounded corners
	#have information overlayed
	def draw(self):
		self.draw_box()
		self.draw_icon()
		self.draw_text()

	#have to card expand to display recomendataions
	#also have it display past data
	def click_began(self):
		self.on = not self.on

	def update(self):
		self.rect = Rect(self.x, self.y, self.width, self.height)
		if self.on:
			self.color = (197, 0, 123)
			self.font_color = (255, 255, 255)
		else:
			self.color = (255, 255, 255)
			self.font_color = (197, 0, 123)

class HAS(State):

	def setup(self):
		images = [transform.scale(image.load("Images/home.jpg"), (64, 64)),
				transform.scale(image.load("Images/window.jpg"), (64, 64)),
				transform.scale(image.load("Images/door.jpg"), (64, 64)),
				transform.scale(image.load("Images/lights.jpg"), (64, 64)),
				transform.scale(image.load("Images/therm.jpg"), (64, 64)),
				transform.scale(image.load("Images/fan.jpg"), (64, 64)),]
		self.cards = [Card(10 + 98*i, images[i]) for i in range(6)]
		self.background_color = (0,158,255)

		port = "/dev/cu.usbmodem1411"
		self.ser = serial.Serial(port, 115200, timeout=5)
		#sleep(1)

		self.counter = 0
		self.temp_threshold = 30.0 #will change later
		values = ["a", 0, 0, 0, 0, 0.0, 0.0] # values [home, win_open, door_open, light_on, temp, humidity]
		self.flag_something_changed = False
		api_key = '745ba33d1bf59284f45453e6030d89c9'
		url = 'http://api.openweathermap.org/data/2.5/weather?q=Austin,us&mode=json&appid=' + api_key
		# possible bug where values don't exist
		r = requests.get(url).json()
		self.sky_status = r["weather"][0]["main"] #clear or rainy etc
		self.cur_temp = r["main"]["temp"]
		cur_hum = r["main"]["humidity"]
		self.data = ["23 4 34 5 2 3"]
		self.home_flag = False

	def draw(self):
		screen.fill(self.background_color)
		for card in self.cards:
			card.draw()
		display.update()

	def click_began(self):
		for i, card in enumerate(self.cards):
			if card.rect.collidepoint(mouse.get_pos()) and i == 0:
				card.click_began()
				self.home_flag = True
			elif card.rect.collidepoint(mouse.get_pos()):
				card.click_began()
				self.flag_something_changed = True

	def update(self):
		for card in self.cards:
			card.update()
		b = time()
		try:
			if self.counter%20 == 0:
				self.data = self.ser.readline().split(" ")
		except:
			pass
		data = self.data[:-1]
		c = time()
		# weird bug where first 4 data points are stupid
		self.counter += 1
		if self.counter > 10:

			#House logic using variables below
			if len(data) != 6:
				return
			try:
				int(data[0])
			except:
				return
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
					"win_open": "1",
					"door_open": "1",
					"light_on": "1",
					"temp": "1",
					"humidity": "1"
					}
			c = time()
			# number = "a00000"
			# the first value MUST be an "a"
			if not data_dict["home"]:
				print "not home"
				number = "a011111"
				# if self.sky_status == "Clear":
				# 	self.flag_something_changed = True
				# 	ret["win_open"] = "1"
				# 	ret["door_open"] = "1"
				# else:
				# 	self.flag_something_changed = True
				# 	ret["door_open"] = "1"
				if self.home_flag:
					print "this activated"
					ret["home"] = "1"
					self.home_flag = False
				# if self.flag_something_changed:
				# 	# writing to arduino
				# 	self.ser.flush()
				# 	#this somehow works
				# 	number = ret["buffer"] + ret["home"] + ret["win_open"] + ret["door_open"] + ret["light_on"] + ret["temp"] + ret["humidity"]
				# 	# number = "".join([ret[key] for key in ret.keys()])
				# 	print "I'm away" + str(number)
			# 		for char in list(number):
			# 			self.ser.write(number)
			# 		#ser.write(number)
			# 		sleep(.033)
			# 		self.flag_something_changed = False
			else:
				print "home"
				number = "a100000"
			# 	if self.flag_something_changed:
			# 		# writing to arduino
			# 		self.ser.flush()
			# 		#this somehow works
			# 		number = ["a"] + ["1" if card.on else "0" for card in self.cards] 
			# 		print number
					# number = "".join([ret[key] for key in ret.keys()])
			for char in list(number):
				self.ser.write(number)
			#ser.write(number)
			sleep(.033)
			self.flag_something_changed = False

if __name__ == '__main__':
	init()
	myfont = font.SysFont("monospace", 15)
	screen = display.set_mode((300, 598))
	origin = (150, 250)
	HAS(screen)
# # data = [float(d) for d in data]
# # for i, d in enumerate(data):
# # 	data[i] = float(d)

# # "".join([ret[key] for key in ret.keys()])
# print bool(-49.0)