import pandas as pd
import numpy as np
import math
from specklepy.objects.geometry import Base
from specklepy.objects.other import RenderMaterial
from specklepy.transports.server import ServerTransport
from specklepy.api import operations

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(PROJECT_ROOT)

from Geometry.geometry import Sphere

class ColumnOffsetEvaluation():

    def Run(commit_data,
            column_parameter : str = '@Tragwerksstützen',
            tolerance : float = 0.01,
            commit_message : str = "Stützenversätze",
            scale_spheres : bool = True):
        
        '''
            commit_data (specklepy.objects.base.Base): commit_data object obtained using Commit.getData() from the bg_specklepy library
            column_parameter (str): String representing the revit parameter used to described columns
            tolerance (float): Calculated distances of the offsets (in the x-y plane) larger than the tolerance will be deemed as an offset column
            commit_message (str): Message commited to the branch
        '''

        column_elements = commit_data[column_parameter]
        df = pd.DataFrame()
        vertices = []

        for column in column_elements:
            
            keys, values = [], []
            
            for var in vars(column):
                
                if var == "baseLine":

                    p1 = column.baseLine.start
                    p2 = column.baseLine.end
                    
                    keys.extend(["obj_u", "x_u", "y_u", "z_u", "obj_o", "x_o", "y_o", "z_o"])
                    values.extend([p1, p1.x, p1.y, p1.z, p2, p2.x, p2.y, p2.z])
                
                else:
                    keys.append(var)
                    values.append(getattr(column, var))
            
            vertices.append(dict(zip(keys, values)))

        df = df.append(vertices)

        df["x_sort"] = df["x_u"].apply(np.floor)
        df["y_sort"] = df["y_u"].apply(np.floor)
        df["z_sort"] = df["z_u"].apply(np.floor)

        df = df.round({'x_u': 2, 'y_u': 2, 'z_u' : 2, 'x_o': 2, 'y_o': 2, 'z_o' : 2})
        df.sort_values(["x_sort", "y_sort", "z_sort"], ascending = [True, True, True], inplace = True)
        df.reset_index(inplace=True)

        offset_column_indices = []
        offset = []

        for index, row in df.iterrows():
            
            if row["isSlanted"] == True:
                raise Exception("Slanted columns not yet implemented.")
            
            else:
                if index == len(df.index) - 1:
                    continue
                    
                elif row["z_o"] <= df.iloc[index + 1]["z_u"]:
                    delta_x = row["x_o"] - df.iloc[index + 1]["x_u"]
                    delta_y = row["y_o"] - df.iloc[index + 1]["y_u"]
                    
                    srss = math.sqrt(delta_x**2 + delta_y**2)
                    
                    if srss > tolerance:
                        offset_column_indices.append(index + 1)
                        offset.append(round(srss, 3))
                        
        offset_df = df.iloc[offset_column_indices].copy(deep=True)
        offset_df["offset"] = offset

        commit_object = Base()
        commit_object["@Stützenversätze"] = []

        for index, row in offset_df.iterrows():
            
            obj = Base(speckle_type = "ColumnOffsetSphere")
            
            radius = 0.5
            if scale_spheres:
                radius = min(1, row["offset"])
            
            mesh = Sphere.Create(radius = radius, center = [row["x_u"], row["y_u"], row["z_u"]])

            obj["displayValue"] = mesh
            obj["displayValue"]["renderMaterial"] = RenderMaterial(opacity = 0.5, diffuse = 16711680, emissive = 16711680)

            for variable in offset_df.columns:
                if variable in ["applicationId", "offset", "elementID", "id", "type", "family", "category"]:
                    obj[variable] = row[variable]
                else:
                    continue
            
            commit_object["@Stützenversätze"].append(obj)
        
        commit_data["@Stützenversätze"] = commit_object
    
        transport = ServerTransport(client = commit_data.client_obj, stream_id = commit_data.stream_id)
        obj_id = operations.send(base=commit_data, transports=[transport])
        commit_data.client_obj.commit.create(stream_id = commit_data.stream_id, object_id = obj_id, message = commit_message)

        print("Successfully commited to branch.")
    