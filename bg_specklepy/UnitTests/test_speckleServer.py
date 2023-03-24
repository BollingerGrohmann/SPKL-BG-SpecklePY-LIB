import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(PROJECT_ROOT)

# Importieren der Bibliotheken
from SpeckleServer.client import Client
from SpeckleServer.stream import Stream
from SpeckleServer.branch import Branch
from SpeckleServer.commit import Commit

def test_speckleServer():

    speckle_server = "https://bg-designflow.germanywestcentral.cloudapp.azure.com"
    speckle_token = "dca43c122db58a93b51cf50a01cd436452855ee7cc"

    client_obj = Client(speckle_server, speckle_token)
    stream_obj = Stream(client_obj, 0)
    branch_obj = Branch(client_obj, stream_obj, 0)
    commit_data = Commit.getData(branch_obj)

    assert client_obj.authenticated == True
    assert stream_obj.name == "Revit ETABS Roundtrip Test"
    assert branch_obj.client.server == "https://bg-designflow.germanywestcentral.cloudapp.azure.com"
    assert commit_data.totalChildrenCount != 0
   