import os
import sys
import pandas as pd
import numpy as np
import math
from specklepy.objects.geometry import Base
from specklepy.objects.other import RenderMaterial
from specklepy.transports.server import ServerTransport
from specklepy.api import operations
from specklepy.objects.units import Units

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(PROJECT_ROOT)

from Geometry.sphere import Sphere
from SpeckleServer.commit import Commit
import dependencies

class ColumnOffsetEvaluation():

    '''
    A general placeholder for methods pertaining to a column offset evaluation.
    '''

    def run(commit_data,
            echo_level : int = 0,
            column_parameter : str = '@Tragwerksstützen',
            tolerance : float = 0.01,
            append_spheres_to_received_commit : bool = True,
            commit_message : str = "Stützenversätze",
            scale_spheres : bool = True):

        '''
        Perform a column offset evaluation on a commit_data.

        Args:
            commit_data (specklepy.objects.base.Base): commit_data object obtained using Commit.getData() from the bg_specklepy library
            echo_level (int): Default of 0 - no updates printed to console. 1 - updates printed to console.
            column_parameter (str): String representing the revit parameter used to described columns
            tolerance (float, m): Calculated distances of the offsets (in the x-y plane) larger than the tolerance will be deemed as an offset column
            append_spheres_to_received_commit (bool): When False, only spheres are commited. When True, spheres are calculated and pushed back WITH all original commit data
            commit_message (str): Message commited to the branch
            scale_spheres (bool): When False, sphere radius is set to offset distance (radius limited to a maximum of 1 m). When True, sphere radius set to 0.5 m
        '''

        client_obj = commit_data.client_obj
        stream_id = commit_data.stream_id

        # HACKY - muss einen besseren Weg geben?
        if not "Revit" in commit_data[dir(commit_data)[0]][0].speckle_type:
            raise Exception("Column offset evaluation currently restricted to Revit models only.")

        if echo_level == 1:
            print("[UPDATE]\t:\tRevit model detected ...")

        if commit_data.speckle_type != "Objects.Organization.Model":
            raise Exception("Commit data not of correct speckle type. A Revit Model needs to be used as basis input.")

        if commit_data.units != Units.m:
            print("[WARNING]\t:\tModel assumed to be in metres. Should commited model not be defined in m, double-check outputs.")

        try:
            commit_data[column_parameter]

        except KeyError:
            print("[WARNING]\t:\tGiven column_parameter given is not found in the model. Parameter should be one of the following:")
            for parameter in dir(commit_data):
                if parameter[0] == "@":
                    print("\t\t\t\t-", parameter)
            sys.exit(1)

        else:
            column_elements = commit_data[column_parameter]

        df = pd.DataFrame()
        vertices = []

        if echo_level == 1:
            print("[UPDATE]\t:\tBuilding column database ...")

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

        df = pd.concat([df, pd.DataFrame(vertices)], axis = 1)
        
        df["x_sort"] = df["x_u"].apply(np.floor)
        df["y_sort"] = df["y_u"].apply(np.floor)
        df["z_sort"] = df["z_u"].apply(np.floor)

        df = df.round({'x_u': 2, 'y_u': 2, 'z_u' : 2, 'x_o': 2, 'y_o': 2, 'z_o' : 2})
        df.sort_values(["x_sort", "y_sort", "z_sort"], ascending = [True, True, True],
                       inplace = True)
        df.reset_index(inplace=True)

        offset_column_indices = []
        offset = []

        if echo_level == 1:
            print("[UPDATE]\t:\tFinding offset columns in accordance with tolerance criterion ...")

        for index, row in df.iterrows():

            if row["isSlanted"]:
                raise Exception("Slanted columns not yet implemented.")

            else:
                if index == len(df.index) - 1:
                    continue

                if row["z_o"] <= df.iloc[index + 1]["z_u"]:
                    delta_x = row["x_o"] - df.iloc[index + 1]["x_u"]
                    delta_y = row["y_o"] - df.iloc[index + 1]["y_u"]

                    srss = math.sqrt(delta_x**2 + delta_y**2)

                    if srss > tolerance:
                        offset_column_indices.append(index + 1)
                        offset.append(srss)

        if echo_level == 1:
            print("[UPDATE]\t:\t{} offset columns found ...".format(str(len(offset))))

        offset_df = df.iloc[offset_column_indices].copy(deep=True)
        offset_df["offset"] = offset
        offset_df = offset_df.round({'offset': 3})

        if echo_level == 1:
            print("[UPDATE]\t:\tGenerating sphere objects for visualization ...")

        commit_object = Base()
        commit_object["@Stützenversätze"] = []

        for index, row in offset_df.iterrows():

            obj = Base(speckle_type = "ColumnOffsetSphere")

            radius = 0.5
            if scale_spheres:
                radius = min(1, row["offset"])

            mesh = Sphere.create(radius = radius, center = [row["x_u"], row["y_u"], row["z_u"]])

            obj["displayValue"] = mesh
            obj["displayValue"]["renderMaterial"] = RenderMaterial(opacity = 0.5,
                                                                   diffuse = 16711680,
                                                                   emissive = 16711680)

            for variable in offset_df.columns:
                if variable in ["applicationId", "offset", "elementID", "id", "type", "family", "category"]:
                    obj[variable] = row[variable]
                else:
                    continue

            commit_object["@Stützenversätze"].append(obj)

        if echo_level == 1:
            print("[UPDATE]\t:\tReady to commit ...")

        if append_spheres_to_received_commit:
            commit_data["@Stützenversätze"] = commit_object

        if not append_spheres_to_received_commit:
            commit_data = commit_object

        if echo_level == 1:
            print("[UPDATE]\t:\tPushing commit ...")

        Commit.send_data(client_obj, stream_id, commit_data, commit_message)

        if echo_level == 1:
            print("[UPDATE]\t:\tFinished! :) ")

    # !! ToDo - Für spätere Entwicklung: Die Funktionen weiter unterteilen
    # def _check_commit_quality():
    # def _build_dataframe():
    # def _find_offset_columns():
    # def _generate_spheres():
    # def _commit_data():
    