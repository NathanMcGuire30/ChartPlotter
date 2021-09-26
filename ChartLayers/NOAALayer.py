#!/usr/bin/env python3

"""
Uses osgeo rasterize function to turn NOAA vector charts into png images
"""

import os
import numpy
import navpy

from shapely.geometry import Polygon
from dataclasses import dataclass
from osgeo import gdal
from osgeo import ogr

from ChartLayers.LayerCore import LayerCore


@dataclass
class ChartInfo(object):
    name: str
    chartData: ogr.DataSource
    coverage: list


class NOAALayer(LayerCore):
    def __init__(self):
        super(NOAALayer, self).__init__()
        rootDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chartDir = os.path.join(rootDir, "Charts", "NOAA")

        # Gets list of all the directories in Charts/NOAA
        self.dataSourceNames = next(os.walk(chartDir))[1]

        # Loop through and figure out bounds
        self.files = {}
        for file in self.dataSourceNames:
            chartPath = os.path.join(chartDir, "{0}".format(file), "{0}.000".format(file))
            self.files[file] = ChartInfo(name=file, chartData=ogr.Open(chartPath), coverage=[])
            self.files[file].coverage = self.getDataRegion(file)

        # TODO: MASKS

    def getNeededCharts(self, lowerLeft, upperRight):
        chartList = []
        p1 = Polygon([(lowerLeft[1], lowerLeft[0]), (lowerLeft[1], upperRight[0]), (upperRight[1], upperRight[0]), (upperRight[1], lowerLeft[0])])

        for file in self.files:
            coverage = self.files[file].coverage
            for polygon in coverage:
                p2 = Polygon(polygon)
                if p1.intersects(p2):
                    if file not in chartList:
                        chartList.append(file)

        return chartList

    def plotChart(self, lowerLeft, upperRight, width_px):
        bounds = [lowerLeft[1], upperRight[1], lowerLeft[0], upperRight[0]]
        rasterImage = createRasterImage(bounds, width_px)
        chartList = self.getNeededCharts(lowerLeft, upperRight)  # Only rasterize the charts we need

        for file in chartList:
            chart = self.files[file].chartData
            parseSingleChart(chart, rasterImage)

        imageChannels = rasterImage.ReadAsArray()
        cv2Image = numpy.dstack((imageChannels[2], imageChannels[1], imageChannels[0]))
        rasterImage = None

        return cv2Image

    def plotWholeChart(self, chartNames, width_px):
        chartsToUse = {}
        for name in chartNames:
            if name in self.files:
                chartsToUse[name] = self.files[name].chartData
            else:
                return

        bounds = getBoundsOverMultipleCharts(chartsToUse.values())
        rasterImage = createRasterImage(bounds, width_px)

        for file in chartsToUse:
            parseSingleChart(chartsToUse[file], rasterImage)

        imageChannels = rasterImage.ReadAsArray()
        cv2Image = numpy.dstack((imageChannels[2], imageChannels[1], imageChannels[0]))
        rasterImage = None

        return cv2Image

    def getDataRegion(self, file):
        dataSet = self.files[file].chartData
        coverageLayerIndex = -1
        coverageList = []

        for coverageLayerIndex in range(dataSet.GetLayerCount()):
            layer = dataSet.GetLayerByIndex(coverageLayerIndex)
            if layer.GetDescription() == "M_COVR":
                break

        layer = dataSet.GetLayerByIndex(coverageLayerIndex)
        Nfeat = layer.GetFeatureCount()
        for j in range(Nfeat - 1):  # The last feature is the full rectangle bounding box
            pointsList = []

            feat = layer.GetNextFeature()
            geom = feat.GetGeometryRef()
            ring = geom.GetGeometryRef(0)
            points = ring.GetPointCount()
            for p in range(points):
                lon, lat, z = ring.GetPoint(p)
                pointsList.append((lon, lat))

            coverageList.append(pointsList)

        return coverageList


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


"""NOAA LAYER CONVERSIONS"""

RASTERIZE_COLOR_FIELD = "__color__"
MIN_DEPTH_KEY = "DRVAL1"
MAX_DEPTH_KEY = "DRVAL2"

# Colors are RGB
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
DK_GREY = [50, 50, 50]
LAND_GREEN = [226, 235, 200]
MARSH_GREEN = [209, 193, 175]
SHALLOW_WATER = [216, 240, 245]
OBSTRUCTION = [100, 150, 150]


def appendToList(outList, layerDictionary, key):
    if key in layerDictionary:
        outList.append(layerDictionary[key])


def sortLayers(file: ogr.DataSource):
    # 7: Buoys
    # 13: Towers on rocks in woods hole
    # 41: Depth soundings
    # Coverage: M_COVR

    layerDictionary = {}

    for i in range(file.GetLayerCount()):
        layer = file.GetLayerByIndex(i)
        desc = layer.GetDescription()
        layerDictionary[desc] = i

    outList = []  # Put things into the right order
    appendToList(outList, layerDictionary, "LNDARE")
    appendToList(outList, layerDictionary, "LAKARE")
    appendToList(outList, layerDictionary, "LNDRGN")
    appendToList(outList, layerDictionary, "BUISGL")
    appendToList(outList, layerDictionary, "RIVERS")
    appendToList(outList, layerDictionary, "BRIDGE")
    appendToList(outList, layerDictionary, "DEPARE")
    appendToList(outList, layerDictionary, "DEPCNT")
    appendToList(outList, layerDictionary, "OBSTRN")
    appendToList(outList, layerDictionary, "FAIRWY")
    appendToList(outList, layerDictionary, "DRGARE")
    appendToList(outList, layerDictionary, "COALNE")
    appendToList(outList, layerDictionary, "SLCONS")
    appendToList(outList, layerDictionary, "UWTROC")
    appendToList(outList, layerDictionary, "NAVLNE")
    appendToList(outList, layerDictionary, "PIPSOL")
    appendToList(outList, layerDictionary, "PONTON")
    appendToList(outList, layerDictionary, "RECTRC")
    appendToList(outList, layerDictionary, "SBDARE")
    appendToList(outList, layerDictionary, "WRECKS")

    return outList


def rasterizeSingleLayer(layer: ogr.Layer, rasterImage: gdal.Dataset):
    description = layer.GetDescription()

    if description == "LNDARE":
        singleColor(layer, rasterImage, LAND_GREEN)
    elif description == "LNDRGN":
        singleColor(layer, rasterImage, MARSH_GREEN)
    elif description == "DEPCNT":
        singleColor(layer, rasterImage, BLACK)
    elif description == "DEPARE":
        depthLayer(layer, rasterImage, SHALLOW_WATER)
    elif description == "FAIRWY":
        singleColor(layer, rasterImage, WHITE)
    elif description == "DRGARE":
        singleColor(layer, rasterImage, WHITE)
    elif description == "BUISGL":
        singleColor(layer, rasterImage, BLACK)
    elif description == "BRIDGE":
        singleColor(layer, rasterImage, BLACK)
    elif description == "COALNE":
        singleColor(layer, rasterImage, BLACK)
    elif description == "SLCONS":
        singleColor(layer, rasterImage, BLACK)
    elif description == "UWTROC":
        singleColor(layer, rasterImage, BLACK)
    elif description == "OBSTRN":
        singleColor(layer, rasterImage, OBSTRUCTION)
    elif description == "LAKARE":
        singleColor(layer, rasterImage, SHALLOW_WATER)
    elif description == "PIPSOL":
        singleColor(layer, rasterImage, BLACK)
    elif description == "PONTON":
        singleColor(layer, rasterImage, BLACK)
    elif description == "RECTRC":
        singleColor(layer, rasterImage, BLACK)
    elif description == "RIVERS":
        singleColor(layer, rasterImage, SHALLOW_WATER)
    # elif description == "SBDARE":
    # singleColor(layer, rasterImage, MARSH_GREEN)
    elif description == "WRECKS":
        singleColor(layer, rasterImage, SHALLOW_WATER)

    # UNUSED
    # elif description == "NAVLNE":
    # singleColor(layer, rasterImage, BLACK)


def singleColor(layer, rasterImage, color):
    source_srs = layer.GetSpatialRef()
    if source_srs:  # Make the target raster have the same projection as the source
        rasterImage.SetProjection(source_srs.ExportToWkt())
    else:  # Source has no projection (needs GDAL >= 1.7.0 to work)
        rasterImage.SetProjection('LOCAL_CS["arbitrary"]')

    # Rasterize
    err = gdal.RasterizeLayer(rasterImage, (1, 2, 3), layer, burn_values=color)
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)


def depthLayer(layer: ogr.Layer, rasterImage: gdal.Dataset, shallowColor):
    # TODO: Scale depth cutoff

    # Make temp place to store deep water areas, so we can rasterize them white
    source = ogr.GetDriverByName('MEMORY').CreateDataSource('memData')
    deepLayer = source.CreateLayer("DEEP", layer.GetSpatialRef())

    for i in range(layer.GetFeatureCount()):
        feature = layer.GetNextFeature()
        minDepth = float(feature.GetField(MIN_DEPTH_KEY))
        maxDepth = float(feature.GetField(MAX_DEPTH_KEY))
        depth = (minDepth + maxDepth) / 2

        if depth > 3:
            deepLayer.SetFeature(feature)
            layer.DeleteFeature(feature.GetFID())

    # Rasterize
    err = gdal.RasterizeLayer(rasterImage, (1, 2, 3), layer, burn_values=shallowColor)
    err1 = gdal.RasterizeLayer(rasterImage, (1, 2, 3), deepLayer, burn_values=WHITE)
    if err != 0 or err1 != 0:
        raise Exception("error rasterizing layer: %s" % err)
