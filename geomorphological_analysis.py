import arcpy
from arcpy.sa import *

def calculate_slope(ElevationRaster):
    """Create slope raster.
    
    Inputs:
        ElevationRaster : raster
    Returns:
        outSlope : raster

    """
    outSlope = Slope(ElevationRaster)
    return outSlope


def calculate_aspect(ElevationRaster):
    """Create aspect raster.
    
    Inputs:
        ElevationRaster : raster
    Returns:
        outAspect : raster

    """
    outAspect = Aspect(ElevationRaster)
    return outAspect

def steep_areas(ElevationRaster, threshold=20, out_raster_features=None, out_polygon_features=None):
    '''Create mask of areas with slope equal or higher than a threshold.

    Inputs:
        ElevationRaster : raster
    Returns:
        steepAreas : raster
    Outputs:
        out_raster_features [optional] : raster
        out_polygon_features [optional] : vector <-- output polygon

    '''
    outSlope = Slope(ElevationRaster)
    steepAreas = SetNull(outSlope < threshold, 1)
    if out_raster_features is not None:
        steepAreas.save(out_raster_features)
    if out_polygon_features is not None:
        arcpy.conversion.RasterToPolygon(steepAreas, out_polygon_features)
        arcpy.management.Dissolve(out_polygon_features, out_polygon_features+'_dissolve')
    return steepAreas
    
