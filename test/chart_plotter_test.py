#!/usr/bin/env python3

"""
test code for ChartPlotter
"""

import cv2

from chart_plotter import ChartPlotter

if __name__ == '__main__':
    chart_plotter = ChartPlotter()
    a = chart_plotter.plotChartPixels([41.51663, -70.6988197], 2000, 1000, 0.5)
    # a = chart_plotter.plotChartByWidth([39.347425, -71.046112], [41.552179, -70.070582], 500)

    cv2.imwrite("../example_images/chart_plotter_test.png", a)
    cv2.imshow("Output", a)
    cv2.waitKey()

