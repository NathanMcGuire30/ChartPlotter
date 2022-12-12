#!/usr/bin/env python3

"""
Test code for ChartPlotter
"""

import cv2
import numpy
import numpy as np

from chart_plotter import ChartPlotter

if __name__ == '__main__':
    chartPlotter = ChartPlotter()

    globalLowerLeft = [41.519489, -70.7288717]
    globalUpperRight = [41.550559, -70.6228197]

    boxes = 8
    boxWidth = 200

    latitudes = numpy.linspace(globalUpperRight[0], globalLowerLeft[0], boxes + 1)
    longitudes = numpy.linspace(globalLowerLeft[1], globalUpperRight[1], boxes + 1)

    image = None

    for i in range(len(latitudes) - 1):
        for j in range(len(longitudes) - 1):
            print("{0} of {1}".format(i * boxes + j + 1, boxes * boxes))

            lowerLeft = (latitudes[i + 1], longitudes[j])
            upperRight = (latitudes[i], longitudes[j + 1])
            im = chartPlotter.plotChart(lowerLeft, upperRight, boxWidth)

            [imHeight, imWidth, _] = im.shape

            if image is None:
                image = np.zeros([imHeight, imWidth, 3], dtype=np.uint8)

            startRow = (imHeight * i)
            endRow = startRow + imHeight
            startColumn = imWidth * j
            endColumn = startColumn + imWidth

            [rows, columns, _] = image.shape
            if rows < endRow:
                extraRows = endRow - rows
                extraImage = np.zeros([extraRows, columns, 3], dtype=np.uint8)
                image = np.concatenate([image, extraImage], axis=0)
            if columns < endColumn:
                extraColumns = endColumn - columns
                extraImage = np.zeros([rows, extraColumns, 3], dtype=np.uint8)
                image = np.concatenate([image, extraImage], axis=1)

            image[startRow:endRow, startColumn:endColumn, 0:2] = im[:, :, 0:2]

            cv2.imshow("Output", image)
            cv2.waitKey(1)

    cv2.imwrite("Output.png", image)
    cv2.imshow("Output", image)
    cv2.waitKey(3000)
