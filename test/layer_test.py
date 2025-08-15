import cv2

from chart_plotter.chart_layers.noaa_layer import NOAALayer


def plotAndShowChart(noaa_layer_object, chart_names, width_px):
    image = noaa_layer_object.plotWholeChart(chart_names, width_px)

    if image is not None:
        cv2.imshow("A", image)
        cv2.waitKey()
    else:
        print("Could not plot chart: {}".format(chart_names))


if __name__ == '__main__':
    NOAALayer = NOAALayer()
    all_charts = NOAALayer.getDataSourceNames()
    # plotAndShowChart(NOAALayer, ["US5MA1EJ"], 1000)
    # plotAndShowChart(NOAALayer, all_charts, 2000)
    # plotAndShowChart(NOAALayer, ["US5MA20M", "US5MA21M", "US5MA25M", "US5MA26M", "US5MA27M", "US5MA28M", "US5MA29M", "US5MA33M"], 1000)

    for chart in NOAALayer.getDataSourceNames():
        plotAndShowChart(NOAALayer, [chart], 1000)
