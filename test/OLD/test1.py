#!/usr/bin/env python3

"""
test script that prints out all the features from a NOAA chart
"""

from osgeo import ogr


def openFile(chartName) -> ogr.DataSource:
    return ogr.Open("Charts/{0}/{0}.000".format(chartName))


def parseFeature(feat: ogr.Feature):
    print('   FEAT:' + str(feat.GetFID()))

    print(feat.geometry())


if __name__ == '__main__':
    file = openFile("US5MA28M")

    for i in range(file.GetLayerCount()):
        layer = file.GetLayerByIndex(i)
        desc = layer.GetDescription()

        print(i, layer.GetDescription())

        # try:
        #     desc = layer.GetDescription()
        #     Nfeat = layer.GetFeatureCount()
        #     print("Found %d features in layer %s" % (Nfeat, desc))
        #
        #     for j in range(Nfeat):
        #         feat = layer.GetNextFeature()
        #         #parseFeature(feat)
        #
        # except:
        #     print("Error on layer " + str(i))
