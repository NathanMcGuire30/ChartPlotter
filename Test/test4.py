#!/usr/bin/env python3

"""
Uses osgeo rasterize function
"""

from osgeo import gdal

from osgeo import ogr

import random

RASTERIZE_COLOR_FIELD = "__color__"


def openFile() -> ogr.DataSource:
    return ogr.Open("../Charts/US5MA28M/ENC_ROOT/US5MA28M/US5MA28M.000")


def rasterize(orig_data_source, layer, pixel_size=25):
    # Make a copy of the layer's data source because we'll need to
    # modify its attributes table
    source_ds = ogr.GetDriverByName("Memory").CopyDataSource(orig_data_source, "")

    source_layer = source_ds.GetLayer(layer)
    source_srs = source_layer.GetSpatialRef()
    # print(source_srs)

    x_min, x_max, y_min, y_max = source_layer.GetExtent()
    print(x_min, x_max, y_min, y_max)

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
    # Create the destination data source
    x_res = int((x_max - x_min) / pixel_size)
    y_res = int((y_max - y_min) / pixel_size)
    target_ds = gdal.GetDriverByName('GTiff').Create('test{}.tif'.format(layer), 1000, 1000, 3, gdal.GDT_Byte)

    target_ds.SetGeoTransform((0, pixel_size, 0, 1000, 0, -pixel_size))

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


if __name__ == '__main__':
    file = openFile()

    for i in range(file.GetLayerCount()):
        rasterize(file, i)
