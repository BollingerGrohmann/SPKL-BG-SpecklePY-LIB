import os
import sys

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(root_folder)

from bg_specklepy.SpeckleServer.client import Client
from bg_specklepy.SpeckleServer.stream import Stream
from bg_specklepy.SpeckleServer.branch import Branch
from bg_specklepy.SpeckleServer.commit import Commit

def test_speckleServer():

    speckle_server = "insert"
    speckle_token = "insert"

    client_obj = Client(speckle_server, speckle_token)
    stream_obj = Stream(client_obj, 0)
    branch_obj = Branch(client_obj, stream_obj, 0)
    commit_data = Commit.get_data(branch_obj, 0)

    assert commit_data.totalChildrenCount != 0
