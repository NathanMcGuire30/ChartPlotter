#!/usr/bin/env python3

"""
test code for ChartPlotter
"""


class LayerCore(object):
    def __init__(self):
        self.data_source_names = []

    def plotChart(self, lower_left, upper_right, width_px, height_pixels):
        """Plots chart based on lat-lon coordinates"""
        return None

    def getDataSourceNames(self):
        return self.data_source_names