#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# ## #############################################################
#
# Author: Mauricio Matamoros
# Date:
#
# ## ############################################################
import smbus2
import struct
import time
from datetime import datetime, timezone
import csv
import matplotlib
matplotlib.use('AGG')	# Usando el rasterizado a .png
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# RP2040 I2C device address
SLAVE_ADDR = 0x0A # I2C Address of RP2040

# Name of the file in which the log is kept
LOG_FILE = './temp.log'

# Initialize the I2C bus;
# RPI version 1 requires smbus.SMBus(0)
i2c = smbus2.SMBus(1)

TEMP_MARGIN = 5
GRAPH_PERIOD_S = 60

def graphTemperature():
	time = []
	temp = []
	try:
		with open(LOG_FILE, 'r') as fp:
			tempFile = csv.reader(fp, delimiter=' ')
			next(tempFile)
			for line in tempFile:
				time.append(datetime.fromtimestamp(float(line[0])).astimezone())
				temp.append(float(line[1]))
	except:
		return

	if len(time) <= 1 or len(temp) <= 1 or len(time) != len(temp):
		return

	fig, ax = plt.subplots()
	ax.plot(time, temp, label='Temperatura')

	plt.ylim(min(temp)-TEMP_MARGIN, max(temp)+TEMP_MARGIN)

	ax.xaxis.set_major_formatter(mdates.DateFormatter('%M:%S'))
	ax.xaxis.set_major_locator(mdates.AutoDateLocator())

	plt.title("Temperatura el {}/{}/{} a las {} h.".format(
		time[0].day, time[0].month, time[0].year, time[0].hour))
	plt.xlabel("Tiempo [min:seg]")
	plt.ylabel("Temperatura [°C]")
	plt.legend()
	plt.tight_layout()
	plt.savefig("Temperatura.png")
	plt.clf()


def readTemperature():
	try:
		msg = smbus2.i2c_msg.read(SLAVE_ADDR, 4)
		i2c.i2c_rdwr(msg)  # Performs write (read request)
		data = list(msg)   # Converts stream to list
		# list to array of bytes (required to decode)
		ba = bytearray()
		for c in data:
			ba.append(int(c))
		temp = struct.unpack('<f', ba)[0]
		#cTime = datetime.utcnow().replace(tzinfo=timezone.utc).astimezone()
		#print(f"Temperatura actual: {temp: .2f} °C @ {cTime}")
		return temp
	except:
		return None

def log_temp(temperature):
	try:
		with open(LOG_FILE, 'a+') as fp:
			fp.write('{} {}\n'.format(
				time.time(),
				temperature
			))
	except:
		return

def reset_log():
	try:
		with open(LOG_FILE, 'w') as fp:
			fp.write('Tiempo[s] Temperatura[*C]\n')
	except:
		return

def main():
	reset_log()
	start = time.time()
	while True:
		try:
			if time.time() - start >= GRAPH_PERIOD_S:
				start = time.time()
				graphTemperature()
				print("Nueva grafica disponible")
				reset_log()

			cTemp = readTemperature()
			log_temp(cTemp)
			time.sleep(1)

		except KeyboardInterrupt:
			return


if __name__ == '__main__':
	main()
