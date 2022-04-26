from aci.aci_utils import CommandPacket, EventPacket
from mesh import access

class DumpLogger(object):
    def __init__(self, name):
        self._name = name + ": "
    def _logging(self, msg, *args, **kwargs):
        print((self._name + msg) % ([a for a in args]))
    def error(self, msg, *args, **kwargs):
        self._logging("Dump LOG(error)" + msg, args, kwargs)
    def warning(self, msg, *args, **kwargs):
        self._logging("Dump LOG(warn )" + msg, args, kwargs)
    def info(self, msg, *args, **kwargs):
        self._logging("Dump LOG(info )" + msg, args, kwargs)
    def debug(self, msg, *args, **kwargs):
        self._logging("Dump LOG(debug)" + msg, args, kwargs)

class DumpSerial(object):
    def __init__(self):
        self.port = "dump_serial"

class DumpDevice(object):
    def __init__(self):
        self.logger = DumpLogger("DumpDevice")
        self._pack_recipients = []
        self.serial = DumpSerial()

    def write_aci_cmd(self, cmd):
        if isinstance(cmd, CommandPacket):
            return cmd.serialize()
        else:
            self.logger.error('The command provided is not valid: %s\nIt must be an instance of the CommandPacket class (or one of its subclasses)', str(cmd))

    def add_packet_recipient(self, function):
        self._pack_recipients.append(function)

    def process_packet(self, packet):
        for fun in self._pack_recipients[:]:
            try:
                fun(packet)
            except:
                self.logger.error('Exception in pkt handler %r', fun)
                self.logger.error('traceback: %s', traceback.format_exc())

class DumpApplicationConfig(object):
    def __init__(self):
        self.data = {
            'ACCESS_ELEMENT_COUNT': 99,
        }
        self.__dict__ = self.data

class DumpACI(object):
    DEFAULT_APP_KEY = bytearray([0xAA] * 16)
    DEFAULT_SUBNET_KEY = bytearray([0xBB] * 16)
    DEFAULT_VIRTUAL_ADDRESS = bytearray([0xCC] * 16)
    DEFAULT_STATIC_AUTH_DATA = bytearray([0xDD] * 16)
    DEFAULT_LOCAL_UNICAST_ADDRESS_START = 0x0001
    CONFIG = DumpApplicationConfig()

    def __init__(self):
        self.acidev = DumpDevice()
        self._event_filter = []
        self._event_filter_enabled = True
        self._other_events = []

        self.logger = DumpLogger("DumpACI")
        self.send = self.acidev.write_aci_cmd

        # Increment the local unicast address range
        # for the next Interactive instance
        self.local_unicast_address_start = (
            self.DEFAULT_LOCAL_UNICAST_ADDRESS_START)
        DumpACI.DEFAULT_LOCAL_UNICAST_ADDRESS_START += (
            self.CONFIG.ACCESS_ELEMENT_COUNT)

        self.access = access.Access(self, self.local_unicast_address_start,
                                    self.CONFIG.ACCESS_ELEMENT_COUNT)
        self.model_add = self.access.model_add

        # Adding the packet recipient will start dynamic behavior.
        # We add it after all the member variables has been defined
        self.acidev.add_packet_recipient(self.__event_handler)

    def event_filter_add(self, event_filter):
        self._event_filter += event_filter

    def __event_handler(self, event):
        pass
