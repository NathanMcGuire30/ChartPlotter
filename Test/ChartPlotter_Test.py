#!/usr/bin/env python3

"""
Test code for ChartPlotter
"""

import cv2

from ChartPlotter import ChartPlotter

if __name__ == '__main__':
    chart_plotter = ChartPlotter()
    # a = chart_plotter.plotChartPixels([41.51663, -70.6988197], 2000, 1000, 0.5)
    a = chart_plotter.plotChart([41.51663, -70.6988197], [41.532422, -70.635176], 1000)

    cv2.imshow("Output", a)
    cv2.waitKey()
