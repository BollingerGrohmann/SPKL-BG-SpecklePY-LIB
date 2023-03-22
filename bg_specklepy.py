# Importieren der Bibliotheken
import dependencies
from specklepy.api import operations
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token
from specklepy.transports.server import ServerTransport

# Interaktion mit dem Speckle-Server
class Branch():
    def __init__(self,
                 speckle_server: str = None,
                 speckle_token: str = None,
                 stream_index: int = None,
                 branch_index: int = None):

        '''
        Args:
            speckle_server (str): Server url for the desired stream.
            speckler_token (str): Personal access token. For more information refer to https://speckle.guide/dev/tokens.html
            stream_index (int, optional): Index of desired stream. Optional parameter. Should no argument be given, the user will be prompted with a list of options.
            branch_index (int, optional): Index of desired branch. Optional parameter. Should no argument be given, the user will be prompted with a list of options.
        '''

        client = SpeckleClient (host = speckle_server)
        account = get_account_from_token(speckle_token, speckle_server)
        client.authenticate_with_account(account)

        branch = None

        self.client = client
        self.account = account

        streams = client.stream.list()
        print(streams)
        stream_names = [s.name for s in streams]

        if stream_index is None:

            print("\nVerfügbare Streams unter dem angegebenen Token:")

            for idx, stream in enumerate(stream_names):
                print("\t",idx, stream)

            stream_idx = input("\nstream_index: ")
            stream_name = stream_names[int(stream_idx)]
            stream = client.stream.search(stream_name)[0]

            self.stream_name = stream_name
            self.stream_id = stream.id
            self.stream = stream

        elif stream_index is not None:

            stream_name = stream_names[int(stream_index)]
            stream = client.stream.search(stream_name)[0]

            self.stream_name = stream_name
            self.stream_id = stream.id
            self.stream = stream

        branches = client.branch.list(stream.id)
        branch_names = [b.name for b in branches]

        if branch_index is None:

            print("\nVerfügbare Branches im ausgewählten Stream:")

            for idx, branch in enumerate(branch_names):
                print("\t", idx, branch)

            branch_idx = input("\nbranch_index: ")
            branch_name = branch_names[int(branch_idx)]
            branch = client.branch.get(stream_id = self.stream_id, name = branch_name)

            self.branch_name = branch_name

        elif branch_index is not None:

            branch_name = branch_names[int(branch_index)]
            branch = client.branch.get(stream_id = self.stream_id, name = branch_name)

            self.branch_name = branch_name

        commit = self.client.commit.get(self.stream_id, branch.commits.items[0].id)
        transport = ServerTransport(client = client, stream_id = self.stream_id)
        commit_data = operations.receive(commit.referencedObject, transport)

        self.commit_data = commit_data

        self = branch
