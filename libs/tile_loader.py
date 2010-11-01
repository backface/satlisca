#!/usr/bin/env python
#######################################
#
# load google-style tiles for a given lat/lon
# from internet or local cache
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
###########################################

import tilenames
import myutils
from PIL import Image
import urllib
import sys, time

class TileLoader:
	def __init__(self):
		self.zoom = 12
		self.retry = 3
		self.surround = 2
		self.tileSize = 256		
		self.source = "landsat"
		self.cache_path = "cache"
		self.w = 512
		self.h = 512
		self.filetype = "PNG"
		self.extensions = {
			"PNG":"png",
			"JPEG":"jpg",
			"TIFF":"tif" }
		self.quality = 98
		self.ulx = 0
		self.uly = 0
		self.lrx = 0
		self.lry = 0
		self.bounds = 0,0,0,0
		
	def setSize(self, w, h):
		self.w = w
		self.h = h

	def setJPEGQuality(self, q):
		self.qualtiy = q

	def setCacheDir(self, dir):
		self.cache_path = dir

	def setSource(self, src):
		self.source = src

	def setZoom(self, zoom):
		self.zoom = zoom

	def setFileType(self,type):
		self.filetype = type

	def setRetryCount(self, i):
		self.retry = 3
		# not yet implemented
		
	def loadTile(self,z,tx,ty):
		
		filecache = "%s/%s/%d/%d/%d.%s" % \
			(self.cache_path, self.source, z, tx, ty, self.extensions[self.filetype])
		url = tilenames.getTileUrl(tx,ty,z, self.source, self.filetype.lower())

		try:		
			img = Image.open(filecache)
			#print "opened image:", filecache
		except IOError:
			ready = False
			while not ready:
				try:
					print "download", filecache, "to cache..."
					#print url
					tmp = urllib.urlretrieve(url)
					img = Image.open(tmp[0]);
					if self.source == "landsat":
						img = img.resize((256,256),Image.ANTIALIAS)
					myutils.createPath(filecache)
					if self.filetype != "JPEG":
						img.save(filecache, self.filetype)
					else:
						img.save(filecache, self.filetype, quality=self.quality)
					ready = True
				except KeyboardInterrupt:
					exit(0)
				except:
					print "Unexpected error: %s" % sys.exc_info()[0]
					time.sleep(1)
					ready = False
		return img

	def loadTileSet(self, lat,lon):
		size = self.tileSize + 2 * self.tileSize * self.surround

		img = Image.new("RGB",(size, size))

		tx, ty = tilenames.tileXY(lat, lon, self.zoom)
		i = 0
		for x in range(tx - self.surround, tx + self.surround +1 ):
			j = 0
			for y in range(ty - self.surround, ty + self.surround +1 ):
				tile = self.loadTile(self.zoom, x, y)
				img.paste(tile,(i*self.tileSize, j*self.tileSize))
				j += 1
			i += 1

		#tmp, lry = tilenames.latEdges(ty + self.surround + 1, self.zoom);
		#uly, tmp = tilenames.latEdges(ty - self.surround, self.zoom);
		#ulx, tmp = tilenames.lonEdges(tx - self.surround, self.zoom);
		#tmp, lrx= tilenames.lonEdges(tx + self.surround + 1, self.zoom);
		#self.bounds = ulx, uly, lrx, lry
		#print self.bounds
		return img

	def getImageATLatLon(self, lat,lon):
		image = self.loadTileSet(lat, lon)
		x,y = tilenames.latlon2pixels(lat,lon, self.zoom)
		x *= self.tileSize
		y *= self.tileSize
		sx = image.size[0]
		sy = image.size[1]
		tsx = self.w
		tsy = self.h
		offx = self.tileSize/2 - x
		offy = self.tileSize/2 - y
		cropped = image.crop( (
			int(sx/2 - tsx/2 - offx), int(sy/2 - tsy/2 - offy) , \
			int(sx/2 + tsx/2 - offx), int(sy/2 + tsy/2 - offy)
			))

		# get bounds (seems to be slightly off!)
		x,y = tilenames.latlon2xy(lat,lon, self.zoom)
		print tilenames.xy2latlon(x,y,self.zoom)
		ul_lat, ul_lon = tilenames.xy2latlon(x - (tsx/2+ offx)/self.tileSize,
			y - (tsy/2+ offy)/self.tileSize,
			self.zoom)
		lr_lat, lr_lon = tilenames.xy2latlon(x + (tsx/2+ offx)/self.tileSize,
			y + (tsy/2+ offy)/self.tileSize,
			self.zoom)
		self.bounds = ul_lon, ul_lat, lr_lon, lr_lat
		print self.bounds

		return cropped

	def getBounds(self, lat,lon):
		return self.bounds

		
	

if __name__ == '__main__':
	tileloader = TileLoader()
	tileloader.setZoom(11)
	
	img = tileloader.getImageATLatLon(48.208330, 16.373060)
	img.show()
		
