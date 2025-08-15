#!/usr/bin/env python3

"""
ChartPlotter

A configurable system for drawing charts
"""

import navpy

from .chart_layers.noaa_layer import NOAALayer
from .utility.conversions import getImageHeightFromWidth


class ChartPlotter(object):
    def __init__(self, noaa_chart_directory=None):
        self.layer_objects = {
            "NOAA": NOAALayer(chart_dir=noaa_chart_directory)
        }

        self.layers = ["NOAA"]

    def plotChartPixels(self, lower_left, width, height, pixels_per_meter):
        """
        Plots chart based on the lower left corner and image size
        """

        width_meters = width / pixels_per_meter
        height_meters = height / pixels_per_meter
        upper_right = navpy.ned2lla((height_meters, width_meters, 0), lower_left[0], lower_left[1], 0)

        return self.plotChartByWidth(lower_left, [upper_right[0], upper_right[1]], width)

    def plotChartByWidth(self, lower_left, upper_right, width_px):
        height_px = getImageHeightFromWidth([lower_left[1], upper_right[1], lower_left[0], upper_right[0]], width_px)
        return self.plotChart(lower_left, upper_right, width_px, height_px)

    def plotChart(self, lower_left, upper_right, width_px, height_px):
        for layer in self.layers:
            image = self.layer_objects[layer].plotChart(lower_left, upper_right, width_px, height_px)

        return image

    def getPossibleLayers(self):
        return self.layer_objects.keys()

    def getLayer(self, name):
        if name in self.layer_objects:
            return self.layer_objects[name]
        else:
            return None

    def setLayers(self, layers):
        self.layers = layers
