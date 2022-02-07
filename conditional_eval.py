import arcpy
from arcpy import env
from arcpy.sa import *

__all__ = ['set_null_between',
           'set_null_below',
           'set_null_above'
          ]

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
