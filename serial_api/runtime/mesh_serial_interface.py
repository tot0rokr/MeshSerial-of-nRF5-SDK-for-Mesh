from abc import ABCMeta, abstractmethod

class MeshSerialInterface(metaclass=ABCMeta):
    def __init__(self, mesh, options, db):
        self.mesh = mesh
        self.options = options
        self.db = db
        self.session_handles = list()
        self.device_handles = list()
        self.nodes = list()                     # element: (session_handle, address)
        self.applications = list()              # element: (session_handle, appkey_index)
        self.__next_default_key = 0xFF000000

    @abstractmethod
    def __del__(self):
        pass

    @abstractmethod
    def connect_session(self, device_index):
        pass

    @abstractmethod
    def set_provisioner(self, session_handle):
        pass

    @abstractmethod
    def start_session(self, session_handle):
        pass

    @abstractmethod
    def provision_node(self, uuid, key_index=0, name="Node", context_id=0, attention_duration_s=0):
        pass

    @abstractmethod
    def run_model(self, session_index, application_index, node_index, command, service):
        pass

    @property
    def _default_key(self):
        self.__next_default_key += 1
        return self.__next_default_key
