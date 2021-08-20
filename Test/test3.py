#!/usr/bin/env python3

"""
"""

from osgeo import gdal

from osgeo import ogr


class MapDraw():
    def __init__(self):
        pass

    def addPolygon(self, data):
        pass

    def export(self):
        pass


def openFile() -> ogr.DataSource:
    return ogr.Open("../Charts/US5MA28M/ENC_ROOT/US5MA28M/US5MA28M.000")


def parseFeature(feat: ogr.Feature):
    print('   FEAT:' + str(feat.GetFID()))
    print(feat.geometry())


if __name__ == '__main__':
    file = openFile()

    for i in range(file.GetLayerCount()):
        print(i)
        layer = file.GetLayerByIndex(i)

        try:
            desc = layer.GetDescription()
            Nfeat = layer.GetFeatureCount()
            print("Found %d features in layer %s" % (Nfeat, desc))

            for j in range(Nfeat):
                feat = layer.GetNextFeature()
                parseFeature(feat)

        except:
            print("Error on layer " + str(i))
