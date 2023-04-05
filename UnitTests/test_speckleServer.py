import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(PROJECT_ROOT)

from SpeckleServer.client import Client
from SpeckleServer.stream import Stream
from SpeckleServer.branch import Branch
from SpeckleServer.commit import Commit

def test_speckleServer():

    speckle_server = input("Provide link to Speckle server: ")
    speckle_token = input("Provide Speckle token: ")

    client_obj = Client(speckle_server, speckle_token)
    stream_obj = Stream(client_obj, 0)
    branch_obj = Branch(client_obj, stream_obj, 0)
    commit_data = Commit.get_data(branch_obj)

    assert client_obj.authenticated == True
    assert branch_obj.client.server == speckle_server
    assert commit_data.totalChildrenCount != 0
   
