#!/usr/bin/env python3

"""
Uses osgeo rasterize function to turn vector charts into raster ones
"""

import navpy

from osgeo import gdal
from osgeo import ogr

from LayerConversions import rasterizeSingleLayer

RASTERIZE_COLOR_FIELD = "__color__"


def openFile() -> ogr.DataSource:
    return ogr.Open("Charts/US5MA28M/ENC_ROOT/US5MA28M/US5MA28M.000")


def boxDimensions(bounds):
    [lon_min, lon_max, lat_min, lat_max] = bounds

    ned = navpy.lla2ned(lat_max, lon_max, 0, lat_min, lon_min, 0)
    n = ned[0]
    e = ned[1]

    return [e, n]


def getFileBounds(fileData):
    bounds = []

    for i in range(fileData.GetLayerCount()):
        layer = fileData.GetLayer(i)
        x_min, x_max, y_min, y_max = layer.GetExtent()
        if abs(x_min - x_max) > 0.000001 and abs(y_min - y_max) > 0.000001:  # Some layers are very small, so we don't care about them
            if len(bounds) == 0:
                bounds = [x_min, x_max, y_min, y_max]
            else:
                bounds[0] = min(bounds[0], x_min)
                bounds[1] = min(bounds[1], x_max)
                bounds[2] = min(bounds[2], y_min)
                bounds[3] = min(bounds[3], y_max)

    return bounds


def sortLayers():
    # 7: Buoys
    # 13: Towers on rocks in woods hole
    # 29: Shallow, near shore stuff
    # 34: Water
    # 41: Depth soundings
    # 42: Rocks

    return [21, 23, 5, 4, 14, 15, 29, 17, 16, 12, 39, 42]


if __name__ == '__main__':
    print("Start")
    file = openFile()
    bounds = getFileBounds(file)
    print("Raster")

    # Make a copy of the file so we can modify stuff
    vectorSource = ogr.GetDriverByName("Memory").CopyDataSource(file, "")

    # Make the raster image
    width_px = 1000

    # Figure out the pixel size and stuff for everything
    [x_min, x_max, y_min, y_max] = bounds  # These are lat and lon values (x is lon, y is lat)
    [xLengthMeters, yLengthMeters] = boxDimensions(bounds)  # Convert to x and y size
    pixelsPerMeter = float(width_px) / float(xLengthMeters)  # Figure out how tall the image should be based on how wide it is
    height = int(yLengthMeters * pixelsPerMeter)
    pixelSizeX = (x_max - x_min) / width_px  # Figure out pixel size in lat and lon
    pixelSizeY = (y_max - y_min) / height

    driver = gdal.GetDriverByName('GTiff')
    rasterImage = driver.Create('Output.tif', width_px, height, 3, gdal.GDT_Byte)
    rasterImage.SetGeoTransform((x_min, pixelSizeX, 0, y_max, 0, -pixelSizeY))
    rasterImage.GetRasterBand(1).SetNoDataValue(10000)

    sortedLayers = sortLayers()

    for layerNumber in sortedLayers:
        try:
            layer = vectorSource.GetLayer(layerNumber)
            image = rasterizeSingleLayer(layer, rasterImage)
        except Exception as e:
            print(e)

    print("DONE")
