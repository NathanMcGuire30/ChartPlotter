#!/usr/bin/env python3

"""
ChartPlotter

A configurable system for drawing charts
"""

import navpy

from ChartLayers.NOAALayer import NOAALayer


class ChartPlotter(object):
    def __init__(self):
        self.layer_objects = {
            "NOAA": NOAALayer()
        }

        self.layers = ["NOAA"]

    def plotChartPixels(self, lower_left, width, height, pixels_per_meter):
        """Plots chart based on the lower left corner and image size"""
        width_meters = width / pixels_per_meter
        height_meters = height / pixels_per_meter
        upper_right = navpy.ned2lla((height_meters, width_meters, 0), lower_left[0], lower_left[1], 0)

        return self.plotChart(lower_left, [upper_right[0], upper_right[1]], width)

    def plotChart(self, lower_left, upper_right, width_px):
        for layer in self.layers:
            image = self.layer_objects[layer].plotChart(lower_left, upper_right, width_px)

        return image

    def getPossibleLayers(self):
        return self.layer_objects.keys()

    def setLayers(self, layers):
        self.layers = layers
