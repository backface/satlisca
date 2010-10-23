#!/usr/bin/env python
#######################################
#
# simple and stupid slitscanner
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################

from PIL import Image
import myutils
import os

class SlitScanner:

	def __init__(self, width=2):
		self.slitWidth = width
		self.path = "scan"
		self.width = 512
		self.height  = 512
		self.scan_img = Image.new( \
			"RGB",(self.width, self.height), 
			(255,255,255))
		self.img_count = 1
		self.frame_count = 0
		self.slit_count = 0
		self.overwrite = True
		self.filetype = "JPEG"
		self.extensions = {
			"PNG":"png",
			"JPEG":"jpg",
			"TIFF":"tif" }
		self.quality = 98

	def setOverwriteExisting(b):
		self.overwrite = b

	def setPath(self, path):
		self.path = path

	def setFileType(self,type):
		self.filetype = type

	def setSlitWidth(self, w):
		self.slitWidth = w

	def setJPEGQuality(self, q):
		self.quality = q

	def setSize(self, w, h):
		self.width = w
		self.height = h
		self.scan_img = scan_img = Image.new( \
			"RGB",(self.width, self.height), 
			(255,255,255) )

	def getFileName(self):
		scan_file = "%s.%s" % \
			(self.getFileBaseName(), self.extensions[self.filetype])
		return scan_file

	def getFileBaseName(self):
		scan_file = "%s/%d/%06d" % \
			(self.path, self.width,
			self.img_count)
		return scan_file
		
	def addFrame(self, img):
		slit = img.crop( (
			(img.size[0]/2 - self.slitWidth/2),
			0,
			(img.size[0]/2 - self.slitWidth/2 + self.slitWidth),
			img.size[1]
			) )
			
		self.scan_img.paste(slit,
			(self.slit_count * self.slitWidth, 0,
			 self.slit_count * self.slitWidth + self.slitWidth, self.height ) )
			 
		if (self.slit_count + 1) * self.slitWidth >= self.width:
			scan_file = self.getFileName()
			myutils.createPath(scan_file)
			print "saving file:", scan_file
			if self.filetype == "JPEG":
				self.scan_img.save(scan_file,self.filetype,quality=self.quality)
			else:
				self.scan_img.save(scan_file,self.filetype)
			self.scan_img = Image.new("RGB",(self.width,self.height),(255,255,255))
			self.img_count +=1
			self.slit_count = 0
		else:
			self.frame_count += 1
			self.slit_count += 1

	def addButDontScanFrame(self):
		if self.slit_count * self.slitWidth > self.width:
			self.img_count +=1
			self.slit_count = 0
		else:
			self.frame_count += 1
			self.slit_count += 1				

	def getImage(self):
		return self.scan_img

	def getPixelInImage(self):
		return (self.slit_count + 1)

	def getPixelInScan(self):
		return (self.img_count - 1)  * self.width + (self.slit_count + 1)
		
	def fileExists(self):
		return os.path.exists(self.getFileName())
		
	def saveImage(self):
		myutils.createPath(self.getFileName())
		print "saving file:", scan_file
		self.scan_img.save(scan_file,"JPEG")
	
		
			
