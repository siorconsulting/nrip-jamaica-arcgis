import arcpy
from arcpy import env
from arcpy.sa import *
from utils import *

__all__ = ['inundation_extents']

def inundation_extents(ElevationRaster, list_thresholds=[0,5,10,15], out_raster_root_path=None, out_polygon_root_path=None, decimal_places=3):
    """ Creates a set of inundation extents based on elevation thresholds and exports them as polygons and/or rasters.

    Inputs:
        ElevationRaster L raster
        list_thresholds [optional] : list
        out_raster_tool_path [optional] : str
        out_polygon_root_path [optional] L str
        decimal_places [optional] : int
    
    Returns:
        None

    """
    
    multiplier = 10^decimal_places
    ElevationRasterInt = Int(ElevationRaster * multiplier)

    for i, th in enumerate(list_thresholds):
        if i==0:

            outRaster=set_null_above(ElevationRasterInt,th*multiplier)
            if out_raster_root_path is not None:
                outRaster.save(f"{out_raster_root_path}_below_{str(th).replace('.','p')}")
            if out_polygon_root_path is not None:
                out_polygon_features = f"{out_polygon_root_path}_below_{str(th).replace('.','p')}"
                arcpy.conversion.RasterToPolygon(outRaster, out_polygon_features)

        if i<len(list_thresholds)-1:

            low_th = th
            high_th = list_thresholds[i+1]
            outRaster = set_null_between(ElevationRasterInt, low_th*multiplier, high_th*multiplier)
            if out_raster_root_path is not None:
                outRaster.save(f"{out_raster_root_path}_from_{str(low_th).replace('.','p')}_to_{str(high_th).replace('.','p')}")
            if out_polygon_root_path is not None:
                out_polygon_features = f"{out_polygon_root_path}_from_{str(low_th).replace('.','p')}_to_{str(high_th).replace('.','p')}"
                arcpy.conversion.RasterToPolygon(outRaster, out_polygon_features)
   



