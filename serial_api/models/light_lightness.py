from mesh.access import Model, Opcode
from models.common import TransitionTime
import struct

class LightLightnessClient(Model):
    LIGHT_LIGHTNESS_GET = Opcode(0x824B, None)
    LIGHT_LIGHTNESS_SET = Opcode(0x824C, None)
    LIGHT_LIGHTNESS_SET_UNACKNOWLEDGED = Opcode(0x824D, None)
    LIGHT_LIGHTNESS_STATUS = Opcode(0x824E, None)
    LIGHT_LIGHTNESS_LINEAR_GET = Opcode(0x824F, None)
    LIGHT_LIGHTNESS_LINEAR_SET = Opcode(0x8250, None)
    LIGHT_LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED = Opcode(0x8251, None)
    LIGHT_LIGHTNESS_LINEAR_STATUS = Opcode(0x8252, None)
    LIGHT_LIGHTNESS_LAST_GET = Opcode(0x8253, None)
    LIGHT_LIGHTNESS_LAST_STATUS = Opcode(0x8254, None)
    LIGHT_LIGHTNESS_DEFAULT_GET = Opcode(0x8255, None)
    LIGHT_LIGHTNESS_DEFAULT_STATUS = Opcode(0x8256, None)
    LIGHT_LIGHTNESS_RANGE_GET = Opcode(0x8257, None)
    LIGHT_LIGHTNESS_RANGE_STATUS = Opcode(0x8258, None)
    LIGHT_LIGHTNESS_DEFAULT_SET = Opcode(0x8259, None)
    LIGHT_LIGHTNESS_DEFAULT_SET_UNACKNOWLEDGED = Opcode(0x825A, None)
    LIGHT_LIGHTNESS_RANGE_SET = Opcode(0x825B, None)
    LIGHT_LIGHTNESS_RANGE_SET_UNACKNOWLEDGED = Opcode(0x825C, None)

    def __init__(self):
        self.opcodes = [
            (self.LIGHT_LIGHTNESS_STATUS, self.__light_lightness_status_handler),
            (self.LIGHT_LIGHTNESS_LINEAR_STATUS, self.__light_lightness_linear_status_handler),
            (self.LIGHT_LIGHTNESS_LAST_STATUS, self.__light_lightness_last_status_handler),
            (self.LIGHT_LIGHTNESS_DEFAULT_STATUS, self.__light_lightness_default_status_handler),
            (self.LIGHT_LIGHTNESS_RANGE_STATUS, self.__light_lightness_range_status_handler)]
        self.__tid = 0
        super(LightLightnessClient, self).__init__(self.opcodes)

    def get(self):
        self.send(self.LIGHT_LIGHTNESS_GET)

    def set(self, value, transition_time_ms=0, delay_ms=0, ack=True):
        message = bytearray()
        message += struct.pack("<HB", value, self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
            self.send(self.LIGHT_LIGHTNESS_SET, message)
        else:
            self.send(self.LIGHT_LIGHTNESS_SET_UNACKNOWLEDGED, message)

    def linear_get(self):
        self.send(self.LIGHT_LIGHTNESS_LINEAR_GET)

    def linear_set(self, value, transition_time_ms=0, delay_ms=0, ack=True):
        message = bytearray()
        message += struct.pack("<HB", value, self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
            self.send(self.LIGHT_LIGHTNESS_LINEAR_SET, message)
        else:
            self.send(self.LIGHT_LIGHTNESS_LINEAR_SET_UNACKNOWLEDGED, message)

    def last_get(self):
        self.send(self.LIGHT_LIGHTNESS_LAST_GET)

    def default_get(self):
        self.send(self.LIGHT_LIGHTNESS_DEFAULT_GET)

    def default_set(self, value, ack=True):
        message = bytearray()
        message += struct.pack("<H", value)

        if ack:
            self.send(self.LIGHT_LIGHTNESS_DEFAULT_SET, message)
        else:
            self.send(self.LIGHT_LIGHTNESS_DEFAULT_SET_UNACKNOWLEDGED, message)

    def range_get(self):
        self.send(self.LIGHT_LIGHTNESS_RANGE_GET)

    def range_set(self, range_min, range_max, ack=True):
        message = bytearray()
        message += struct.pack("<HH", range_min, range_max)

        if ack:
            self.send(self.LIGHT_LIGHTNESS_RANGE_SET, message)
        else:
            self.send(self.LIGHT_LIGHTNESS_RANGE_SET_UNACKNOWLEDGED, message)

    @property
    def _tid(self):
        tid = self.__tid
        self.__tid += 1
        if self.__tid >= 255:
            self.__tid = 0
        return tid

    def __light_lightness_status_handler(self, opcode, message):
        logstr = "Present Lightness: %d" % (struct.unpack("<H", message.data[0:2]))
        if len(message.data) > 2:
            logstr += " Target Lightness: %d" % (struct.unpack("<H", message.data[2:4]))

        if len(message.data) == 5:
            logstr += " Remaining time: %d ms" % (TransitionTime.decode(message.data[4]))
        self.logger.info(logstr)

    def __light_lightness_linear_status_handler(self, opcode, message):
        self.__light_lightness_status_handler(opcode, message)

    def __light_lightness_last_status_handler(self, opcode, message):
        logstr = "Last Lightness: %d" % (struct.unpack("<H", message.data[0:2]))
        self.logger.info(logstr)

    def __light_lightness_default_status_handler(self, opcode, message):
        logstr = "Default Lightness: %d" % (struct.unpack("<H", message.data[0:2]))
        self.logger.info(logstr)

    def __light_lightness_range_status_handler(self, opcode, message):
        status, range_min, range_max = struct.unpack("<BHH", message.data[0:5])
        if status == 1:
            logstr = "Cannot Set Range Min: "
        elif status == 2:
            logstr = "Cannot Set Range Max: "
        else:
            logstr = "Success: "
        logstr += "Range Min: %d, Range Max: %d, " % (range_min, range_max)
        self.logger.info(logstr)

