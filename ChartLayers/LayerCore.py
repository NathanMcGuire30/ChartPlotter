#!/usr/bin/env python3

"""
Test code for ChartPlotter
"""


class LayerCore(object):
    def __init__(self):
        self.dataSourceNames = []

    def plotChart(self, lowerLeft, upperRight, width_px):
        """Plots chart based on lat-lon coordinates"""
        return None

    def getDataSourceNames(self):
        return self.dataSourceNames