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
		self.filetype = "PNG"
		self.extensions = {
			"PNG":"png",
			"JPEG":"jpg",
			"TIFF":"tif" }

	def setOverwriteExisting(b):
		self.overwrite = b

	def setPath(self, path):
		self.path = path

	def setFileType(self,type):
		self.filetype = type

	def setSlitWidth(self, w):
		self.slitWidth = w

	def setSize(self, w, h):
		self.width = w
		self.height = h
		self.scan_img = scan_img = Image.new( \
			"RGB",(self.width, self.height), 
			(255,255,255) )

	def getFileName(self):
		scan_file = "%s/%d/%d/%06d.%s" % \
			(self.path, self.slitWidth, self.width,
			self.img_count, self.extensions[self.filetype])
		return scan_file

	def getFileBaseName(self):
		scan_file = "%s/%d/%d/%06d" % \
			(self.path, self.slitWidth, self.width,
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
			 
		if self.slit_count * self.slitWidth > self.width:
			scan_file = "%s/%d/%d/%06d.%s" % \
				(self.path, self.slitWidth, self.width,
				self.img_count, self.extensions[self.filetype])
			myutils.createPath(scan_file)
			print "saving file:", scan_file
			self.scan_img.save(scan_file,"JPEG")
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

	def fileExists(self):
		scan_file = "%s/%d/%d/%06d.jpg" % (self.path, self.slitWidth, self.width, self.img_count)
		return os.path.exists(scan_file)
		
	def saveImage(self):
		scan_file = "%s/%d/%d/%06d.jpg" % (self.path, self.slitWidth, self.width, self.img_count)
		myutils.createPath(scan_file)
		print "saving file:", scan_file
		self.scan_img.save(scan_file,"JPEG")
	
		
			
