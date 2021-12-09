import arcpy
import os
from arcpy import env
from arcpy.sa import *
from utils import *

__all__ = ['complete_hydrological_routine',
           'calculate_fill',
           'calculate_flow_direction',
           'calculate_flow_accumulation',
           'calculate_flow_network',
          ]

def calculate_fill(inSurfaceRaster, zLimit=None):
    """Calculates filled digital elevation model raster.
    
    Inputs:
        inSurfaceRaster : raster 
        zLimit : float
        
    Return:
        outFill : raster
    """
    
    if zLimit is not None:
        outFill = Fill(inSurfaceRaster, zLimit)
    else:
        outFill = Fill(inSurfaceRaster)
        
    return outFill

    
def calculate_flow_direction(inFillRaster):
    """Calculates flow direction raster.
    
    Inputs:
        inFillRaster : raster 
        
    Return:
        outFlowDirection : raster
    """
    
    outFlowDirection = FlowDirection(inFillRaster, "NORMAL")
    return outFlowDirection

    
def calculate_flow_accumulation(inFlowDirection):
    """Calculates flow accumulation raster.
    
    Inputs:
        inFlowDirection : raster 
        
    Return:
        outFlowAccumulation : raster
    """
        
    outFlowAccumulation = FlowAccumulation(inFlowDirection)
    return outFlowAccumulation


def calculate_flow_network(inFlowAccumulation, flow_acc_threshold):
    """Calculates flow network raster.
    
    Inputs:
        inFlowAccumulation : raster 
        flow_acc_threshold : float
        
    Return:
        outFlowAccumulationNetwork : raster
    """
        
    outFlowAccumulationNetwork = SetNull(inFlowAccumulation < flow_acc_threshold, 1)
    return outFlowAccumulationNetwork


def complete_hydrological_routine(inSurfaceRaster, gdb_folder_path, gdb_name, out_filename_root=None, flow_acc_threshold=1000):
    """ Hydrological routing routine, which generates the following:

    Inputs:
        inSurfaceRaster : raster

    Outputs:
        outFill : raster
        outFlowDirection: raster
        outFlowAccumulation : raster
        outFlowAccumulationNetwork : raster
        outBasins : raster
        outFillDiff: raster
        outFillDiff : vector <-- output fill difference polygon
        outFlowAccumulationNetwork : vector <-- output flow accumulation network polygon
        outBasins : vector <-- output basins polygon

    """
    
    # Calculate fill 
    outFill = Fill(inSurfaceRaster)
    outFill.save(f'{gdb_folder_path}\\{gdb_name}\\{out_filename_root}_fill')

    # Calculate flow direction
    outFlowDirection = FlowDirection(outFill, "NORMAL")
    outFlowDirection.save(f'{gdb_folder_path}\\{gdb_name}\\{out_filename_root}_fdir')
    
    # Calculate flow acccumulation
    outFlowAccumulation = FlowAccumulation(outFlowDirection)
    outFlowAccumulation.save(f'{gdb_folder_path}\\{gdb_name}\\{out_filename_root}_facc')
    
    # Calculate flow network (raster)
    outFlowAccumulationNetwork = SetNull(outFlowAccumulation < flow_acc_threshold, 1)
    
    # Calculate basins
    outBasins = Basin(outFlowDirection)
    outBasins.save(f'{gdb_folder_path}\\{gdb_name}\\{out_filename_root}_basins')
  
    # Calculate fill - DTM Difference
    outFillDiff = SetNull((outFill - inSurfaceRaster) == 0, 1)

    # Convert fill difference raster to polygon and export
    outPolygons_filename = f'{out_filename_root}_Fill_polygons'
    outPolygons = os.path.join(gdb_folder_path,gdb_name,outPolygons_filename)
    arcpy.RasterToPolygon_conversion(outFillDiff, outPolygons, "NO_SIMPLIFY")

    # Convert flow network raster to polygon and export
    outPolygons_filename = f'{out_filename_root}_flow_network_polygons'
    outPolygons = os.path.join(gdb_folder_path,gdb_name,outPolygons_filename)
    arcpy.RasterToPolygon_conversion(outFlowAccumulationNetwork, outPolygons, "NO_SIMPLIFY")
    
    # Cnvert basins to polygon and export
    outPolygons_filename = f'{out_filename_root}_basins_polygons'
    outPolygons = os.path.join(gdb_folder_path,gdb_name,outPolygons_filename)
    arcpy.RasterToPolygon_conversion(outBasins, outPolygons, "NO_SIMPLIFY")
    

if __name__ == '__main__':
    
    # Define paths
    gdb_folder_path = 'INSERT_GDB_FOLDER_PATH'
    gdb_name = 'INSERT_GDB_NAME'

    # Create geodatabase
    create_geodatabase(gdb_folder_path, gdb_name)

    # Define filename root
    out_filename_root = 'DTM'

    # Set flow accumulation threshold
    flow_acc_threshold = 100000
