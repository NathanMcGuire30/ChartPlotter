#!usr/bin/python3

import threading

import cv2
import imutils

from PyQt5 import QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QTabWidget, QGridLayout, QLabel

from ChartPlotter import ChartPlotter


class MapWidget(QLabel):
    def __init__(self, QWidget=None):
        super(MapWidget, self).__init__(QWidget)

    def updateImage(self, image):
        image = imutils.resize(image, width=int(self.width()))

        convertToQtFormat = QtGui.QImage(image.data, image.shape[1], image.shape[0], QtGui.QImage.Format_ARGB32)
        convertToQtFormat = QtGui.QPixmap.fromImage(convertToQtFormat)
        pixmap = QPixmap(convertToQtFormat)
        self.setPixmap(pixmap)


class MapGUI(threading.Thread):
    def __init__(self):
        self.appWindow = None

        self.chartPlotter = ChartPlotter()
        self.image = self.chartPlotter.plotChartPixels([41.51663, -70.6988197], 2000, 1000, 0.5)

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

        self.mapWidget = MapWidget(tab1)
        layout = QGridLayout()
        layout.addWidget(self.mapWidget)
        tab1.setLayout(layout)

        self.mapWidget.updateImage(self.image)

        # QTimer to run the update method
        timer = QTimer()
        timer.timeout.connect(self.updateGUI)
        timer.start(10)

        self.app.setCentralWidget(tabHolderWidget)
        self.app.show()

        self.appWindow.exec_()

    def updateGUI(self):
        self.app.update()
        self.mapWidget.updateImage(self.image)


if __name__ == '__main__':
    a = MapGUI()
    while True:
        pass
