#!/usr/bin/env python
#######################################
#
# simple and stupid GPS/GPX track walker
# with interpolation
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################

from xml.dom import minidom
import numpy as np
from scipy import interpolate

import mygeo
import sys

class TrackWalker:

	def __init__(self):
		self.cur = 0
		self.points = []
		self.len = 0
		self.distance = 0
		self.interpolated = False

	def load(self, file):
		self.filename = file
		xmldoc = minidom.parse(file) 
		gpx = xmldoc.firstChild
		self.points = gpx.getElementsByTagName("trkpt")
		self.distance = 0
		self.cur = 0
		self.interpolated = False
		self.len = len(self.points)

	def goToNext(self):
		if self.cur + 1 >= self.len:
			return False			
		else:
			self.cur += 1
			self.distance += self.getDistanceToLast()
			return True
			
	def hasNext(self):
		if self.cur + 1 >= self.len:
			return False			
		else:
			return True		

	def hasPrev(self):
		if self.cur > 0:
			return True			
		else:
			return False
			
	def rewind(self):
		self.cur = 0
		self.distance = 0

	def getLat(self):
		if not self.interpolated:
			lat = float(self.points[self.cur].attributes["lat"].value)
		else:
			 lat = self.points[self.cur][0]
		return lat

	def getLon(self):
		if not self.interpolated:
			lon = float(self.points[self.cur].attributes["lon"].value)
		else:
			lon = self.points[self.cur][1]
		return lon

	def getPoint(self):
		if not self.interpolated:
			lat = float(self.points[self.cur].attributes["lat"].value)
			lon = float(self.points[self.cur].attributes["lon"].value)
		else:
			lat = self.points[self.cur][0]
			lon = self.points[self.cur][1]
		return lat,lon
		
	def getNextPoint(self):		
		if self.cur < self.len:
			if not self.interpolated:
				lat = float(self.points[self.cur+1].attributes["lat"].value)
				lon = float(self.points[self.cur+1].attributes["lon"].value)
			else:
				lat = self.points[self.cur+1][0]
				lon = self.points[self.cur+1][1]
			return lat,lon
		else:
			return 0

	def getPointNumber(self):
		return self.len

	def getPointId(self):
		return self.cur

	def getPrevPoint(self):
		if self.cur > 0:
			if not self.interpolated:
				lat = float(self.points[self.cur-1].attributes["lat"].value)
				lon = float(self.points[self.cur-1].attributes["lon"].value)
			else:
				lat = self.points[self.cur-1][0]
				lon = self.points[self.cur-1][1]
			return lat, lon
		else:
			return False

	def getBearing(self):
		if self.hasNext():
			lat, lon = self.getPoint()
			next_lat, next_lon = self.getNextPoint()
			brng = mygeo.getBearing_old(lat, lon, next_lat, next_lon)
			return brng
		else:
			return False
			
	def getDistanceToLast(self):
		if self.hasPrev():
			lat, lon = self.getPoint()
			prev_lat, prev_lon = self.getPrevPoint()
			dist = mygeo.getDistGeod(prev_lat, prev_lon, lat, lon)
			return dist
		else:
			return 0

	def getPointAt(self,id):
		if not self.interpolated:
			lat = float(self.points[id].attributes["lat"].value)
			lon = float(self.points[id].attributes["lon"].value)
		else:
			lat = self.points[id][0]
			lon = self.points[id][1]
		return lat, lon
		
	# caculate Distance in km
	def getTotalDistance(self):
		last_lat, last_lon = self.getPointAt(0)
		totaldist = 0
		
		for i in range(1,self.len):
			lat, lon  = self.getPointAt(i)
			dist = mygeo.getDistGeod(lat, lon, last_lat, last_lon)
			totaldist += dist				
			last_lat = lat
			last_lon = lon	
		return totaldist / 1000

	def getDistance(self):
		return self.distance

	# interpolate along track (distance in metres)
	def interpolate(self, distance, spline=False):

		if spline:
			spline = 2
		else:
			spline = 1
			
		orig_num = self.getPointNumber()
		x = []
		y = []
		x.append(self.getLat())
		y.append(self.getLon())

		while self.goToNext():
			x.append(self.getLat())
			y.append(self.getLon())
	
		tck,u = interpolate.splprep([x,y],s=0,k=spline)
		num = int(self.getDistance() / distance)
		x,y= interpolate.splev(np.linspace(0,1,num),tck)	

		self.points = []
		for j in range(0,len(x)):
			self.points.append((x[j], y[j]))

		self.interpolated = True
		self.len = len(self.points)
		self.rewind()


if __name__ == '__main__':
	track = Track()
	track.load(sys.argv[1])
	print "distance: ", track.getTotalDistance()

	print track.getLat(), track.getLon(), \
		track.getBearing(), track.getDistance()
	while track.next():
		print track.getLat(), track.getLon(), \
			track.getBearing(), track.getDistance()
