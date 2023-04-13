# This class is intended to work in conjunction with the specklepy class, not replace it!

from specklepy.api.models import Branch
from specklepy.api import operations
from specklepy.transports.server import ServerTransport

class Commit():

    '''
    A general placeholder for methods pertaining to commiting of data.
    '''

    def get_data(branch: Branch = None,
                 index: int = None):

        '''
        Get all data from a specific branch.

        Args:
            branch (speckle.api.models.Branch): Branch to get data from.
            index (int, optional): Index of desired commit (if known). Empty paramaters will lead user to being prompted with a list of available streams.

        Returns:
            specklepy.objects.base.Base: All commit data under the given branch.
        '''

        commit = None

        if index is None:

            print("\nAvailable commits under the given branch:")

            for idx, commit in enumerate(branch.commits.items):
                print("\t",idx, commit.message)

            commit_idx = input("\ncommit_index: ")
            print("")
            commit = branch.client.commit.get(branch.stream.id, branch.commits.items[int(commit_idx)].id)

        if index is not None:

            commit = branch.client.commit.get(branch.stream.id, branch.commits.items[index].id)

        transport = ServerTransport(branch.stream.id, branch.client)
        commit_data = operations.receive(commit.referencedObject, transport)

        commit_data.__setattr__("client_obj", branch.client)
        commit_data.__setattr__("stream_obj", branch.stream)

        return commit_data

    def send_data(client_obj, stream_id, commit_data, branch_name, commit_message):

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
        commit = client_obj.commit.create(stream_id = stream_id,
                                          object_id = obj_id,
                                          branch_name = branch_name,
                                          message = commit_message)
