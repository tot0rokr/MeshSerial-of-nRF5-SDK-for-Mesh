from aci.aci_utils import STATUS_CODE_LUT
import aci.aci_cmd as cmd
import aci.aci_evt as evt

from mesh import access

from runtime.model_mgr import ModelMgr
class MeshSerialSession(object):
    DEFAULT_APP_KEY = bytearray([0xAA] * 16)
    DEFAULT_SUBNET_KEY = bytearray([0xBB] * 16)
    DEFAULT_VIRTUAL_ADDRESS = bytearray([0xCC] * 16)
    DEFAULT_STATIC_AUTH_DATA = bytearray([0xDD] * 16)
    DEFAULT_LOCAL_UNICAST_ADDRESS_START = 0x0001

    def __init__(self, acidev, logger, config, prov_db):
        self.acidev = acidev
        self._event_filter = set()
        self._event_filter_enabled = True
        self._other_events = []
        self.CONFIG = config
        self.logger = logger
        self.send = self.acidev.write_aci_cmd
        self.print_event_on = True
        self.model_mgr = ModelMgr(prov_db)
        self.model_handles = list()
        self.cmdrsp_queue = list()
        self.event_queue = list()

        # Increment the local unicast address range
        # for the next Meshserialsession instance
        self.local_unicast_address_start = (
            self.DEFAULT_LOCAL_UNICAST_ADDRESS_START)
        MeshSerialSession.DEFAULT_LOCAL_UNICAST_ADDRESS_START += (
            self.CONFIG.ACCESS_ELEMENT_COUNT)

        self.access = access.Access(self, self.local_unicast_address_start,
                                    self.CONFIG.ACCESS_ELEMENT_COUNT)
        self.model_add = self.access.model_add

        # Adding the packet recipient will start dynamic behavior.
        # We add it after all the member variables has been defined
        self.acidev.add_packet_recipient(self.__event_handler)

    def __del__(self):
        del self.access

    def get_model(self, model_name):
        model_handle = self.model_mgr.model_handle(model_name)
        model = self.model_mgr.model(model_handle)
        if model is None:
            return None
        if not model_handle in self.model_handles:
            self.model_add(model)
            self.model_handles.append(model_handle)
        return model

    def event_pop(self):
        if len(self._other_events) > 0:
            return self._other_events.pop()
        return None

    def event_filter_add(self, event_filter):
        self._event_filter |= set(event_filter)

    def event_filter_remove(self, event_filter):
        self._event_filter -= set(event_filter)

    def event_filter_disable(self):
        self._event_filter_enabled = False

    def event_filter_enable(self):
        self._event_filter_enabled = True

    def device_port_get(self):
        return self.acidev.serial.port

    def __event_handler(self, event):
        if self._event_filter_enabled and event._opcode in self._event_filter:
            # Ignore event
            return -1
        if event._opcode == evt.Event.DEVICE_STARTED:
            self.logger.info("Device rebooted.")

        elif event._opcode == evt.Event.CMD_RSP:
            if event._data["status"] != 0:
                self.logger.error("{}: {}".format(
                    cmd.response_deserialize(event),
                    STATUS_CODE_LUT[event._data["status"]]["code"]))
                return -1
            else:
                data = cmd.response_deserialize(event)
                text = str(data)
                if text == "None":
                    text = "Success"
                self.cmdrsp_queue.append(data)
                self.logger.info(text)
        else:
            if self.print_event_on and event is not None:
                self.logger.info(str(event))
            self._other_events.append(event)
        return 0
