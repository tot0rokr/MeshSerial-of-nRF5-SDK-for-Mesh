from runtime.mesh_serial_session import MeshSerialSession
from runtime.device_mgr import DeviceMgr
from runtime.session_mgr import SessionMgr

import aci.aci_cmd as cmd

class MeshSerial(object):
    def __init__(self, options, config):
        self.options = options
        self.config = config
        self.device_mgr = DeviceMgr()
        self.session_mgr = SessionMgr(self.options, self.config, self.device_mgr)
        self.model_handles = list()

    def create_device(self, device):
        return self.device_mgr.create_device(device)

    def create_session(self, device_handle, prov_db):
        return self.session_mgr.create_session(device_handle, prov_db)

    def _decode_handles(self, application, address):
        # TODO:
        return 0, 0

    def run_model(self, session_handle, application, address, command):
        session = self.session_mgr.session(session_handle)
        if not 'op' in command or not 'model' in command:
            raise Exception("Command is invalid: model/op")
        model = session.get_model(command['model'])
        if model is None:
            raise Exception("%s is not found" % command['model'])
        op = getattr(model, command['op'])
        key_handle, address_handle = self._decode_handles(application, address)
        model.publish_set(key_handle, address_handle)
        if not 'arg' in command or command['arg'] is None:
            op()
        elif isinstance(command['arg'], dict):
            op(**command['arg'])
        elif isinstance(command['arg'], list):
            op(*command['arg'])
        else:
            raise Exception("Command is invalid: arg")

