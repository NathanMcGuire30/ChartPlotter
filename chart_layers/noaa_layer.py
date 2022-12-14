#!/usr/bin/env python3

"""
Uses osgeo rasterize function to turn NOAA vector charts into png images
"""

import os
from typing import List

import numpy
from collections import OrderedDict

import osgeo.gdal
from shapely.geometry import Polygon
from dataclasses import dataclass
from osgeo import gdal, ogr, osr

from chart_layers.layer_core import LayerCore
from utility.conversions import getImageHeightFromWidth


@dataclass
class ChartInfo(object):
    name: str
    chartData: ogr.DataSource
    coverage: list


class NOAALayer(LayerCore):
    def __init__(self):
        super(NOAALayer, self).__init__()
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        chart_dir = os.path.join(root_dir, "charts", "noaa")

        # Gets list of all the directories in charts/noaa
        self.dataSourceNames = next(os.walk(chart_dir))[1]

        # Colors are RGB
        self.color_palette = {"BLACK": [0, 0, 0],
                              "WHITE": [255, 255, 255],
                              "DK_GREY": [50, 50, 50],
                              "LAND_GREEN": [226, 235, 200],
                              "MARSH_GREEN": [209, 193, 175],
                              "SHALLOW_WATER": [216, 240, 245],
                              "OBSTRUCTION": [100, 150, 150],
                              }

        # Layer to palette mapping and layer order
        self.layer_colors = OrderedDict({"LNDARE": "LAND_GREEN",
                                         "LAKARE": "SHALLOW_WATER",
                                         "LNDRGN": "MARSH_GREEN",
                                         "BUISGL": "BLACK",
                                         "RIVERS": "SHALLOW_WATER",
                                         "BRIDGE": "BLACK",
                                         "DEPARE": "SHALLOW_WATER",
                                         "DEPCNT": "BLACK",
                                         "OBSTRN": "OBSTRUCTION",
                                         "FAIRWY": "WHITE",
                                         "DRGARE": "WHITE",
                                         "COALNE": "BLACK",
                                         "SLCONS": "BLACK",
                                         "UWTROC": "BLACK",
                                         "NAVLNE": None,
                                         "PIPSOL": "BLACK",
                                         "PONTON": "BLACK",
                                         "RECTRC": "BLACK",
                                         "SBDARE": None,  # Marshy areas or something
                                         "WRECKS": "SHALLOW_WATER",
                                         "BOYLAT": None,  # Buoys
                                         })

        self.shallow_water_depth = 5  # Depth in meters for water to be considered "shallow"

        self.tif_reproject = False
        self.tif_name = ""
        self.tif_projection = ""
        self.tif_bounds = [None, None]

        # Loop through and figure out bounds
        self.files = {}
        for file in self.dataSourceNames:
            chart_path = os.path.join(chart_dir, "{0}".format(file), "{0}.000".format(file))
            self.files[file] = ChartInfo(name=file, chartData=ogr.Open(chart_path), coverage=[])
            self.files[file].coverage = self.getDataRegion(file)

        # TODO: MASKS

    def setColorPalette(self, new_palette):
        self.color_palette.update(new_palette)

    def setLayerColors(self, new_layer_colors):
        self.layer_colors.update(new_layer_colors)

    def removeLayers(self, layers_to_remove: List[str]):
        for layer in layers_to_remove:
            if layer in self.layer_colors:
                del self.layer_colors[layer]

    def setShallowWaterDepth(self, new_depth):
        self.shallow_water_depth = new_depth

    def enableTifReproject(self, tif_projection: str, file_name: str = "test.tif"):
        self.tif_reproject = True
        self.tif_name = file_name
        self.tif_projection = tif_projection

    def getNeededCharts(self, lower_left, upper_right):
        chart_list = []
        p1 = Polygon([(lower_left[1], lower_left[0]), (lower_left[1], upper_right[0]), (upper_right[1], upper_right[0]), (upper_right[1], lower_left[0])])

        for file in self.files:
            coverage = self.files[file].coverage
            for polygon in coverage:
                p2 = Polygon(polygon)
                if p1.intersects(p2):
                    if file not in chart_list:
                        chart_list.append(file)

        return chart_list

    def plotChart(self, lower_left, upper_right, width_px, height_px):
        bounds = [lower_left[1], upper_right[1], lower_left[0], upper_right[0]]
        raster_image = createRasterImage(bounds, width_px, height_px)
        chart_list = self.getNeededCharts(lower_left, upper_right)  # Only rasterize the charts we need

        # Set raster image to have the same projection as the origional chart

        chart_coordinate_system = self.files[chart_list[0]].chartData.GetLayer(1).GetSpatialRef()
        raster_image.SetProjection(chart_coordinate_system.ExportToWkt())

        # Go through each chart and its data to the raster image
        for file in chart_list:
            chart = self.files[file].chartData
            self.parseSingleChart(chart, raster_image)

        if self.tif_reproject:
            # This is a hack, but it seems to work
            # The only way I could get anything to re-project was to save it out as another file type
            a = gdal.Warp(self.tif_name, raster_image, dstSRS=self.tif_projection)
            a = None  # Apparently you have to do this to properly free memory

            # https://gis.stackexchange.com/questions/104362/how-to-get-extent-out-of-geotiff
            test = gdal.Open(self.tif_name)
            geo_transform = test.GetGeoTransform()
            min_x = geo_transform[0]
            max_y = geo_transform[3]
            max_x = min_x + geo_transform[1] * test.RasterXSize
            min_y = max_y + geo_transform[5] * test.RasterYSize

            lower_left = [min_x, min_y]
            upper_right = [max_x, max_y]
            self.tif_bounds = [lower_left, upper_right]
            image_channels = test.ReadAsArray()
        else:
            image_channels = raster_image.ReadAsArray()

        cv2_image = numpy.dstack((image_channels[2], image_channels[1], image_channels[0]))
        raster_image = None

        return cv2_image

    def plotWholeChart(self, chart_names, width_px):
        charts_to_use = {}
        for name in chart_names:
            if name in self.files:
                charts_to_use[name] = self.files[name].chartData
            else:
                return

        bounds = getBoundsOverMultipleCharts(charts_to_use.values())
        raster_image = createRasterImageByWidth(bounds, width_px)

        for file in charts_to_use:
            self.parseSingleChart(charts_to_use[file], raster_image)

        image_channels = raster_image.ReadAsArray()
        cv2_image = numpy.dstack((image_channels[2], image_channels[1], image_channels[0]))
        raster_image = None

        return cv2_image

    def getDataRegion(self, file):
        data_set = self.files[file].chartData
        coverage_layer_index = -1
        coverage_list = []

        for coverage_layer_index in range(data_set.GetLayerCount()):
            layer = data_set.GetLayerByIndex(coverage_layer_index)
            if layer.GetDescription() == "M_COVR":
                break

        layer = data_set.GetLayerByIndex(coverage_layer_index)
        nfeat = layer.GetFeatureCount()
        for j in range(nfeat):  # The last feature is the full rectangle bounding box
            points_list = []

            feat = layer.GetNextFeature()
            geom = feat.GetGeometryRef()
            ring = geom.GetGeometryRef(0)
            points = ring.GetPointCount()
            for p in range(points):
                lon, lat, z = ring.GetPoint(p)
                points_list.append((lon, lat))

            coverage_list.append(points_list)

        return coverage_list

    def parseSingleChart(self, file, raster_image):
        # Make a copy of the file so we can modify stuff
        vector_source = ogr.GetDriverByName("Memory").CopyDataSource(file, "")

        sorted_layers = self.getSortedLayerNames(file)

        for layerNumber in sorted_layers:
            try:
                layer = vector_source.GetLayer(layerNumber)
                self.rasterizeSingleLayer(layer, raster_image)
            except Exception as e:
                print(e)

    def rasterizeSingleLayer(self, layer: ogr.Layer, raster_image: gdal.Dataset):
        description = layer.GetDescription()

        if description == "DEPARE":
            depthLayer(layer, raster_image, self.color_palette["SHALLOW_WATER"], self.color_palette["WHITE"], self.shallow_water_depth)
        elif description in self.layer_colors:
            color_choice = self.layer_colors[description]
            if color_choice in self.color_palette:
                singleColor(layer, raster_image, self.color_palette[color_choice])

    def getSortedLayerNames(self, file: ogr.DataSource):
        # Coverage: M_COVR

        layer_dictionary = {}
        out_list = []

        for i in range(file.GetLayerCount()):
            layer = file.GetLayerByIndex(i)
            desc = layer.GetDescription()
            layer_dictionary[desc] = i

        for key in self.layer_colors.keys():
            if key in layer_dictionary:
                out_list.append(layer_dictionary[key])

        return out_list


def getFileBounds(file_data):
    bounds = []

    for i in range(file_data.GetLayerCount()):
        layer = file_data.GetLayer(i)
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


def createRasterImageByWidth(bounds, width_px):
    height_px = getImageHeightFromWidth(bounds, width_px)
    return createRasterImage(bounds, width_px, height_px)


def createRasterImage(bounds, width_px, height_px) -> osgeo.gdal.Dataset:
    [longitude_min, longitude_max, latitude_min, latitude_max] = bounds
    pixel_size_x = (longitude_max - longitude_min) / width_px  # Figure out pixel size in lat and lon
    pixel_size_y = (latitude_max - latitude_min) / height_px

    driver = gdal.GetDriverByName('MEM')
    raster_image = driver.Create("", width_px, height_px, 3, gdal.GDT_Byte)
    raster_image.SetGeoTransform((longitude_min, pixel_size_x, 0, latitude_max, 0, -pixel_size_y))
    raster_image.GetRasterBand(1).SetNoDataValue(1000)

    return raster_image


def getBoundsOverMultipleCharts(file_data):
    bounds = []

    for file in file_data:
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


def singleColor(layer, raster_image, color):
    # Rasterize
    err = gdal.RasterizeLayer(raster_image, (1, 2, 3), layer, burn_values=color)
    if err != 0:
        raise Exception("error rasterizing layer: %s" % err)


def depthLayer(layer: ogr.Layer, raster_image: gdal.Dataset, shallow_color, deep_color, depth_cutoff):
    # TODO: Scale depth cutoff

    # Make temp place to store deep water areas, so we can rasterize them white
    source = ogr.GetDriverByName('MEMORY').CreateDataSource('memData')
    deep_layer = source.CreateLayer("DEEP", layer.GetSpatialRef())

    for i in range(layer.GetFeatureCount()):
        feature = layer.GetNextFeature()
        min_depth = float(feature.GetField(MIN_DEPTH_KEY))  # Depths are in METERS!

        if min_depth > depth_cutoff:
            deep_layer.SetFeature(feature)
            layer.DeleteFeature(feature.GetFID())

    # Rasterize
    err = gdal.RasterizeLayer(raster_image, (1, 2, 3), layer, burn_values=shallow_color)
    err1 = gdal.RasterizeLayer(raster_image, (1, 2, 3), deep_layer, burn_values=deep_color)
    if err != 0 or err1 != 0:
        raise Exception("error rasterizing layer: %s" % err)
