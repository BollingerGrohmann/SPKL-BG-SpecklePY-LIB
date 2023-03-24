from specklepy.api.client import SpeckleClient

class Stream():
    def __new__(cls,
                client: SpeckleClient = None,
                index: int = None):

        '''
        Args:
            client (specklepy.api.client.SpeckleClient): SpeckleClient object. Use bg_specklepy.client to define this object.
            index (int, optional): Index of desired stream (if known). Empty paramaters will lead user to being prompted with a list of available streams.
        '''

        streams = client.stream.list()
        stream_names = [s.name for s in streams]

        if index is None:

            print("\nVerfügbare Streams unter dem angegebenen Token:")

            for idx, stream in enumerate(stream_names):
                print("\t",idx, stream)

            stream_idx = input("\nstream_index: ")
            stream_name = stream_names[int(stream_idx)]
            stream = client.stream.search(stream_name)[0]

            return stream

        elif index is not None:

            stream_name = stream_names[int(index)]
            stream = client.stream.search(stream_name)[0]

            return stream
