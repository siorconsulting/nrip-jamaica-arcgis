import arcpy
import os
from arcpy import env
from arcpy.sa import *


__all__ = ['change_first_character_to_alphabetic',
           'rename_feature_class_if_already_exists',
           'create_geodatabase',
           'reclassify_raster',
           'set_symbology_from_layer', # NOT TESTED
           'set_null_above',
           'set_null_below',
           'set_null_between'
          ]

def change_first_character_to_alphabetic(name):
    """Adds AA_ prefix to a string if its first character is not alphabetic
    
    Inputs:
        name : string
        
    Returns:
        name : string
    """
    if not(name[0].isalpha()):
        return 'AA_' + name
    else:
        return name

def rename_feature_class_if_already_exists(gdb_folder_path, gdb_name, out_feature_class):
    """Adds numeric suffix to a feature class name if this already exists in the specified geodatabase
    
    Inputs:
        gdb_folder_path : str
        gdb_name : str
        out_feature_class : str
        
    Returns:
        out_feature_clas : str
    """
    if not(arcpy.Exists(os.path.join(gdb_folder_path,gdb_name,out_feature_class))):
        return out_feature_class
    
    else:
        new_out_feature_class = out_feature_class + '_1'
    
        i = 1
        while arcpy.Exists(os.path.join(gdb_folder_path,gdb_name,new_out_feature_class)):
            i = i + 1
            new_out_feature_class = out_feature_class + f'_{i}'
    
        return new_out_feature_class
    
def create_geodatabase(gdb_folder_path, gdb_name):
    """Creates a new file geodabatase at the specified location and, if needed, overwrites the existing one.
    
    Inputs:
        gdb_folder_path : str
        gdb_name : str
        
    Returns:
        None
        
    """
    arcpy.management.Delete(os.path.join(gdb_folder_path,gdb_name))
    arcpy.management.CreateFileGDB(gdb_folder_path, gdb_name)
     
    return print("geodatabase successfully created")

def reclassify_raster(in_raster, reclass_field="Value", save_raster=False, save_raster_path=None):
    """Reclassify raster values.
    
    Inputs:
           in_raster : raster
           reclass_field : 
           save_raster :
           save_raster_path : 
    
    Returns:
           None
    """
    
    array = arcpy.RasterToNumPyArray(in_raster)

    p = [np.percentile(array, q) for q in [0,20,40,60,80,100]]
    
    outReclass = Reclassify(in_raster, reclass_field, 
                            RemapRange([[p[0],p[1],1],
                                        [p[1],p[2],2],
                                        [p[2],p[3],3],
                                        [p[3],p[4],4],
                                        [p[4],p[5],5],
                                       ]))
                           
    if save_raster:
        outReclass.save(save_raster_path)
    
    return outReclass

def set_symbology_from_layer(inputLayer, symbologyLayer):
    """Import symbology from layer
    
    Inputs:
    
    Returns: 
           None
    """
    
    # Apply the symbology from the symbology layer to the input layer
    arcpy.ApplySymbologyFromLayer_management(inputLayer, symbologyLayer)
                            
def set_null_below(inRaster, th):
  """ Creates constant valued raster based on SetNull operator below threshold.
  
  Input:
      inRaster : raster
      th : float
  
  Return:
      outRaster : raster
  
  """
  outRaster = SetNull(inRaster < th, inRaster)
  
  return outRaster

def set_null_above(inRaster, th):
  """ Creates constant valued raster based on SetNull operator above threshold.
  
  Input:
      inRaster : raster
      th : float
  
  Return:
      outRaster : raster
  
  """
  outRaster = SetNull(inRaster > th, inRaster)
  
  return outRaster

def set_null_between(inRaster, low_th, high_th):
  """ Creates constant valued raster based on two SetNull operations.
  
  Input:
      inRaster : raster
      low_th : float
      high_th : float
  
  Return:
      outRaster : raster
  
  """
         
  lowRaster = SetNull(inRaster > high_th, inRaster)
  outRaster = SetNull(lowRaster < low_th, 1)
  
  return outRaster
