#!/usr/bin/env python3

"""
Test code for ChartPlotter
"""

import time
import cv2
import numpy
import numpy as np

from ChartPlotter import ChartPlotter

if __name__ == '__main__':
    chartPlotter = ChartPlotter()

    globalLowerLeft = [41.519489, -70.7288717]
    globalLowerRight = [41.550559, -70.6228197]

    boxes = 6

    latitudes = numpy.linspace(globalLowerLeft[0], globalLowerRight[0], boxes + 1)
    longitudes = numpy.linspace(globalLowerLeft[1], globalLowerRight[1], boxes + 1)

    image = None

    for i in range(len(latitudes) - 1):
        row = None

        for j in range(len(longitudes) - 1):
            print("{0} of {1}".format(i * boxes + j + 1, boxes * boxes))

            lowerLeft = (latitudes[i], longitudes[j])
            upperRight = (latitudes[i + 1], longitudes[j + 1])
            im = chartPlotter.plotChart(lowerLeft, upperRight, 200)

            if row is None:
                row = im
            else:
                row = numpy.concatenate((row, im), axis=1)

        if image is None:
            image = row
        else:
            image = numpy.concatenate((row, image), axis=0)

    cv2.imwrite("Output.png", image)
    cv2.imshow("Output", image)
    cv2.waitKey(3000)
