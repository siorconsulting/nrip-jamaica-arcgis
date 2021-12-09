import arcpy
from arcpy import env
from arcpy.sa import *

__all__ = ['zonal_statistics',
           'summarize_within',
           'calculate_proximity',
           'calculate_hotspots',
           'buffer_vector', # Update Dissolve Optional Paramater
           'intersect', # NOT TESTED
          ]

def zonal_statistics(in_zone_data, zone_field, in_value_raster, outRasterPath, statistics_type = 'MEAN'):
    """Calculates zonal statistics
    
    Inputs:
        in_zone_data : raster or feature layer
        zone_field : field (str)
        in_value_raster : raster
        statistics_type : str
        outRasterPath.: str
    
    Return:
        None 
    """
    
    outRaster = ZonalStatistics(in_zone_data, zone_field, in_value_raster, statistics_type = statistics_type)
    outRaster.save(outRasterPath)
    

def summarize_within(in_polygons, in_sum_features, out_feature_class, keep_all_polygons='KEEP_ALL', sum_fields='Sum'):
    """Calculates summarize within and exports to a feature class.
    
    Inputs:
        in_polygons : str
        in_sum_features : str
        out_feature_class : str
        keep_all_polygons : str ['Sum', 'Mean', 'Min', 'Max', 'Stddev']
        sum_fields : str
    
    Return:
        None
    """
  
    arcpy.SummarizeWithin_analysis(in_polygons, in_sum_features, out_feature_class, 
                                   keep_all_polygons = keep_all_polygons, 
                                   sum_fields = sum_fields, 
                                   )
    
def calculate_proximity(inSourceData, maxDistance, cellSize, outDirectionRaster):
    """Calculates proximity based on Euclidean distance
    
    Inputs:
        inSourceData : raster
        maxDistance : float
        cellSize : float
        outDirectionRaster : raster
        
    Return:
        outEucDistance : raster   
    """
    outEucDistance = EucDistance(inSourceData, maxDistance, cellSize, outDirectionRaster)
    return outEucDistance

def calculate_hotspots(in_features, masking_polygon, out_raster_path, population_field = None):                                      
    """Calculates hotspots based on a layer of points using a kernel function to fit a smoothly tapered surface.
    
    Inputs:
           in_features : str
           masking_polygon : str
           out_raster_path : str
           population_field[optional] : str <-- field used for kernel density calculation, default is none
    
    Outputs: 
           out_raster_path : raster
   
    Return: 
           None
    """
           
    outKernelDensity = KernelDensity(in_features, population_field, cell_size = 500)
    
    outExtractByMask = ExtractByMask(outKernelDensity, masking_polygon)
    outExtractByMask.save(f'{gdb_folder_path}\\{gdb_name}\\{out_filename_root}_Hotspot')
    
    array = arcpy.RasterToNumPyArray(outExtractByMask)

    p = [np.percentile(array, q) for q in [0,20,40,60,80,100]]
    
        
    outReclass = Reclassify(outExtractByMask, "Value", 
                         RemapRange([[p[0],p[1],1],
                                     [p[1],p[2],2],
                                     [p[2],p[3],3],
                                     [p[3],p[4],4],
                                     [p[4],p[5],5],
                                    ])
                           )
    outReclass.save(out_raster_path)

def buffer_vector(in_features, out_feature_class, buffer_distance_or_field):
    """Buffers vector features by specified distance.
    
    Inputs:
           in_features : str
           out_feature_class : str
           buffer_distance_or_field : float
           
    Returns:
           None
    """

    arcpy.analysis.Buffer(in_features, out_feature_class, buffer_distance_or_field)

def intersection(in_features, out_feature_class):
    """Intersect
        
    Inputs:
            in_features : str
            out_feature_class : str
    
    Return: 
            None
    """
    arcpy.Intersect_analysis(in_features, out_feature_class)
    

if __name__ == '__main__':
    
    # Define paths
    gdb_folder_path = 'INSERT_GDB_FOLDER_PATH'
    gdb_name = 'INSERT_GDB_NAME'

    # Create geodatabase
    create_geodatabase(gdb_folder_path, gdb_name)

    # Define filename root
    out_filename_root = 'INSERT_FILENAME_ROOT'
