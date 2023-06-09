# Shifting working directory to root
import os
import sys

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(root_folder)

# Importing required modules
from bg_specklepy.SpeckleServer.client import Client
from bg_specklepy.SpeckleServer.stream import Stream
from bg_specklepy.SpeckleServer.branch import Branch
from bg_specklepy.SpeckleServer.commit import Commit
from bg_specklepy.Operations.columnOffsetEvaluation import ColumnOffsetEvaluation

# Example Model can be found here: https://speckle.xyz/streams/ff47530e95

# Server and token information
speckle_server = "insert"
speckle_token = "insert" # https://speckle.guide/dev/tokens.html

# Initiating appropriate server objects
client_obj = Client(speckle_server, speckle_token)
stream_obj = Stream(client_obj)
branch_obj = Branch(client_obj, stream_obj)

# Getting commit_data
commit_data = Commit.get_data(branch_obj)

# Define and run analysis
evaluation = ColumnOffsetEvaluation(commit_data = commit_data,
                                    tolerance = 0.02,
                                    echo_level = 1,
                                    scale_spheres = False)
evaluation.run()
