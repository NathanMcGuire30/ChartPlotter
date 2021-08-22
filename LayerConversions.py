#!/usr/bin/env python3

"""
Uses osgeo rasterize function to turn vector charts into raster ones
"""

from osgeo import gdal
from osgeo import ogr

RASTERIZE_COLOR_FIELD = "__color__"

# Colors are BGR
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
DK_GREY = [50, 50, 50]
LAND_GREEN = [200, 226, 235]
MARSH_GREEN = [175, 209, 193]


def rasterizeSingleLayer(layer: ogr.Layer, rasterImage: gdal.Dataset):
    description = layer.GetDescription()

    if description == "LNDARE":
        singleColor(layer, rasterImage, LAND_GREEN)
    elif description == "LNDRGN":
        singleColor(layer, rasterImage, MARSH_GREEN)
    elif description == "DEPCNT":
        singleColor(layer, rasterImage, BLACK)
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

    # Unused ones
    # elif description == "OBSTRN":
    #     singleColor(layer, rasterImage, DK_GREY)


def singleColor(layer, rasterImage, color):
    source_srs = layer.GetSpatialRef()

    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(RASTERIZE_COLOR_FIELD, ogr.OFTReal)
    layer.CreateField(field_def)

    # Color stuff
    # layer_def = layer.GetLayerDefn()
    # field_index = layer_def.GetFieldIndex(RASTERIZE_COLOR_FIELD)
    # for feature in layer:
    #     feature.SetField(field_index, color)
    #     layer.SetFeature(feature)

    if source_srs:  # Make the target raster have the same projection as the source
        rasterImage.SetProjection(source_srs.ExportToWkt())
    else:  # Source has no projection (needs GDAL >= 1.7.0 to work)
        rasterImage.SetProjection('LOCAL_CS["arbitrary"]')

    # Rasterize
    err = gdal.RasterizeLayer(rasterImage, (3, 2, 1), layer, burn_values=color)
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)

    rasterImage.GetRasterBand(1).SetNoDataValue(10000)
    rasterImage.FlushCache()
