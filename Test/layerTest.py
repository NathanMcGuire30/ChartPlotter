import cv2

from ChartLayers.NOAALayer import NOAALayer


def plotAndShowChart(NOAALayerObject, chartNames, width_px):
    image = NOAALayerObject.plotWholeChart(chartNames, width_px)

    if image is not None:
        cv2.imshow("A", image)
        cv2.waitKey()
    else:
        print("Could not plot chart: {}".format(chartNames))


if __name__ == '__main__':
    NOAALayer = NOAALayer()
    plotAndShowChart(NOAALayer, ["US5MA28M"], 1000)
    plotAndShowChart(NOAALayer, ["US4MA14M", "US4MA43M"], 1000)
    plotAndShowChart(NOAALayer, ["US5MA20M", "US5MA21M", "US5MA25M", "US5MA26M", "US5MA27M", "US5MA28M", "US5MA29M", "US5MA33M"], 1000)
