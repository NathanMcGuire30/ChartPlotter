#!/usr/bin/env python3

"""
Uses osgeo rasterize function to turn vector charts into raster ones
"""

import numpy
import navpy
import cv2
import osgeo.gdal

from osgeo import gdal
from osgeo import ogr

from LayerConversions import rasterizeSingleLayer, sortLayers


def openFile(chartName) -> ogr.DataSource:
    return ogr.Open("Charts/{0}/{0}.000".format(chartName))


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
                bounds[1] = max(bounds[1], x_max)
                bounds[2] = min(bounds[2], y_min)
                bounds[3] = max(bounds[3], y_max)

    return bounds


def parseSingleChart(file, rasterImage):
    # Make a copy of the file so we can modify stuff
    vectorSource = ogr.GetDriverByName("Memory").CopyDataSource(file, "")

    sortedLayers = sortLayers(file)

    for layerNumber in sortedLayers:
        try:
            layer = vectorSource.GetLayer(layerNumber)
            rasterizeSingleLayer(layer, rasterImage)
        except Exception as e:
            print(e)


def createRasterImage(bounds, width_px):
    # Figure out the pixel size and stuff for everything
    [x_min, x_max, y_min, y_max] = bounds  # These are lat and lon values (x is lon, y is lat)
    [xLengthMeters, yLengthMeters] = boxDimensions(bounds)  # Convert to x and y size
    pixelsPerMeter = float(width_px) / float(xLengthMeters)  # Figure out how tall the image should be based on how wide it is
    height_px = int(yLengthMeters * pixelsPerMeter)
    pixelSizeX = (x_max - x_min) / width_px  # Figure out pixel size in lat and lon
    pixelSizeY = (y_max - y_min) / height_px

    driver = gdal.GetDriverByName('MEM')
    rasterImage = driver.Create("", width_px, height_px, 3, gdal.GDT_Byte)
    rasterImage.SetGeoTransform((x_min, pixelSizeX, 0, y_max, 0, -pixelSizeY))
    rasterImage.GetRasterBand(1).SetNoDataValue(1000)

    return rasterImage


def getBoundsOverMultipleCharts(fileData):
    bounds = []

    for file in fileData:
        [x_min, x_max, y_min, y_max] = getFileBounds(file)

        if len(bounds) == 0:
            bounds = [x_min, x_max, y_min, y_max]
        else:
            bounds[0] = min(bounds[0], x_min)
            bounds[1] = max(bounds[1], x_max)
            bounds[2] = min(bounds[2], y_min)
            bounds[3] = max(bounds[3], y_max)

    return bounds


def parseCharts(chartNames):
    files = [openFile(chartName) for chartName in chartNames]
    bounds = getBoundsOverMultipleCharts(files)
    width_px = 1000
    rasterImage = createRasterImage(bounds, width_px)

    for file in files:
        parseSingleChart(file, rasterImage)

    imageChannels = rasterImage.ReadAsArray()
    cv2Image = numpy.dstack((imageChannels[2], imageChannels[1], imageChannels[0]))
    rasterImage = None

    cv2.imshow("A", cv2Image)
    cv2.waitKey()


if __name__ == '__main__':
    parseCharts(["US5MA28M"])
    # parseCharts(["US4MA14M", "US4MA43M"])
    # parseCharts(["US5MA20M", "US5MA21M", "US5MA25M", "US5MA26M", "US5MA27M", "US5MA28M", "US5MA29M", "US5MA33M"])
