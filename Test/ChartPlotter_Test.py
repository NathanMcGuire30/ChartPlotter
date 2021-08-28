#!/usr/bin/env python3

"""
Test code for ChartPlotter
"""

import cv2

from ChartPlotter import ChartPlotter

if __name__ == '__main__':
    chartPlotter = ChartPlotter()
    a = chartPlotter.plotChartMeters([41.51663, -70.6988197], 2000, 1000, 0.5)

    cv2.imshow("Output", a)
    cv2.waitKey()
