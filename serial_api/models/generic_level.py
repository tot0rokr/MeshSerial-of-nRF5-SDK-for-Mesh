from mesh.access import Model, Opcode
from models.common import TransitionTime
import mesh.types as mt
import struct

class GenericLevelClient(Model):
    MODEL_ID = mt.ModelId(0x1003)
    TARGET_MODEL_ID = mt.ModelId(0x1002)
    GENERIC_LEVEL_GET = Opcode(0x8205, None, "Generic Level Get")
    GENERIC_LEVEL_SET = Opcode(0x8206, None, "Generic Level Set")
    GENERIC_LEVEL_SET_UNACKNOWLEDGED = Opcode(0x8207, None, "Generic Level Set Unacknowledged")
    GENERIC_LEVEL_STATUS = Opcode(0x8208, None, "Generic Level Status")
    GENERIC_DELTA_SET = Opcode(0x8209, None, "Generic Delta Set")
    GENERIC_DELTA_SET_UNACKNOWLEDGED = Opcode(0x820A, None, "Generic Delta Set Unacknowledged")
    GENERIC_MOVE_SET = Opcode(0x820B, None, "Generic Move Set")
    GENERIC_MOVE_SET_UNACKNOWLEDGED = Opcode(0x820C, None, "Generic Move Set Unacknowledged")

    def __init__(self):
        self.opcodes = [
            (self.GENERIC_LEVEL_GET, self.get),
            (self.GENERIC_LEVEL_SET, self.set),
            (self.GENERIC_LEVEL_SET_UNACKNOWLEDGED, self.set),
            (self.GENERIC_LEVEL_STATUS, self.__generic_level_status_handler),
            (self.GENERIC_DELTA_SET, self.delta_set),
            (self.GENERIC_DELTA_SET_UNACKNOWLEDGED, self.delta_set),
            (self.GENERIC_MOVE_SET, self.move_set),
            (self.GENERIC_MOVE_SET_UNACKNOWLEDGED, self.move_set),
            ]
        self.__tid = 0
        super(GenericLevelClient, self).__init__(self.opcodes)

    def set(self, value, transition_time_ms=0, delay_ms=0, ack=True):
        message = bytearray()
        message += struct.pack("<hB", value, self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
            return self.send(self.GENERIC_LEVEL_SET, message)
        else:
            return self.send(self.GENERIC_LEVEL_SET_UNACKNOWLEDGED, message)

    def get(self):
        return self.send(self.GENERIC_LEVEL_GET)

    def delta_set(self, value, transition_time_ms=0, delay_ms=0, ack=True):
        message = bytearray()
        message += struct.pack("<iB", value, self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
            return self.send(self.GENERIC_DELTA_SET, message)
        else:
            return self.send(self.GENERIC_DELTA_SET_UNACKNOWLEDGED, message)

    def move_set(self, value, transition_time_ms=0, delay_ms=0, ack=True):
        if transition_time_ms == 0:
            self.logger.info("If transition time is 0 or undefined," +
                             " no Generic Level state change happens.")
        message = bytearray()
        message += struct.pack("<HB", value, self._tid)

        if transition_time_ms > 0:
            message += TransitionTime.pack(transition_time_ms, delay_ms)

        if ack:
            return self.send(self.GENERIC_MOVE_SET, message)
        else:
            return self.send(self.GENERIC_MOVE_SET_UNACKNOWLEDGED, message)

    @property
    def _tid(self):
        tid = self.__tid
        self.__tid += 1
        if self.__tid >= 255:
            self.__tid = 0
        return tid

    def __generic_level_status_handler(self, opcode, message):
        _data = dict()
        _data['present_level'] = struct.unpack("<h", message.data[0:2])
        logstr = "Present Level: " + str(_data['present_level'])
        if len(message.data) > 2:
            _data['target_level'] = struct.unpack("<h", message.data[2:4])
            logstr += " Target Level: " + str(_data['target_level'])
        if len(message.data) == 5:
            _data['remaining_time'] = TransitionTime.decode(message.data[4])
            logstr += " Remaining time: %d ms" % _data['remaining_time']

        self.logger.info(logstr)
        return _data
