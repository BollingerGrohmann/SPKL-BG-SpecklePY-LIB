#from branch import Branch
from specklepy.api.models import Branch
from specklepy.api import operations
from specklepy.transports.server import ServerTransport

class Commit():

    def getData(branch: Branch = None):
                    
        commit = branch.client.commit.get(branch.stream.id, branch.commits.items[0].id)
        transport = ServerTransport(branch.stream.id, branch.client)
        commit_data = operations.receive(commit.referencedObject, transport)

        return commit_data