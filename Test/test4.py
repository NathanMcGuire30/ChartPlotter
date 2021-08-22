#!/usr/bin/env python3

"""
Uses osgeo rasterize function to turn vector charts into raster ones
"""

import random
import navpy

from osgeo import gdal
from osgeo import ogr

RASTERIZE_COLOR_FIELD = "__color__"


def openFile() -> ogr.DataSource:
    return ogr.Open("../Charts/US5MA28M/ENC_ROOT/US5MA28M/US5MA28M.000")


def boxDimensions(bounds):
    [lon_min, lon_max, lat_min, lat_max] = bounds

    ned = navpy.lla2ned(lat_max, lon_max, 0, lat_min, lon_min, 0)
    n = ned[0]
    e = ned[1]

    return [e, n]


def rasterizeSingleLayer(orig_data_source, layer, bounds, width=1000):
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")
    source_layer = source_ds.GetLayer(layer)
    source_srs = source_layer.GetSpatialRef()

    # Create a field in the source layer to hold the features colors
    field_def = ogr.FieldDefn(RASTERIZE_COLOR_FIELD, ogr.OFTReal)
    source_layer.CreateField(field_def)
    source_layer_def = source_layer.GetLayerDefn()
    field_index = source_layer_def.GetFieldIndex(RASTERIZE_COLOR_FIELD)

    # Generate random values for the color field (it's here that the value
    # of the attribute should be used, but you get the idea)
    for feature in source_layer:
        feature.SetField(field_index, random.randint(0, 255))
        source_layer.SetFeature(feature)

    # Figure out the pixel size and stuff for everything
    [x_min, x_max, y_min, y_max] = bounds  # These are lat and lon values (x is lon, y is lat)
    [xLengthMeters, yLengthMeters] = boxDimensions(bounds)  # Convert to x and y size
    pixelsPerMeter = float(width) / float(xLengthMeters)  # Figure out how tall the image should be based on how wide it is
    height = int(yLengthMeters * pixelsPerMeter)
    pixelSizeX = (x_max - x_min) / width  # Figure out pixel size in lat and lon
    pixelSizeY = (y_max - y_min) / height

    target_ds = gdal.GetDriverByName('GTiff').Create('Output/test{}.tif'.format(layer), width, height, 3, gdal.GDT_Byte)
    target_ds.SetGeoTransform((x_min, pixelSizeX, 0, y_max, 0, -pixelSizeY))

    if source_srs:
        # Make the target raster have the same projection as the source
        target_ds.SetProjection(source_srs.ExportToWkt())
    else:
        # Source has no projection (needs GDAL >= 1.7.0 to work)
        target_ds.SetProjection('LOCAL_CS["arbitrary"]')

    # Rasterize
    err = gdal.RasterizeLayer(target_ds, (3, 2, 1), source_layer, burn_values=(0, 0, 0), options=["ATTRIBUTE=%s" % RASTERIZE_COLOR_FIELD])
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)

    target_ds.GetRasterBand(1).SetNoDataValue(10000)
    target_ds.FlushCache()


def getFileBounds(fileData):
    bounds = []

    for i in range(fileData.GetLayerCount()):
        source_layer = fileData.GetLayer(i)
        x_min, x_max, y_min, y_max = source_layer.GetExtent()
        if abs(x_min - x_max) > 0.000001 and abs(y_min - y_max) > 0.000001:  # Some layers are very small, so we don't care about them
            if len(bounds) == 0:
                bounds = [x_min, x_max, y_min, y_max]
            else:
                bounds[0] = min(bounds[0], x_min)
                bounds[1] = min(bounds[1], x_max)
                bounds[2] = min(bounds[2], y_min)
                bounds[3] = min(bounds[3], y_max)

    return bounds


if __name__ == '__main__':
    print("Start")
    file = openFile()
    bounds = getFileBounds(file)
    print("Raster")

    for i in range(file.GetLayerCount()):
        try:
            rasterizeSingleLayer(file, i, bounds, width=2000)
        except Exception as e:
            print(e)

    print("DONE")
