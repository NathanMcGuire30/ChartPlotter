import navpy


def boxDimensions(bounds):
    [lon_min, lon_max, lat_min, lat_max] = bounds

    ned = navpy.lla2ned(lat_max, lon_max, 0, lat_min, lon_min, 0)
    n = ned[0]
    e = ned[1]

    return [e, n]


def getImageHeightFromWidth(bounds, width_px):
    # Figure out the pixel size and stuff for everything
    [x_length_meters, y_length_meters] = boxDimensions(bounds)  # Convert to x and y size
    pixels_per_meter = float(width_px) / float(x_length_meters)  # Figure out how tall the image should be based on how wide it is
    height_px = int(y_length_meters * pixels_per_meter)

    return height_px
