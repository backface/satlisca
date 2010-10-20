#!/usr/bin/env python
#-------------------------------------------------------
# Translates between lat/long and the slippy-map tile
# numbering scheme
# 
# http://wiki.openstreetmap.org/index.php/Slippy_map_tilenames
# 
# Written by Oliver White, 2007
# This file is public-domain
#-------------------------------------------------------
from math import *

def numTiles(z):
  return(pow(2,z))

def sec(x):
  return(1/cos(x))

def latlon2relativeXY(lat,lon):
  x = (lon + 180) / 360
  y = (1 - log(tan(radians(lat)) + sec(radians(lat))) / pi) / 2
  return(x,y)

def latlon2xy(lat,lon,z):
  n = numTiles(z)
  x,y = latlon2relativeXY(lat,lon)
  return(n*x, n*y)

def latlon2pixels(lat,lon,z):
	n = numTiles(z)
	x,y = latlon2relativeXY(lat,lon)
	offsx = n*x - int(n*x) 
	offsy = n*y - int(n*y)
	return offsx, offsy
  
def tileXY(lat, lon, z):
  x,y = latlon2xy(lat,lon,z)
  return(int(x),int(y))

def xy2latlon(x,y,z):
  n = numTiles(z)
  relY = y / n
  lat = mercatorToLat(pi * (1 - 2 * relY))
  lon = -180.0 + 360.0 * x / n
  return(lat,lon)
  
def latEdges(y,z):
  n = numTiles(z)
  unit = 1 / n
  relY1 = y * unit
  relY2 = relY1 + unit
  lat1 = mercatorToLat(pi * (1 - 2 * relY1))
  lat2 = mercatorToLat(pi * (1 - 2 * relY2))
  return(lat1,lat2)

def lonEdges(x,z):
  n = numTiles(z)
  unit = 360 / n
  lon1 = -180 + x * unit
  lon2 = lon1 + unit
  return(lon1,lon2)
  
def tileEdges(x,y,z):
  lat1,lat2 = latEdges(y,z)
  lon1,lon2 = lonEdges(x,z)
  return((lat2, lon1, lat1, lon2)) # S,W,N,E

def mercatorToLat(mercatorY):
  return(degrees(atan(sinh(mercatorY))))

def tileSizePixels():
  return(256)

def tileLayerExt(layer):
  if(layer in ('oam')):
    return('jpg')
  return('png')

def tileLayerBase(layer):
  layers = { \
    "tah": "http://cassini.toolserver.org:8080/http://a.tile.openstreetmap.org/+http://toolserver.org/~cmarqu/hill/",
	#"tah": "http://tah.openstreetmap.org/Tiles/tile/",
    "oam": "http://oam1.hypercube.telascience.org/tiles/1.0.0/openaerialmap-900913/",
    "osm_mapnik": "http://tile.openstreetmap.org/mapnik/"
    }
  return(layers[layer])
  
def tileURL(x,y,z,layer="osm_mapnik"):
  return "%s%d/%d/%d.%s" % (tileLayerBase(layer),z,x,y,tileLayerExt(layer))

def tileGoogleURL(x,y,z,layer="sat"):
	layers = { \
    "sat": "s",
    "terrain": "t",
    "overlay": "h",
    "street":"m"
	} 
	return "http://mt.google.com/vt/lyrs=%s@132&x=%d&y=%d&z=%d" % (layers[layer],x,y,z)

def tileYahooArialURL(x,y,z):
  return "http://aerial.maps.yimg.com/img?x=%d&y=%d&z=%d&v=1.7" % (x,y,z)

def tileWMSURL(x,y,z,format="jpeg"):
  layers = "global_mosaic"
  wms_url = "http://onearth.jpl.nasa.gov/wms.cgi?request=GetMap&styles="
  wms_url += "&format=image/jpeg&srs=EPSG:4326&width=512&height=512"
  wms_url += "&layers=" + layers
  x1, y1, x2, y2 = tileEdges(x,y,z)
  return "%s&bbox=%f,%f,%f,%f&layers=%s" % (wms_url, y1, x1, y2, x2, layers)

def getTileUrl(x,y,z,source,format="jpeg"):
	if source == "osm_mapnik":
		return tileURL(x,y,z)
	elif source == "landsat":
		return tileWMSURL(x,y,z,format)
	elif source == "google_sat":
		return tileGoogleURL(x,y,z,"sat")
	elif source == "google_terrain":
		return tileGoogleURL(x,y,z,"terrain")
	elif source == "google_street":
		return tileGoogleURL(x,y,z,"street")
	elif source == "yahoo":
		return tileYahooArialURL(x,y,z)

if __name__ == "__main__":
  for z in range(0,17):
    x,y = tileXY(48.208330, 16.373060, z)
    
    s,w,n,e = tileEdges(x,y,z)
    print "%d: %d,%d --> %1.3f :: %1.3f, %1.3f :: %1.3f" % (z,x,y,s,n,w,e)
    print tileURL(x,y,z,"mapnik")
    #print "<img src='%s'><br>" % tileURL(x,y,z)
