from multiprocessing.connection import Client

class MeshAPIClient(object):
    def __init__(self, address=('localhost', 5070)):
        self.address = address

    def __call__(self, func, *args, **kwargs):
        with Client(self.address, authkey=b'1234') as conn:
            conn.send([func, args, kwargs])
            ret = conn.recv()
        return ret

