from mesh.access import Model, Opcode
from models.common import TransitionTime
import struct

class GenericPowerLevelClient(Model):
    GENERIC_POWER_LEVEL_GET = Opcode(0x8215, None, "Generic Power Level Get")
    GENERIC_POWER_LEVEL_SET = Opcode(0x8216, None, "Generic Power Level Set")
    GENERIC_POWER_LEVEL_SET_UNACKNOWLEDGED = Opcode(0x8217, None, "Generic Power Level Set Unacknowledged")
    GENERIC_POWER_LEVEL_STATUS = Opcode(0x8218, None, "Generic Power Level Status")
    GENERIC_POWER_LAST_GET = Opcode(0x8219, None, "Generic Power Last Get")
    GENERIC_POWER_LAST_STATUS = Opcode(0x821A, None, "Generic Power Last Status")
    GENERIC_POWER_DEFAULT_GET = Opcode(0x821B, None, "Generic Power Default Get")
    GENERIC_POWER_DEFAULT_STATUS = Opcode(0x821C, None, "Generic Power Default Status")
    GENERIC_POWER_RANGE_GET = Opcode(0x821D, None, "Generic Power Range Get")
    GENERIC_POWER_RANGE_STATUS = Opcode(0x821E, None, "Generic Power Range Status")
    GENERIC_POWER_DEFAULT_SET = Opcode(0x821F, None, "Generic Power Default Set")
    GENERIC_POWER_DEFAULT_SET_UNACKNOWLEDGED = Opcode(0x8220, None, "Generic Power Default Set Unacknowledged")
    GENERIC_POWER_RANGE_SET = Opcode(0x8221, None, "Generic Power Range Set")
    GENERIC_POWER_RANGE_SET_UNACKNOWLEDGED = Opcode(0x8222, None, "Generic Power Range Set Unacknowledged")

    def __init__(self):
        self.opcodes = [
            (self.GENERIC_POWER_LEVEL_STATUS, self.__generic_power_level_status_handler),
            (self.GENERIC_POWER_LAST_STATUS, self.__generic_power_last_status_handler),
            (self.GENERIC_POWER_DEFAULT_STATUS, self.__generic_power_default_status_handler),
            (self.GENERIC_POWER_RANGE_STATUS, self.__generic_power_range_status_handler)]
        self.__tid = 0
        super(GenericPowerLevelClient, self).__init__(self.opcodes)

    def get(self):
        self.send(self.GENERIC_POWER_LEVEL_GET)

    def set(self, value, transition_time_ms=0, delay_ms=0, ack=True):
        message = bytearray()
        message += struct.pack("<HB", value, self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
            self.send(self.GENERIC_LEVEL_SET, message)
        else:
            self.send(self.GENERIC_LEVEL_SET_UNACKNOWLEDGED, message)

    def last_get(self):
        self.send(self.GENERIC_POWER_LAST_GET)

    def default_get(self):
        self.send(self.GENERIC_POWER_DEFAULT_GET)

    def default_set(self, value, ack=True):
        message = bytearray()
        message += struct.pack("<H", value)

        if ack:
            self.send(self.GENERIC_POWER_DEFAULT_SET, message)
        else:
            self.send(self.GENERIC_POWER_DEFAULT_SET_UNACKNOWLEDGED, message)

    def range_get(self):
        self.send(self.GENERIC_POWER_RANGE_GET)

    def range_set(self, range_min, range_max, ack=True):
        message = bytearray()
        message += struct.pack("<HH", range_min, range_max)

        if ack:
            self.send(self.GENERIC_POWER_DEFAULT_SET, message)
        else:
            self.send(self.GENERIC_POWER_DEFAULT_SET_UNACKNOWLEDGED, message)

    @property
    def _tid(self):
        tid = self.__tid
        self.__tid += 1
        if self.__tid >= 255:
            self.__tid = 0
        return tid

    def __generic_power_level_status_handler(self, opcode, message):
        logstr = "Present Power: %d" % (struct.unpack("<H", message.data[0:2]))
        if len(message.data) > 2:
            logstr += " Target Power: %d" % (struct.unpack("<H", message.data[2:4]))

        if len(message.data) == 5:
            logstr += " Remaining time: %d ms" % (TransitionTime.decode(message.data[4]))
        self.logger.info(logstr)

    def __generic_power_last_status_handler(self, opcode, message):
        logstr = "Last Power: %d" % (struct.unpack("<H", message.data[0:2]))
        self.logger.info(logstr)

    def __generic_power_default_status_handler(self, opcode, message):
        logstr = "Default Power: %d" % (struct.unpack("<H", message.data[0:2]))
        self.logger.info(logstr)

    def __generic_power_range_status_handler(self, opcode, message):
        status, range_min, range_max = struct.unpack("<BHH", message.data[0:5])
        if status == 1:
            logstr = "Cannot Set Range Min: "
        elif status == 2:
            logstr = "Cannot Set Range Max: "
        else:
            logstr = "Success: "
        logstr += "Range Min: %d, Range Max: %d, " % (range_min, range_max)
        self.logger.info(logstr)
