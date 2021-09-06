#!/usr/bin/env python3

"""
Test code for ChartPlotter
"""

import cv2
import numpy
import numpy as np

from ChartPlotter import ChartPlotter

if __name__ == '__main__':
    chartPlotter = ChartPlotter()

    globalLowerLeft = [41.519489, -70.7288717]
    globalLowerRight = [41.550559, -70.6228197]

    boxes = 8
    boxWidth = 100

    latitudes = numpy.linspace(globalLowerLeft[0], globalLowerRight[0], boxes + 1)
    longitudes = numpy.linspace(globalLowerLeft[1], globalLowerRight[1], boxes + 1)

    image = None
    padding = boxes

    for i in range(len(latitudes) - 1):
        for j in range(len(longitudes) - 1):
            print("{0} of {1}".format(i * boxes + j + 1, boxes * boxes))

            lowerLeft = (latitudes[i], longitudes[j])
            upperRight = (latitudes[i + 1], longitudes[j + 1])
            im = chartPlotter.plotChart(lowerLeft, upperRight, boxWidth)

            [imHeight, imWidth, _] = im.shape

            if image is None:
                image = np.zeros([imHeight * boxes + padding, imWidth * boxes + 1, 3], dtype=np.uint8)

            startRow = (imHeight * boxes) - (imHeight * i) - 1 + padding
            startColumn = imWidth * j

            image[startRow - imHeight:startRow, startColumn:startColumn + imWidth, 0:2] = im[:, :, 0:2]

            cv2.imshow("Output", image)
            cv2.waitKey(1)

    cv2.imwrite("Output.png", image)
    cv2.imshow("Output", image)
    cv2.waitKey(3000)
