import os
import sys
import pandas as pd
import math
from specklepy.objects.geometry import Base
from specklepy.objects.other import RenderMaterial

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(root_folder)

from Geometry.sphere import Sphere
from SpeckleServer.commit import Commit
import dependencies

class ColumnOffsetEvaluation():

    def __init__(self,
                 commit_data,
                 echo_level : int = 0,
                 tolerance : float = 0.01,
                 scale_spheres : bool = False):

        '''
        Perform a column offset evaluation on a commit_data.

        Args:
            commit_data (specklepy.objects.base.Base): commit_data object obtained using Commit.getData() from the bg_specklepy library
            echo_level (int): Default of 0 - no updates printed to console. 1 - updates printed to console.
            tolerance (float): Calculated distances of the offsets (in the x-y plane) larger than the tolerance will be deemed as an offset column. To be given in units of Revit model. Default assumed to be in metres.
            append_spheres_to_received_commit (bool): When False, only spheres are commited. When True, spheres are calculated and pushed back WITH all original commit data
            scale_spheres (bool): When False, sphere radius is set to offset distance (radius limited to a maximum of 0.5 m). When True, sphere radius set to 0.35 m
        '''

        self.commit_data = commit_data
        self.echo_level = echo_level
        self.column_parameter = None
        self.tolerance = tolerance
        self.commit_message = "analysis_column_eccentricity"
        self.scale_spheres = scale_spheres
        self.client_obj = commit_data.client_obj
        self.stream_obj = commit_data.stream_obj
        self.column_elements = None
        self.data_frame = None
        self.offset_columns_dataframe = None
        self.commit_object = None
        self._units = 'm'
        self._units_scaling = 1

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
            -   ToDo muss ein normales Revit-Modell sein (nicht ein Berechnungsmodell). Ein Berechnungsmodell hat Stützen ohne "baseLine" Attributen
        '''

        # HACKY - muss einen besseren Weg geben?
        if not "Revit" in self.commit_data[dir(self.commit_data)[0]][0].speckle_type:
            raise NotImplementedError("Column offset evaluation currently restricted to Revit models only.")

        if self.echo_level == 1:
            print("[UPDATE]\t:\tRevit model detected ...")

        if self.commit_data.speckle_type != "Objects.Organization.Model":
            raise AttributeError("Commit data not of correct speckle type. A Revit Model needs to be used as basis input.")

        # More languages to be added. But, Revit export should be standard english
        for column_parameter in ["@Structural Columns", "@Tragwerksstützen"]:
            try:
                self.column_elements = self.commit_data[column_parameter]
                self.column_parameter = column_parameter
                break
            except KeyError:
                continue

        if self.column_elements[0].units != 'm':
            if self.column_elements[0].units == 'mm':
                self._units = 'mm'
                self._units_scaling = 1000
                print("[WARNING]\t:\tModel assumed to be in metres. Internal conversions taking place for mm. Double-check outputs")
            else:
                raise NotImplementedError("Currently only supported for Revit models of units of m and mm.")

    def _build_dataframe(self):

        df = pd.DataFrame()
        vertices = []

        if self.echo_level == 1:
            print("[UPDATE]\t:\tBuilding column database ...")

        if 'baseLine' not in vars(self.column_elements[0]):
            raise AttributeError('Columns have no attribute "baseLine". This is crucial to analysis. Double-check Revit model commit.')

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

        ndigits = 0 # e.g. 3,753 m -> 4 m

        if self._units == 'mm':
            ndigits = -3 # e.g. 3753 mm -> 4000 mm

        df["x_sort"] = round(df["x_u"], ndigits) # !! Überprüfen
        df["y_sort"] = round(df["y_u"], ndigits) # !! Überprüfen
        df["z_sort"] = round(df["z_u"], ndigits) # !! Überprüfen

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
                raise NotImplementedError("Slanted columns not yet implemented.")

            else:
                # Last index of the DataFrame, ignored. No comparison
                if index == len(self.data_frame.index) - 1:
                    continue

                # Here, if the z coord of the below column is <= the z coord of column above, we can compare
                if row["z_o"] - self.data_frame.iloc[index + 1]["z_u"] <= self.tolerance:
                    delta_x = float(row["x_o"] - self.data_frame.iloc[index + 1]["x_u"])
                    delta_y = float(row["y_o"] - self.data_frame.iloc[index + 1]["y_u"])

                    srss = math.sqrt(delta_x**2 + delta_y**2)

                    if srss > self.tolerance and srss < 0.5 * self._units_scaling: # < 500 mm assumed to be offset. > 500 mm assumed to be discontinuity

                        column_below_id.append(row["id"]) # ToDo: 7 Zeilen -> Funktion (wird 3 Mal aufgerufen)
                        column_below_elementId.append(row["elementId"])
                        column_below_applicationId.append(row["applicationId"])

                        offset_column_indices.append(index + 1)

                        offset_srss.append(srss)
                        offset_x.append(delta_x)
                        offset_y.append(delta_y)
                    
                    # If the SRSS > 500 mm, this doesn't belong to column run and is a discontinuous
                    if srss > 0.5 * self._units_scaling:

                        column_below_id.append(None) # No column below, hence None
                        column_below_elementId.append(None)
                        column_below_applicationId.append(None)
    
                        offset_column_indices.append(index + 1)
    
                        offset_srss.append("-")
                        offset_x.append("-")
                        offset_y.append("-")

                # If the column above "jumps" vertically more than 1 m, there is a discontinuity in the level!
                if self.data_frame.iloc[index + 1]["z_u"] - row["z_o"] > 1 * self._units_scaling:

                    column_below_id.append(None) # No column below, hence None
                    column_below_elementId.append(None)
                    column_below_applicationId.append(None)

                    offset_column_indices.append(index + 1)

                    offset_srss.append("-")
                    offset_x.append("-")
                    offset_y.append("-")

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

        self.offset_columns_dataframe = offset_df

    def _generate_spheres(self):

        if self.echo_level == 1:
            print("[UPDATE]\t:\tGenerating sphere objects for visualization ...")

        commit_object = Base()
        commit_object["@Analysis_ColumnEccentricity"] = []

        for index, row in self.offset_columns_dataframe.iterrows():

            obj = Base()

            obj["@column_above"], obj["@column_below"], obj["@offset"] = {}, {}, {}

            radius = 0.35 * self._units_scaling
            if self.scale_spheres:
                if row["offset_srss"] != '-': # Discontinuities have no numeric SRSS information
                    radius = min(0.5 * self.scale_spheres, row["offset_srss"]) # Limiting to a maximum of 500 mm radius. Big offsets present a display danger

            mesh = Sphere.create(radius = radius, center = [row["x_u"], row["y_u"], row["z_u"]])

            obj["displayValue"] = mesh
            obj["displayValue"]["renderMaterial"] = RenderMaterial(opacity = 0.5,
                                                                   diffuse = 16711680,
                                                                   emissive = 16711680) # Red

            for variable in self.offset_columns_dataframe.columns:

                if variable.startswith("column_below"):

                    if row["column_below_id"] is None: # Discontinuous col.
                        obj["@column_below"][variable.split("_")[-1]] = "Column underneath missing"
                        obj["@offset"]["Column_discontinuous"] = True

                    else: # Not discontinuous but eccentric col.
                        obj["@column_below"][variable.split("_")[-1]] = row[variable]
                        obj["@offset"]["Column_discontinuous"] = False

                elif variable.startswith("column_above"):

                    obj["@column_above"][variable.split("_")[-1]] = row[variable]

                elif variable.startswith("offset"):

                    if self._units == 'm' and isinstance(row[variable], float):
                        display_num = round(row[variable], 3)
                    if self._units == 'mm' and isinstance(row[variable], float):
                        display_num = round(row[variable], 0)
                    if row[variable] == '-':
                        display_num = '-'

                    obj["@offset"]["Offset_" + variable.split("_")[-1].upper() + " ({})".format(self._units)] = display_num

            commit_object["@Analysis_ColumnEccentricity"].append(obj)

        self.commit_object = commit_object

    def _commit_data(self):
        
        self.commit_data = self.commit_object

        if self.echo_level == 1:
            print("[UPDATE]\t:\tReady to commit ...")

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
                         branch_name = "analysis_column_eccentricity",
                         commit_message = self.commit_message)

        if self.echo_level == 1:
            print("[UPDATE]\t:\tFinished! :) ")
