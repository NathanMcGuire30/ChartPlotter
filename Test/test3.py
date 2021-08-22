#!/usr/bin/env python3

"""
"""

from osgeo import gdal

from osgeo import ogr


class MapDraw():
    def __init__(self):
        self.datum = [None, None]

    def addPolygon(self, data):
        pass

    def export(self):
        pass


def openFile() -> ogr.DataSource:
    return ogr.Open("../Charts/a/ENC_ROOT/a/a.000")


def parseFeature(feat: ogr.Feature):
    if "polygon" in str(feat.geometry()).lower():
        # print('   FEAT:' + str(feat.GetFID()))
        print(feat.geometry())
        parseGeometry(feat.geometry())


def parseGeometry(geo: ogr.Geometry):
    # print(geo.Value())
    print("HI")


if __name__ == '__main__':
    file = openFile()

    for i in [1]:  # range(file.GetLayerCount())
        print(i)
        layer = file.GetLayerByIndex(i)

        desc = layer.GetDescription()
        Nfeat = layer.GetFeatureCount()
        print("Found %d features in layer %s" % (Nfeat, desc))

        for j in range(Nfeat):
            feat = layer.GetNextFeature()
            parseFeature(feat)
