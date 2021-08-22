#!/usr/bin/env python3

"""
Test script that prints out all the features from a NOAA chart
"""

from osgeo import ogr


def openFile() -> ogr.DataSource:
    return ogr.Open("Charts/US5MA28M/ENC_ROOT/US5MA28M/US5MA28M.000")


def parseFeature(feat: ogr.Feature):
    print('   FEAT:' + str(feat.GetFID()))
    print(feat.geometry())


if __name__ == '__main__':
    file = openFile()

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
