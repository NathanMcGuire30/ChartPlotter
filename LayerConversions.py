#!/usr/bin/env python3

"""
Uses osgeo rasterize function to turn vector charts into raster ones
"""

from osgeo import gdal
from osgeo import ogr

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


def depthLayer(layer, rasterImage, shallowColor):
    for i in range(layer.GetFeatureCount()):
        feature = layer.GetNextFeature()
        minDepth = float(feature.GetField(MIN_DEPTH_KEY))
        maxDepth = float(feature.GetField(MAX_DEPTH_KEY))
        depth = (minDepth + maxDepth) / 2

        if depth > 3:
            layer.DeleteFeature(feature.GetFID())

    # Rasterize
    err = gdal.RasterizeLayer(rasterImage, (1, 2, 3), layer, burn_values=shallowColor)
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)
