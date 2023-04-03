import os
import sys
from specklepy.api.client import SpeckleClient
from specklepy.api.credentials import get_account_from_token

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(PROJECT_ROOT)

import dependencies

class Client():

    def __new__(cls,
                speckle_server: str = None,
                speckle_token: str = None):

        '''
        Access the SpeckleClient object for a given server using an authorization token.

        Args:
            speckle_server (str): Server url for the desired stream.
            speckler_token (str): Personal access token. For more information refer to https://speckle.guide/dev/tokens.html

        Returns:
            specklepy.api.client.SpeckleClient: SpeckleClient object is returned.
        '''

        client = SpeckleClient (host = speckle_server)
        account = get_account_from_token(speckle_token, speckle_server)
        client.authenticate_with_account(account)

        object.__setattr__(client, 'speckle_server', speckle_server)
        object.__setattr__(client, 'speckle_token', speckle_token)

        return client
    