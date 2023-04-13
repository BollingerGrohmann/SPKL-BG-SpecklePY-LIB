# This class is intended to work in conjunction with the specklepy class, not replace it!

from specklepy.api.client import SpeckleClient
from specklepy.api.models import Stream

class Branch():

    def __new__(cls,
                client: SpeckleClient = None,
                stream: Stream = None,
                index: int = None):

        '''
        Access a Branch of a given Stream.

        Args:
            client (specklepy.api.client.SpeckleClient): SpeckleClient object. Use bg_specklepy.client to define this object.
            stream (specklepy.api.models.Stream): Stream object. Use bg_specklepy.stream to define this object.
            index (int, optional): Index of desired branch (if known). Empty paramaters will lead user to being prompted with a list of available branches.

        Returns:
            specklepy.api.models.Branch: Speckle Branch object is returned.
        '''

        branches = client.branch.list(stream.id)
        branch_names = [b.name for b in branches]

        branch = None

        if index is None:

            print("\nAvailable branches in selected stream:")

            for idx, branch in enumerate(branch_names):
                print("\t", idx, branch)

            branch_idx = input("\nbranch_index: ")
            branch_name = branch_names[int(branch_idx)]
            branch = client.branch.get(stream_id = stream.id, name = branch_name)

        elif index is not None:

            branch_name = branch_names[int(index)]
            branch = client.branch.get(stream_id = stream.id, name = branch_name)

        object.__setattr__(branch, 'client', client)
        object.__setattr__(branch, 'stream', stream)

        return branch
