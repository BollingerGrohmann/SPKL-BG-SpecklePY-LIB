import os
import sys
import pandas as pd
import numpy as np
import math
from datetime import date
from specklepy.api.client import SpeckleClient
from specklepy.objects.geometry import Base
from specklepy.objects.other import RenderMaterial
from specklepy.objects.units import Units

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(PROJECT_ROOT)

from Geometry.sphere import Sphere
from SpeckleServer.commit import Commit
import dependencies

class ColumnOffsetEvaluation():

    def __init__(self,
                 commit_data,
                 echo_level : int = 0,
                 column_parameter : str = '@Tragwerksstützen',
                 tolerance : float = 0.01,
                 scale_spheres : bool = True):

        '''
        Perform a column offset evaluation on a commit_data.

        Args:
            commit_data (specklepy.objects.base.Base): commit_data object obtained using Commit.getData() from the bg_specklepy library
            echo_level (int): Default of 0 - no updates printed to console. 1 - updates printed to console.
            column_parameter (str): String representing the revit parameter used to described columns.
            tolerance (float, m): Calculated distances of the offsets (in the x-y plane) larger than the tolerance will be deemed as an offset column
            append_spheres_to_received_commit (bool): When False, only spheres are commited. When True, spheres are calculated and pushed back WITH all original commit data
            scale_spheres (bool): When False, sphere radius is set to offset distance (radius limited to a maximum of 1 m). When True, sphere radius set to 0.5 m
        '''

        self.commit_data = commit_data
        self.echo_level = echo_level
        self.column_parameter = column_parameter
        self.tolerance = tolerance
        self.append_spheres_to_received_commit = False
        self.commit_message = "[{}] analysis_column_eccentricity".format(date.today())
        self.scale_spheres = scale_spheres
        self.client_obj = commit_data.client_obj
        self.stream_obj = commit_data.stream_obj
        self.column_elements = None
        self.data_frame = None
        self.offset_columns_dataframe = None
        self.commit_object = None

    def run(self):

        '''
        Running the evaluation invokes all subprocesses and pushes results to commit.
        '''

        self._check_commit_quality()
        self._build_dataframe()
        self._find_offset_columns()
        self._generate_spheres()
        self._commit_data()

    def _check_commit_quality(self):

        '''
        Hier wollen wir ein paar Sachen überprüfen, z.B.:
            -   Muss ein Revit-Modell sein
            -   commit muss der richtige Datentyp sein
            -   "@column_parameter muss richtig eingegeben werden. ToDo wäre eine Funktion, die den Namen findet? vll. def find_revit_column_parameter(). Je nach Sprache ist unterschiedlich
            -   ToDo muss ein normales Revit-Modell sein (nicht ein Berechnungsmodell). Ein Berechnungsmodell hat Stützen ohne "baseLine" Attributen
        '''

        # HACKY - muss einen besseren Weg geben?
        if not "Revit" in self.commit_data[dir(self.commit_data)[0]][0].speckle_type:
            raise Exception("Column offset evaluation currently restricted to Revit models only.")

        if self.echo_level == 1:
            print("[UPDATE]\t:\tRevit model detected ...")

        if self.commit_data.speckle_type != "Objects.Organization.Model":
            raise Exception("Commit data not of correct speckle type. A Revit Model needs to be used as basis input.")

        if self.commit_data.units != Units.m:
            print("[WARNING]\t:\tModel assumed to be in metres. Should commited model not be defined in m, double-check outputs.")

        try:
            self.commit_data[self.column_parameter]

        except KeyError:
            print("[WARNING]\t:\tGiven column_parameter given is not found in the model. Parameter should be one of the following:")
            for parameter in dir(self.commit_data):
                if parameter[0] == "@":
                    print("\t\t\t\t-", parameter)
            sys.exit(1)

        else:
            self.column_elements = self.commit_data[self.column_parameter]

    def _build_dataframe(self):

        df = pd.DataFrame()
        vertices = []

        if self.echo_level == 1:
            print("[UPDATE]\t:\tBuilding column database ...")

        for column in self.column_elements:

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

        self.data_frame = df

    def _find_offset_columns(self):

        offset_column_indices = []

        column_below_id = []
        column_below_elementId = []
        column_below_applicationId = []

        offset_srss, offset_x, offset_y = [], [], []

        if self.echo_level == 1:
            print("[UPDATE]\t:\tFinding offset columns in accordance with tolerance criterion ...")

        for index, row in self.data_frame.iterrows():

            if row["isSlanted"]:
                raise Exception("Slanted columns not yet implemented.")

            else:
                if index == len(self.data_frame.index) - 1:
                    continue

                if row["z_o"] <= self.data_frame.iloc[index + 1]["z_u"]:
                    delta_x = row["x_o"] - self.data_frame.iloc[index + 1]["x_u"]
                    delta_y = row["y_o"] - self.data_frame.iloc[index + 1]["y_u"]

                    srss = math.sqrt(delta_x**2 + delta_y**2)

                    if srss > self.tolerance:

                        column_below_id.append(row["id"])
                        column_below_elementId.append(row["elementId"])
                        column_below_applicationId.append(row["applicationId"])

                        offset_column_indices.append(index + 1)

                        offset_srss.append(srss)
                        offset_x.append(delta_x)
                        offset_y.append(delta_y)

        if self.echo_level == 1:
            print("[UPDATE]\t:\t{} offset columns found ...".format(str(len(offset_srss))))

        offset_df = self.data_frame.iloc[offset_column_indices].copy(deep=True)

        offset_df.rename(columns={'id': 'column_above_id',
                                  'elementId': 'column_above_elementId',
                                  'applicationId': 'column_above_applicationId'},
                                  inplace=True)

        offset_df["offset_srss"] = offset_srss
        offset_df["offset_x"] = offset_x
        offset_df["offset_y"] = offset_y
        offset_df = offset_df.round({'offset_srss': 3, 'offset_x': 3, 'offset_y': 3})

        offset_df["column_below_id"] = column_below_id
        offset_df["column_below_elementId"] = column_below_elementId
        offset_df["column_below_applicationId"] = column_below_applicationId

        offset_df.to_excel("output.xlsx")
        
        self.offset_columns_dataframe = offset_df

    def _generate_spheres(self):

        if self.echo_level == 1:
            print("[UPDATE]\t:\tGenerating sphere objects for visualization ...")

        commit_object = Base()
        commit_object["@Analysis_ColumnEccentricity"] = []

        for index, row in self.offset_columns_dataframe.iterrows():

            obj = Base()

            obj["@column_above"], obj["@column_below"], obj["@offset"] = {}, {}, {}

            radius = 0.5
            if self.scale_spheres:
                radius = min(1, row["offset_srss"])

            mesh = Sphere.create(radius = radius, center = [row["x_u"], row["y_u"], row["z_u"]])

            obj["displayValue"] = mesh
            obj["displayValue"]["renderMaterial"] = RenderMaterial(opacity = 0.5,
                                                                   diffuse = 16711680,
                                                                   emissive = 16711680)

            for variable in self.offset_columns_dataframe.columns:

                if variable.startswith("column_below"):

                    if row["offset_srss"] < 1:
                        obj["@column_below"][variable.split("_")[-1]] = row[variable]
                        obj["@offset"]["Column_discontinuous"] = False

                    else:
                        obj["@column_below"][variable.split("_")[-1]] = "Column underneath missing"
                        obj["@offset"]["Column_discontinuous"] = True

                elif variable.startswith("column_above"):

                    obj["@column_above"][variable.split("_")[-1]] = row[variable]

                elif variable.startswith("offset"):

                    obj["@offset"]["_".join(["Offset", variable.split("_")[-1].upper()])] = row[variable]

            commit_object["@Analysis_ColumnEccentricity"].append(obj)

        self.commit_object = commit_object

    def _commit_data(self):

        if self.echo_level == 1:
            print("[UPDATE]\t:\tReady to commit ...")

        if self.append_spheres_to_received_commit: # Used to be parameter. Now defaults to False
            self.commit_data["@Analysis_ColumnEccentricity"] = self.commit_object

        if not self.append_spheres_to_received_commit:
            self.commit_data = self.commit_object

        if self.echo_level == 1:
            print("[UPDATE]\t:\tPushing commit ...")

        branches = self.client_obj.branch.list(self.stream_obj.id)
        branch_names = [b.name for b in branches]

        if self.echo_level == 1:
            print("[UPDATE]\t:\tSearching for appropriate branch ...")

        try:

            branch_names.index("analysis_column_eccentricity")

            if self.echo_level == 1:
                print("[UPDATE]\t:\tBranch found ...")

        except ValueError:

            if self.echo_level == 1:
                print("[UPDATE]\t:\tBranch not found, will be created ...")

            self.client_obj.branch.create(self.stream_obj.id,
                                          "analysis_column_eccentricity",
                                          "Output of the column eccentricity evaluation.")

        Commit.send_data(self.client_obj,
                         self.stream_obj.id,
                         self.commit_data,
                         "analysis_column_eccentricity",
                         self.commit_message)

        if self.echo_level == 1:
            print("[UPDATE]\t:\tFinished! :) ")
    