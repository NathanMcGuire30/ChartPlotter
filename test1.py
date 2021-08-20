import numpy as np

from osgeo import ogr, gdal_array

"""
Test script that prints out all the features from a NOAA chart
"""


def openFile() -> ogr.DataSource:
    return ogr.Open("Charts/US5MA28M/ENC_ROOT/US5MA28M/US5MA28M.000")


if __name__ == '__main__':
    file = openFile()

    for i in range(file.GetLayerCount()):
        layer = file.GetLayerByIndex(i)

        try:
            desc = layer.GetDescription()
            Nfeat = layer.GetFeatureCount()
            print("Found %d features in layer %s" % (Nfeat, desc))

            for j in range(Nfeat):
                feat = layer.GetNextFeature()
                print('   FEAT:' + str(feat.GetFID()))
                for feat_attribute in feat.keys():
                    print('       ATTR:' + feat_attribute + ':' + feat.GetFieldAsString(feat_attribute))

        except:
            print("Error on layer " + str(i))
