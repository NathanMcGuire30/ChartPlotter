#!/usr/bin/env python3

"""
ChartPlotter

A configurable system for drawing charts
"""

import navpy

from ChartLayers.NOAALayer import NOAALayer


class ChartPlotter(object):
    def __init__(self):
        self.layerObjects = {
            "NOAA": NOAALayer()
        }

        self.layers = ["NOAA"]

    def plotChartPixels(self, lowerLeft, width, height, pixelsPerMeter):
        """Plots chart based on the lower left corner and image size"""
        widthMeters = width / pixelsPerMeter
        heightMeters = height / pixelsPerMeter
        upperRight = navpy.ned2lla((heightMeters, widthMeters, 0), lowerLeft[0], lowerLeft[1], 0)

        return self.plotChart(lowerLeft, [upperRight[0], upperRight[1]], width)

    def plotChart(self, lowerLeft, upperRight, width_px):
        for layer in self.layers:
            image = self.layerObjects[layer].plotChart(lowerLeft, upperRight, width_px)

        return image

    def getPossibleLayers(self):
        return self.layerObjects.keys()

    def setLayers(self, layers):
        self.layers = layers
