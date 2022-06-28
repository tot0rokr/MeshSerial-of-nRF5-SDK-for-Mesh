from runtime.configure_logger import configure_logger
from runtime.mesh_serial_session import MeshSerialSession
from runtime.device_mgr import DeviceMgr

class SessionMgr(object):
    def __init__(self, options, config, device_mgr):
        self.options = options
        self.device_mgr = device_mgr
        self.config = config
        self.__sessions = dict()
        self.__next_session_handle = 0

    def create_session(self, device_handle, prov_db):
        logger = configure_logger(self.options.log_level,
                                  self.device_mgr.device(device_handle).device_name,
                                  self.device_mgr.device(device_handle).port)
        device = self.device_mgr.hold_device(device_handle)
        if device is None:
            raise RuntimeError("Target device (handle #{}) can't be used.".format(device_handle))
        self.__sessions[self.__next_session_handle] = {'session': MeshSerialSession(
                                                                        self.device_mgr.device(device_handle),
                                                                        logger,
                                                                        self.config,
                                                                        prov_db),
                                                       'device_handle': device_handle}
        self.__next_session_handle += 1
        return self.__next_session_handle - 1

    def remove_session(self, session_handle):
        if not self.__valid_handle(session_handle):
            return
        self.device_mgr.release_device(self.__sessions[session_handle]['device_handle'])
        del self.__sessions[session_handle]

    def __valid_handle(self, session_handle):
        return session_handle in self.__sessions

    def session(self, session_handle):
        if not self.__valid_handle(session_handle):
            return None
        else:
            return self.__sessions[session_handle]['session']
