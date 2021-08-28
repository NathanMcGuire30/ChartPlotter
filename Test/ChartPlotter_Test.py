#!/usr/bin/env python3

"""
Test code for ChartPlotter
"""

from ChartPlotter import ChartPlotter

if __name__ == '__main__':
    chartPlotter = ChartPlotter()
    chartPlotter.plotChartMeters([41.51663, -70.6988197], 2000, 1000, 0.5)
