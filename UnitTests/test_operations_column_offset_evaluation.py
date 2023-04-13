# Definierte Modell aus dem Beispiel https://speckle.xyz/streams/ff47530e95
# 3 Stützenversätze

import os
import sys

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(root_folder)

from bg_specklepy.SpeckleServer.client import Client
from bg_specklepy.SpeckleServer.stream import Stream
from bg_specklepy.SpeckleServer.branch import Branch
from bg_specklepy.SpeckleServer.commit import Commit
from bg_specklepy.Operations.columnOffsetEvaluation import ColumnOffsetEvaluation

def test_operations_column_offset_evaluation():

    speckle_server = "https://speckle.xyz"
    speckle_token = input("Provide Speckle token: ")

    client_obj = Client(speckle_server, speckle_token)
    stream_obj = Stream(client_obj, 0)
    branch_obj = Branch(client_obj, stream_obj, 0)
    commit_data = Commit.get_data(branch_obj, 0)

    evaluation = ColumnOffsetEvaluation(commit_data = commit_data,
                                        tolerance = 0.02,
                                        echo_level = 0,
                                        column_parameter = "@Structural Columns",
                                        scale_spheres = False)
    evaluation.run()

    assert len(evaluation.commit_data["@Analysis_ColumnEccentricity"]) == 3
