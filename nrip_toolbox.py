import arcpy
from arcpy import env
from arcpy.sa import *
import os


class nrip_toolbox:

    def __init__(self):
        pass
 
    #### GEOMETRIC ANALYSIS ####

    # Zonal Statistics
    def zonal_statistics(self, in_zone_data, zone_field, in_value_raster, outRasterPath, statistics_type = 'MEAN'):
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

    # Summarise Within
    def summarize_within(self, in_polygons, in_sum_features, out_feature_class, keep_all_polygons='KEEP_ALL', sum_fields='Sum'):
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

    # Calculate Proximity
    def calculate_proximity(self, inSourceData, maxDistance, cellSize, outDirectionRaster):
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

    # Calculate Hotspots
    def calculate_hotspots(self, in_features, masking_polygon, out_raster_path, population_field = None):                                      
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

    # Buffer Vector
    def buffer_vector(self, in_features, out_feature_class, buffer_distance_or_field):
        """Buffers vector features by specified distance.
        
        Inputs:
            in_features : str
            out_feature_class : str
            buffer_distance_or_field : float
            
        Returns:
            None
        """

        arcpy.analysis.Buffer(in_features, out_feature_class, buffer_distance_or_field)

    # Intersection 
    def intersection(self, in_features, out_feature_class):
        """Intersect
            
        Inputs:
                in_features : str
                out_feature_class : str
        
        Return: 
                None
        """
        arcpy.Intersect_analysis(in_features, out_feature_class)

    #### GEOMORPHOLOGICAL ANALYSIS ####

    # Calculate Slope
    def calculate_slope(self, ElevationRaster):
        """Create slope raster.
        
        Inputs:
            ElevationRaster : raster
        Returns:
            outSlope : raster

        """
        outSlope = Slope(ElevationRaster)
        return outSlope

    # Calculate Aspect
    def calculate_aspect(self, ElevationRaster):
        """Create aspect raster.
        
        Inputs:
            ElevationRaster : raster
        Returns:
            outAspect : raster

        """
        outAspect = Aspect(ElevationRaster)
        return outAspect
    
    # Steep Areas
    def steep_areas(self, ElevationRaster, threshold=20, out_raster_features=None, out_polygon_features=None):
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

    #### Hydrological Analysis ####

    def calculate_fill(self, inSurfaceRaster, zLimit=None):
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
    
    # Calculate Flow Direction
    def calculate_flow_direction(self, inFillRaster):
        """Calculates flow direction raster.
        
        Inputs:
            inFillRaster : raster 
            
        Return:
            outFlowDirection : raster
        """
        
        outFlowDirection = FlowDirection(inFillRaster, "NORMAL")
        return outFlowDirection

    # Calculate Flow Accumulation
    def calculate_flow_accumulation(self, inFlowDirection):
        """Calculates flow accumulation raster.
        
        Inputs:
            inFlowDirection : raster 
            
        Return:
            outFlowAccumulation : raster
        """
            
        outFlowAccumulation = FlowAccumulation(inFlowDirection)
        return outFlowAccumulation

    # Calculate Flow Direction
    def calculate_flow_network(self, inFlowAccumulation, flow_acc_threshold):
        """Calculates flow network raster.
        
        Inputs:
            inFlowAccumulation : raster 
            flow_acc_threshold : float
            
        Return:
            outFlowAccumulationNetwork : raster
        """
            
        outFlowAccumulationNetwork = SetNull(inFlowAccumulation < flow_acc_threshold, 1)
        return outFlowAccumulationNetwork

    # Complete Hydrological Routine
    def complete_hydrological_routine(self, inSurfaceRaster, gdb_folder_path, gdb_name, out_filename_root=None, flow_acc_threshold=1000):
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

    #### INUNDATION ANALYSIS ####

    # Inundation Extents
    def inundation_extents(self, ElevationRaster, list_thresholds=[0,5,10,15], out_raster_root_path=None, out_polygon_root_path=None, decimal_places=3):
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
        
        multiplier = 10**decimal_places
        ElevationRasterInt = Int(ElevationRaster * multiplier)

        for i, th in enumerate(list_thresholds):
        
        #     if i==0:
        #         outRaster=set_null_above(ElevationRasterInt,th*multiplier)
        #         if out_raster_root_path is not None:
        #             outRaster.save(f"{out_raster_root_path}_below_{str(th).replace('.','p')}")
        #         if out_polygon_root_path is not None:
        #             out_polygon_features = f"{out_polygon_root_path}_below_{str(th).replace('.','p')}"
        #             arcpy.conversion.RasterToPolygon(outRaster, out_polygon_features)

            if i<len(list_thresholds)-1:
                low_th = th
                high_th = list_thresholds[i+1]
                outRaster = set_null_between(ElevationRasterInt, low_th*multiplier, high_th*multiplier)
                if out_raster_root_path is not None:
                    outRaster.save(f"{out_raster_root_path}_from_{str(low_th).replace('.','p')}_to_{str(high_th).replace('.','p')}")
                if out_polygon_root_path is not None:
                    out_polygon_features = f"{out_polygon_root_path}_from_{str(low_th).replace('.','p')}_to_{str(high_th).replace('.','p')}"
                    arcpy.conversion.RasterToPolygon(outRaster, out_polygon_features)

    #### UTILS ####

    # Change First Character to Alphabetic
    def change_first_character_to_alphabetic(self, name):
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

    # Rename Feature Class if it Already Exists
    def rename_feature_class_if_already_exists(self, gdb_folder_path, gdb_name, out_feature_class):
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

    # Create Geodatabase
    def create_geodatabase(self, gdb_folder_path, gdb_name):
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

    # Reclassify Raster
    def reclassify_raster(self, in_raster, reclass_field="Value", save_raster=False, save_raster_path=None):
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

    # Set Symbology From Layer
    def set_symbology_from_layer(self, inputLayer, symbologyLayer, field, new_field_name, new_field_alias):
        """Import symbology from layer file. 
        
        Inputs:
            inputLayer : str 
            symbologyLayer : str
            field : 
            new_field_name : 
            new_field_alias :
        
        Returns: 
            None
        """
        
        # Change field name
        arcpy.management.AlterField(inputLayer, field, new_field_name, new_field_alias)

        # Apply the symbology from the symbology layer to the input layer
        arcpy.ApplySymbologyFromLayer_management(inputLayer, symbologyLayer)

    # Set Null Below
    def set_null_below(self, inRaster, th):
        """ Creates constant valued raster based on SetNull operator below threshold.
        
        Input:
            inRaster : raster
            th : float
        
        Return:
            outRaster : raster
        
        """
        outRaster = SetNull(inRaster < th, inRaster)
        
        return outRaster

    # Set Null Above
    def set_null_above(self, inRaster, th):
        """ Creates constant valued raster based on SetNull operator above threshold.
        
        Input:
            inRaster : raster
            th : float
        
        Return:
            outRaster : raster
        
        """
        outRaster = SetNull(inRaster > th, inRaster)
        
        return outRaster

    # Set Null Between
    def set_null_between(self, inRaster, low_th, high_th):
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






