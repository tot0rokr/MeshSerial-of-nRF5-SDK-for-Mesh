from mesh.access import Model, Opcode
from models.common import TransitionTime
import struct

class GenericDefaultTransitionTimeClient(Model):
    GENERIC_DEFAULT_TRANSITION_TIME_GET = Opcode(0x820D, None, "Generic Default Transition Time Get")
    GENERIC_DEFAULT_TRANSITION_TIME_SET = Opcode(0x820E, None, "Generic Default Transition Time Set")
    GENERIC_DEFAULT_TRANSITION_TIME_SET_UNACKNOWLEDGED = Opcode(
                                                 0x820F, None, "Generic Default Transition Time Set Unacknowledged")
    GENERIC_DEFAULT_TRANSITION_TIME_STATUS = Opcode(0x8210, None, "Generic Default Transition Time Status")

    def __init__(self):
        self.opcodes = [
            (self.GENERIC_DEFAULT_TRANSITION_TIME_STATUS, self.__generic_default_transition_time_status_handler)]
        super(GenericDefaultTransitionTimeClient, self).__init__(self.opcodes)

    def get(self):
        self.send(self.GENERIC_DEFAULT_TRANSITION_TIME_GET)

    def set(self, transition_time_ms, ack=True):
        message = bytearray([TransitionTime.encode(transition_time_ms)])

        if ack:
            self.send(self.GENERIC_DEFAULT_TRANSITION_TIME_SET, message)
        else:
            self.send(self.GENERIC_DEFAULT_TRANSITION_TIME_SET_UNACKNOWLEDGED, message)

    def __generic_default_transition_time_status_handler(self, opcode, message):
        logstr = "Transition time: %d ms" % (TransitionTime.decode(message.data[0]))
        self.logger.info(logstr)
