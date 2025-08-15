#!/usr/bin/env python3

"""
Script to take NOAA chart and spit out an STL that gazebo will use

Uses this half-baked library I wrote a while ago to actually parse the chart
https://github.com/NathanMcGuire30/ChartPlotter
"""

import cv2
from chart_plotter.chart_layers.noaa_layer import NOAALayer


def main():
    ll = [41.510172, -70.695575]
    ur = [41.539469, -70.644350]

    noaa_layer = NOAALayer()
    # print(noaa_layer.getDataSourceNames())
    # a = noaa_layer.plotChart(ll, ur, 1000, 1000)
    # cv2.imshow("Output", a)
    # cv2.waitKey()

    s = noaa_layer.getShapesFromLayers(ll, ur, ["LNDARE", "SOUNDG"])
    for layer in s:
        print(layer)
        features = s[layer]
        for feature in features:
            print(f"  {feature}")


if __name__ == '__main__':
    main()
