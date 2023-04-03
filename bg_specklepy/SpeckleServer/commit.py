from specklepy.api.models import Branch
from specklepy.api import operations
from specklepy.transports.server import ServerTransport

class Commit():

    '''
    A general placeholder for methods pertaining to commiting of data.
    '''

    def get_data(branch: Branch = None):

        '''
        Get all data from a specific branch.

        Args:
            branch (speckle.api.models.Branch): Branch to get data from.
        Returns:
            specklepy.objects.base.Base: All commit data under the given branch.
        '''

        commit = branch.client.commit.get(branch.stream.id, branch.commits.items[0].id)
        transport = ServerTransport(branch.stream.id, branch.client)
        commit_data = operations.receive(commit.referencedObject, transport)

        commit_data.__setattr__("client_obj", branch.client)
        commit_data.__setattr__("stream_id", branch.stream.id)

        print(type(commit_data))

        return commit_data

    def send_data(client_obj, stream_id, commit_data, commit_message):

        '''
        Send a commit to a specific stream.

        Args:
            client_obj (): Client object to commit to.
            stream_id (): ID of stream to commit to.
            commit_data (): Base / Hash of data to be comitted. 
            commit_message (str): Associated message to the Speckle Server with commit.
        '''

        transport = ServerTransport(client = client_obj, stream_id = stream_id)
        obj_id = operations.send(base = commit_data, transports = [transport])
        commit = client_obj.commit.create(stream_id = stream_id, object_id = obj_id,
                                          message = commit_message)
