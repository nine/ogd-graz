#!/usr/bin/env python
# -*- coding: utf-8 -*-

import optparse
import textwrap

from math import pi,cos,sin,log,exp,atan
from subprocess import call
import sys, os
from Queue import Queue

import threading

import ogr,osr
import urllib


DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi

# Default number of download-threads to spawn
NUM_THREADS = 8

DESCRIPTION="""Donwload von Tiles in TMS-Ordnerstruktur von einem
WMS Server.
"""

VERSION='%prog version 1.0'


class IndentedHelpFormatterWithNL(optparse.IndentedHelpFormatter):
  def format_description(self, description):
    if not description: return ""
    desc_width = self.width - self.current_indent
    indent = " "*self.current_indent
# the above is still the same
    bits = description.split('\n')
    formatted_bits = [
      textwrap.fill(bit,
        desc_width,
        initial_indent=indent,
        subsequent_indent=indent)
      for bit in bits]
    result = "\n".join(formatted_bits) + "\n"
    return result

  def format_option(self, option):
    # The help for each option consists of two parts:
    #   * the opt strings and metavars
    #   eg. ("-x", or "-fFILENAME, --file=FILENAME")
    #   * the user-supplied help string
    #   eg. ("turn on expert mode", "read data from FILENAME")
    #
    # If possible, we write both of these on the same line:
    #   -x    turn on expert mode
    #
    # But if the opt string list is too long, we put the help
    # string on a second line, indented to the same column it would
    # start in if it fit on the first line.
    #   -fFILENAME, --file=FILENAME
    #       read data from FILENAME
    result = []
    opts = self.option_strings[option]
    opt_width = self.help_position - self.current_indent - 2
    if len(opts) > opt_width:
      opts = "%*s%s\n" % (self.current_indent, "", opts)
      indent_first = self.help_position
    else: # start help on same line as opts
      opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
      indent_first = 0
    result.append(opts)
    if option.help:
      help_text = self.expand_default(option)
# Everything is the same up through here
      help_lines = []
      for para in help_text.split("\n"):
        help_lines.extend(textwrap.wrap(para, self.help_width))
# Everything is the same after here
      result.append("%*s%s\n" % (
        indent_first, "", help_lines[0]))
      result.extend(["%*s%s\n" % (self.help_position, "", line)
        for line in help_lines[1:]])
    elif opts[-1] != "\n":
      result.append("\n")
    return "".join(result)



def minmax (a,b,c):
  a = max(a,b)
  a = min(a,c)
  return a

class GoogleProjection:
  def __init__(self,levels=18):
    self.Bc = []
    self.Cc = []
    self.zc = []
    self.Ac = []
    c = 256
    for d in range(0,levels):
      e = c/2;
      self.Bc.append(c/360.0)
      self.Cc.append(c/(2 * pi))
      self.zc.append((e,e))
      self.Ac.append(c)
      c *= 2

  def fromLLtoPixel(self,ll,zoom):
    d = self.zc[zoom]
    e = round(d[0] + ll[0] * self.Bc[zoom])
    f = minmax(sin(DEG_TO_RAD * ll[1]),-0.9999,0.9999)
    g = round(d[1] + 0.5*log((1+f)/(1-f))*-self.Cc[zoom])
    return (e,g)

  def fromPixelToLL(self,px,zoom):
    e = self.zc[zoom]
    f = (px[0] - e[0])/self.Bc[zoom]
    g = (px[1] - e[1])/-self.Cc[zoom]
    h = RAD_TO_DEG * ( 2 * atan(exp(g)) - 0.5 * pi)
    return (f,h)


class RenderThread:
  def __init__(self, tile_dir, url, q, printLock, maxZoom, overwrite):
    self.tile_dir = tile_dir
    self.url = url
    self.overwrite = overwrite
    self.q = q
    self.printLock = printLock
    
    # Projects between tile pixel co-ordinates and LatLong (EPSG:4326)
    self.tileproj = GoogleProjection(maxZoom+1)
    # setup url-projection
    srcSR = osr.SpatialReference()
    srcSR.ImportFromEPSG(4326)
    destSR = osr.SpatialReference()
    destSR.ImportFromEPSG(3857)
    self.tileTrans = osr.CoordinateTransformation(srcSR,destSR)



  def render_tile(self, tile_uri, x, y, z):

    # Calculate pixel positions of bottom-left & top-right
    p0 = (x * 256, (y + 1) * 256)
    p1 = ((x + 1) * 256, y * 256)

    # Convert to LatLong (EPSG:4326)
    l0 = self.tileproj.fromPixelToLL(p0, z);
    l1 = self.tileproj.fromPixelToLL(p1, z);
    
    x1 = self.tileTrans.TransformPoint(l0[0], l0[1])
    x2 = self.tileTrans.TransformPoint(l1[0], l1[1])
    #print 'l0= %10.6f , %10.6f, x1= %10.6f, %10.6f' % (l0[0], l0[1], x1[0], x1[1] )
    #print 'l1= %10.6f , %10.6f, x2= %10.6f, %10.6f' % (l1[0], l1[1], x2[0], x2[1] )
    url = self.url + '?LAYERS=1&FORMAT=image%2Fpng&VERSION=1.3.0&TRANSPARENT=TRUE&UNITS=meters&PROJECTION=EPSG%3A3857&EXCEPTIONS=INIMAGE&SERVICE=WMS&REQUEST=GetMap&STYLES=&CRS=EPSG%3A3857'
    url = url + '&BBOX=' + ('%10.6f' % x1[0]) + ',' + ('%10.6f' % x1[1]) + ',' + ('%10.6f' % x2[0]) + ','+ ('%10.6f' % x2[1]) + '&WIDTH=256&HEIGHT=256'
    urllib.urlretrieve(url, tile_uri)


  def loop(self):
    while True:
      #Fetch a tile from the queue and render it
      r = self.q.get()
      if (r == None):
        self.q.task_done()
        break
      else:
        (name, tile_uri, x, y, z) = r

      # overwrite existing files?
      exists= ""
      if not self.overwrite and os.path.isfile(tile_uri):
        exists= "exists"
      else:
        self.render_tile(tile_uri, x, y, z)

      bytes=os.stat(tile_uri)[6]
      empty= ''
      if bytes == 103:
        empty = " Empty Tile "
      self.printLock.acquire()
      print name, ":", z, x, y, exists, empty
      self.printLock.release()
      self.q.task_done()


def download_tiles(bbox, url, tile_dir, minZoom=1, maxZoom=18, overwrite=False, name="unknown", num_threads=NUM_THREADS, tms_scheme=False):
  print "download_tiles(",bbox, url, tile_dir, minZoom,maxZoom, name,")"

  # Launch rendering threads
  queue = Queue(32)
  printLock = threading.Lock()
  renderers = {}
  for i in range(num_threads):
    renderer = RenderThread(tile_dir, url, queue, printLock, maxZoom, overwrite)
    render_thread = threading.Thread(target=renderer.loop)
    render_thread.start()
    #print "Started render thread %s" % render_thread.getName()
    renderers[i] = render_thread

  if not os.path.isdir(tile_dir):
    os.mkdir(tile_dir)

  gprj = GoogleProjection(maxZoom+1)

  ll0 = (float(bbox[0]),float(bbox[3]))
  ll1 = (float(bbox[2]),float(bbox[1]))

  for z in range(minZoom,maxZoom + 1):
    px0 = gprj.fromLLtoPixel(ll0,z)
    px1 = gprj.fromLLtoPixel(ll1,z)

    # check if we have directories in place
    zoom = "%s" % z
    if not os.path.isdir(tile_dir + zoom):
      os.mkdir(tile_dir + zoom)
    for x in range(int(px0[0]/256.0),int(px1[0]/256.0)+1):
      # Validate x co-ordinate
      if (x < 0) or (x >= 2**z):
        continue
      # check if we have directories in place
      str_x = "%s" % x
      if not os.path.isdir(tile_dir + zoom + '/' + str_x):
        os.mkdir(tile_dir + zoom + '/' + str_x)
      for y in range(int(px0[1]/256.0),int(px1[1]/256.0)+1):
        # Validate x co-ordinate
        if (y < 0) or (y >= 2**z):
          continue
        # flip y to match OSGEO TMS spec
        if tms_scheme:
          str_y = "%s" % ((2**z-1) - y)
        else:
          str_y = "%s" % y
        tile_uri = tile_dir + zoom + '/' + str_x + '/' + str_y + '.png'
        # Submit tile to be rendered into the queue
        t = (name, tile_uri, x, y, z)
        try:
          queue.put(t)
        except KeyboardInterrupt:
          # hack to interrupt all threads
          print "Ctrl-c received! Sending kill to threads..."
          os._exit(0)
          #raise SystemExit("Ctrl-c detected, exiting...")


  # Signal render threads to exit by sending empty request to queue
  for i in range(num_threads):
    queue.put(None)
  # wait for pending rendering jobs to complete
  queue.join()
  for i in range(num_threads):
    renderers[i].join()



if __name__ == "__main__":

  p = optparse.OptionParser(
        formatter=IndentedHelpFormatterWithNL(),
        version=VERSION,
        description=DESCRIPTION,
      )
  p.add_option('--url',  default='http://geodaten1.graz.at/ArcGIS_Graz/services/Extern/BASISKARTE_WMS/MapServer/WMSServer')
  p.add_option('--tile-dir',  default="tiles")
  p.add_option('--min-zoom',  default=1, type="int")
  p.add_option('--max-zoom',  default=21, type="int")
  p.add_option('--bbox',      default="15.34,47.00,15.55,47.14")  # Graz, Austria 
  p.add_option('--overwrite', action="store_true")
  opts, args = p.parse_args()

  
  tile_dir = opts.tile_dir
  if not tile_dir.endswith('/'):
    tile_dir = tile_dir + '/'

  bbox = opts.bbox.split(',')
  download_tiles(bbox, opts.url, tile_dir, opts.min_zoom, opts.max_zoom, opts.overwrite, "Graz")

#eof
