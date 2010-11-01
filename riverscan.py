#!/usr/bin/env python
#######################################
#
# slitscan satellite data over a track
#
# author:(c) Michael Aschauer <m AT ash.to>
# www: http:/m.ash.to
# licenced under: GPL v3
# see: http://www.gnu.org/licenses/gpl.html
#
#######################################

from libs.track import TrackWalker
from libs.tile_loader import TileLoader
from libs.slitscanner import SlitScanner
from libs import myutils
from PIL import ImageDraw, Image
import sys, os
import getopt

# current setting
# for landsat: 20m, zoom=12, lw=1
# for google: 10m, zoom=13, lw=1
name = "noname"
size = (512,512)
lh = 1
source = "landsat"
interval = 20
zoom = 12
overwriteExisting = False
output = "scan"
trackfiles = []
display = True
format = "JPEG"
write_log_files = True
process_images = True
cache_only = False


def usage():
	print """
usage: riverscan.py -i TRACKFILE.gpx [-i FILE.gpx ..] [options]

linescan over map data along a gps track

options:
    -h, --help              print usage
    -i, --input=FILE        GPX track file (REQUIRED!)
    -n, --name=NAME         name of scan
    -o, --output=PATH       output path
    -z, --zoom=ZOOM         zoom setting
    -l, --lineheight=LH     lineheight of scan line
    -m, --interval=METERS   interpolate track to interval in meters (0=off)
    -x, --width=WIDTH       width of output tiles
    -y, --height=HEIGHT     height if output tiles
    -s, --source=SOURCE     source map ["landsat","google_sat"]
    -w, --overwrite         overwrite existing scan tiles (default:FALSE)
    -n, --nodisplay         don't display visual output
    -f, --format=FORMAT     image format for cache and output
                             [JPEG,PNG,TIFF] - default: JPEG
        --cacheonly         download cache files only (don't scan)
        --nologs            don't write gps-logfiles for scanned img
        --logsonly          just write gps-logfiles for scanned img
"""

def process_args():
	global trackfiles, interval, zoom, source, size
	global output, overwriteExisting, lh, name
	global display, format
	global process_images, write_log_files, cache_only
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hi:o:n:s:z:l:x:y:m:wdf:pcg",
			["help", "input=","output=","name=","source=","zoom=",
				"lineheight=","width=","height=","interval=",
				"overwrite","nodisplay","format=","nologs","cacheonly","logsonly"])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)

	for o, a in opts:
		if o == "-v":
			verbose = True
		elif o in ("-h", "--help"):
			usage()
			sys.exit()
		elif o in ("-o", "--output"):
			output = a
		elif o in ("-i", "--input"):
			trackfiles.append(a)
		elif o in ("-z", "--zoom"):
			zoom = int(a)
		elif o in ("-l", "--lineheight"):
			lh = int(a)
		elif o in ("-s", "--source"):
			source = a
		elif o in ("-x", "--width"):
			size = (a,size[1])           
		elif o in ("-y", "--height"):
			size = (size[0],a)
		elif o in ("-n", "--name"):
			name = a
		elif o in ("-m", "--interval"):
			interval = float(a)
		elif o in ("-f", "--format"):
			format = a
		elif o in ("-w","--overwrite"):
			overwriteExisting = True
		elif o in ("-d","--nodisplay"):
			display = False
		elif o in ("--nologs"):
			write_log_files = False
		elif o == "--logsonly":
			write_log_files = True
			process_images = False
			display = False
			print "logsonly"
		elif o in ("--cacheonly"):
			write_log_files = False
			process_images = False
			display = False
			cache_only = True		
		else:
			assert False, "unhandled option"

	if len(trackfiles) == 0:
		print "trackfile required."
		usage()
		sys.exit(2)
		

if __name__ == '__main__':

	process_args()
	
	if display:
		import cv
		cv.NamedWindow("current")
		cv.NamedWindow("scan")

	track = TrackWalker()
	
	imgloader = TileLoader()
	imgloader.setSource(source)		
	imgloader.setZoom(zoom)
	imgloader.setFileType(format)
	print "loading images from", source, "at zoom level", zoom
	
	scan_path = output+"/"+name+"/"+str(interval)+"m/"+str(zoom)
	print "scan to", scan_path
	
	slitscanner = SlitScanner(lh)
	slitscanner.setFileType(format)
	slitscanner.setPath(scan_path + "/" + source)
	slitscanner.setSize(size[0],size[1])	

	for trackfile in trackfiles:
		
		print "loading track", trackfile
		track.load(trackfile)
		print "track points: %d, length: %0.2fkm" %( track.getPointNumber(),track.getTotalDistance())
	
		if interval > 0:
			print "interpolating points at",interval,"meters ..."
			track.interpolate(interval,True)
			print "track points: %d, length: %0.2fkm" %( track.getPointNumber(),track.getTotalDistance())
		
		while track.goToNext():
		
			percent = float(track.getPointId()) / float(track.getPointNumber()) * 100
			
			print "%0.2f%%, #%06d, %0.6f, %0.6f, bearing: %0.3f, distance: %0.0fm, total: %0.1fkm" % \
			( 	percent, track.getPointId(), track.getLat(), track.getLon(), \
				track.getBearing(), track.getDistanceToLast(), track.getDistance()/1000 )

			if cache_only or process_images:
				if not ((not overwriteExisting) and slitscanner.fileExists()):
					img = imgloader.getImageATLatLon( track.getLat(), track.getLon())
				
			if process_images:
				
				if ((not overwriteExisting) and slitscanner.fileExists()):
					slitscanner.addButDontScanFrame()
				else:
					img = imgloader.getImageATLatLon( track.getLat(), track.getLon())	

					bearing = track.getBearing()

					if bearing < 90:
						angle = - (90 - bearing)
					else:
						angle = (bearing - 90)
			
					img_rot = img.rotate(angle, Image.BICUBIC, True)
					rot = img_rot.crop( (
						img_rot.size[0]/2 - size[0]/2,
						img_rot.size[1]/2 - size[1]/2,
						img_rot.size[0]/2 + size[0]/2,
						img_rot.size[1]/2 + size[1]/2)
					)
					slitscanner.addFrame(rot)

					# draw crosshair (debug output)
					draw = ImageDraw.Draw(rot)
					draw.line( (
						0,	img.size[1]/2,
						img.size[0], img.size[1]/2
						), fill=128	)
					draw.line( (
						img.size[0]/2, 0,
						img.size[0]/2, img.size[1]
						), fill=128 )			
					del draw

					# visual debug/preview output via opencv
					if display:					
						cv_img = cv.CreateImageHeader(rot.size, cv.IPL_DEPTH_8U, 3)
						cv.SetData(cv_img, rot.tostring())
						cv.CvtColor(cv_img, cv_img, cv.CV_RGB2BGR)
						cv.ShowImage("current",cv_img)

						scan_img = slitscanner.getImage()
						cv_scan_img = cv.CreateImageHeader(scan_img.size, cv.IPL_DEPTH_8U, 3)
						cv.SetData(cv_scan_img, scan_img.tostring())
						cv.CvtColor(cv_scan_img, cv_scan_img, cv.CV_RGB2BGR)
						cv.ShowImage("scan",cv_scan_img)

						cv.WaitKey(10)					
					
			elif write_log_files:
				slitscanner.addButDontScanFrame()

			if write_log_files:
				log_file = slitscanner.getFileBaseName()+".log"
				myutils.createPath(log_file)
				f = open(log_file,"a")
				f.write("%d, %f, %f\n" % (slitscanner.getPixelInScan(), track.getLat(), track.getLon()))
				f.close()

	if process_images:		
		if (not overwriteExisting) and slitscanner.fileExists():
			slitscanner.addButDontScanFrame()		
		else:
			slitscanner.saveImage()
