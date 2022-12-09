#!/usr/bin/env python3

"""
Test code for ChartPlotter
"""


class LayerCore(object):
    def __init__(self):
        self.data_source_names = []

    def plotChart(self, lower_left, upper_right, width_px):
        """Plots chart based on lat-lon coordinates"""
        return None

    def getDataSourceNames(self):
        return self.data_source_names