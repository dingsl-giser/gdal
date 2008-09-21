#!/usr/bin/env python
#******************************************************************************
#  $Id: rgb2pct.py 13110 2007-11-26 21:28:27Z hobu $
# 
#  Project:  GDAL Python Interface
#  Purpose:  Application for converting raster data to a vector polygon layer.
#  Author:   Frank Warmerdam, warmerdam@pobox.com
# 
#******************************************************************************
#  Copyright (c) 2008, Frank Warmerdam
# 
#  Permission is hereby granted, free of charge, to any person obtaining a
#  copy of this software and associated documentation files (the "Software"),
#  to deal in the Software without restriction, including without limitation
#  the rights to use, copy, modify, merge, publish, distribute, sublicense,
#  and/or sell copies of the Software, and to permit persons to whom the
#  Software is furnished to do so, subject to the following conditions:
# 
#  The above copyright notice and this permission notice shall be included
#  in all copies or substantial portions of the Software.
# 
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#  OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#  THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#******************************************************************************

try:
    from osgeo import gdal, ogr
except ImportError:
    import gdal
    import ogr

import sys
import os.path

def Usage():
    print """
gdal_polygonize [-o name=value] [-nomask] [-mask filename] raster_file [-b band]
                [-q] [-f ogr_format] out_file [layer] [fieldname]
"""
    sys.exit(1)

# =============================================================================
# 	Mainline
# =============================================================================

format = 'GML'
options = []
quiet_flag = 0
src_filename = None
src_band_n = 1

dst_filename = None
dst_layername = None
dst_fieldname = None
dst_field = -1

mask = 'default'

gdal.AllRegister()
argv = gdal.GeneralCmdLineProcessor( sys.argv )
if argv is None:
    sys.exit( 0 )

# Parse command line arguments.
i = 1
while i < len(argv):
    arg = argv[i]

    if arg == '-f':
        i = i + 1
        format = argv[i]

    elif arg == '-q':
        quiet_flag = 1
        
    elif arg == '-nomask':
        mask = 'none'
        
    elif arg == '-mask':
        i = i + 1
        mask = argv[i]
        
    elif arg == '-b':
        i = i + 1
        src_band_n = int(argv[i])

    elif src_filename is None:
        src_filename = argv[i]

    elif dst_filename is None:
        dst_filename = argv[i]

    elif dst_layername is None:
        dst_layername = argv[i]

    elif dst_fieldname is None:
        dst_fieldname = argv[i]

    else:
        Usage()

    i = i + 1

if src_filename is None or dst_filename is None:
    Usage()

if dst_layername is None:
    dst_layername = 'out'
    
# =============================================================================
# 	Verify we have next gen bindings with the polygonize method.
# =============================================================================
try:
    gdal.Polygonize
except:
    print
    print 'gdal.Polygonize() not available.  You are likely using "old gen"'
    print 'bindings or an older version of the next gen bindings.'
    print
    sys.exit(1)

# =============================================================================
#	Open source file
# =============================================================================

src_ds = gdal.Open( src_filename )
    
if src_ds is None:
    print 'Unable to open ', src_filename
    sys.exit(1)

srcband = src_ds.GetRasterBand(src_band_n)

if mask is 'default':
    maskband = srcband.GetMaskBand()
elif mask is 'none':
    maskband = None
else:
    mask_ds = gdal.Open( mask )
    maskband = mask_ds.GetRasterBand(1)

# =============================================================================
#       Try opening the destination file as an existing file.
# =============================================================================

try:
    gdal.PushErrorHandler( 'QuietErrorHandler' )
    dst_ds = ogr.Open( dst_filename, update=1 )
    gdal.PopErrorHandler()
except:
    dst_ds = None

# =============================================================================
# 	Create output file.
# =============================================================================
if dst_ds is None:
    drv = ogr.GetDriverByName(format)
    if not quiet_flag:
        print 'Creating output %s of format %s.' % (dst_filename, format)
    dst_ds = drv.CreateDataSource( dst_filename )

# =============================================================================
#       Find or create destination layer.
# =============================================================================
try:
    dst_layer = dst_ds.GetLayerByName(dst_layername)
except:
    dst_layer = None

if dst_layer is None:
    dst_layer = dst_ds.CreateLayer(dst_layername)

    if dst_fieldname is None:
        dst_fieldname = 'DN'
        
    fd = ogr.FieldDefn( dst_fieldname, ogr.OFTInteger )
    dst_layer.CreateField( fd )
    dst_field = 0
    
# =============================================================================
#	Invoke algorithm.
# =============================================================================

if quiet_flag:
    prog_func = None
else:
    prog_func = gdal.TermProgress
    
result = gdal.Polygonize( srcband, maskband, dst_layer, dst_field, options,
                          callback = prog_func )
    
srcband = None
dst_ds = None








