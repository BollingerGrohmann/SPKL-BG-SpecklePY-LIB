from specklepy.api.client import SpeckleClient

class Stream():

    def __new__(cls,
                client: SpeckleClient = None,
                index: int = None):

        '''
        Access the Stream of a given Client.

        Args:
            client (specklepy.api.client.SpeckleClient): SpeckleClient object. Use bg_specklepy.client to define this object.
            index (int, optional): Index of desired stream (if known). Empty paramaters will lead user to being prompted with a list of available streams.

        Raises:
            Exception: _description_

        Returns:
            specklepy.api.models.Stream: A Speckle Stream object is returned.
        '''

        streams = client.stream.list()

        if len(streams) == 0:
            raise Exception("No streams under the given Client.")

        stream_names = [s.name for s in streams]

        if index is None:

            print("\nAvailable streams under the given client:")

            for idx, stream in enumerate(stream_names):
                print("\t",idx, stream)

            stream_idx = input("\nstream_index: ")
            stream_name = stream_names[int(stream_idx)]
            stream = client.stream.search(stream_name)[0]

            object.__setattr__(stream, 'index', stream_idx)

            return stream

        if index is not None:

            stream_name = stream_names[int(index)]
            stream = client.stream.search(stream_name)[0]

            object.__setattr__(stream, 'index', index)

            return stream
