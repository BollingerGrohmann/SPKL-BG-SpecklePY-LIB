# MUSS ALS UNIT TEST UMGESCHRIEBEN WERDEN!!!!

if __name__ == "__main__":

    # Importieren der Bibliotheken
    from client import Client
    from stream import Stream
    from branch import Branch
    from commit import Commit

    # Variabeln
    speckle_server = "https://bg-designflow.germanywestcentral.cloudapp.azure.com"
    speckle_token = "dca43c122db58a93b51cf50a01cd436452855ee7cc"

    # Objekte definieren
    client_obj = Client(speckle_server, speckle_token)
    stream_obj = Stream(client_obj, 0)
    branch_obj = Branch(client_obj, stream_obj, 0)
    commit_data = Commit.getData(branch_obj)
    