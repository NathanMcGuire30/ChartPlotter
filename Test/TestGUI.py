#!usr/bin/python3

import threading

import cv2
import imutils
import numpy

from PyQt5 import QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QGridLayout, QLabel

from ChartPlotter import ChartPlotter


class MapWidget(QLabel):
    def __init__(self, chartPlotter, QWidget=None):
        super(MapWidget, self).__init__(QWidget)

        self.chartPlotter = chartPlotter

        self.lat = 41.51663
        self.lon = -70.6988197
        self.pixel_per_meter = 0.5
        self.pixelOffset = [0, 0]
        self.mouseDownPos = [0, 0]

        print("A")
        self.image = self.chartPlotter.plotChartPixels([self.lat, self.lon], 2000, 1000, self.pixel_per_meter)
        print("B")

    def updateImage(self):
        image = cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR)

        imageWidth = 4 * round(int(self.width()) / 4)
        image = imutils.resize(image, width=imageWidth)
        [height, width, _] = image.shape

        section = image[0:height - self.pixelOffset[1], 0:width - self.pixelOffset[0]]
        [sectionHeight, sectionWidth, _] = section.shape

        newImage = numpy.zeros(image.shape, dtype=numpy.uint8)
        newImage[height - sectionHeight:, width - sectionWidth:] = section

        convertToQtFormat = QtGui.QImage(newImage.data, newImage.shape[1], newImage.shape[0], QtGui.QImage.Format_RGB888)
        convertToQtFormat = QtGui.QPixmap.fromImage(convertToQtFormat)
        pixmap = QPixmap(convertToQtFormat)
        self.setPixmap(pixmap)

    def mousePressEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.mouseDownPos = [self.pixelOffset[0] - ev.x(), self.pixelOffset[1] - ev.y()]

    def mouseMoveEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.pixelOffset = [ev.x() + self.mouseDownPos[0], ev.y() + self.mouseDownPos[1]]

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        print("BYE")


class MapGUI(threading.Thread):
    def __init__(self):
        self.appWindow = None

        self.chartPlotter = ChartPlotter()

        # Start the thread
        threading.Thread.__init__(self)
        self.start()

    def run(self):
        self.appWindow = QApplication([])
        self.app = QMainWindow()
        self.app.setGeometry(0, 0, 500, 500)
        self.app.setWindowTitle("Hi")

        tabHolderWidget = QTabWidget()
        tab1 = QTabWidget()
        tab2 = QWidget()
        tabHolderWidget.addTab(tab1, "Tab 1")
        tabHolderWidget.addTab(tab2, "Tab 2")

        self.mapWidget = MapWidget(self.chartPlotter, tab1)
        layout = QGridLayout()
        layout.addWidget(self.mapWidget)
        tab1.setLayout(layout)

        # QTimer to run the update method
        timer = QTimer()
        timer.timeout.connect(self.updateGUI)
        timer.start(10)

        self.app.setCentralWidget(tabHolderWidget)
        self.app.show()

        self.appWindow.exec_()

    def updateGUI(self):
        self.app.update()
        self.mapWidget.updateImage()


if __name__ == '__main__':
    a = MapGUI()
    while True:
        pass
