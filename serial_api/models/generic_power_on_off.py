from mesh.access import Model, Opcode
import struct

class GenericPowerOnOffClient(Model):
    GENERIC_ON_POWER_UP_GET = Opcode(0x8211, None, "Generic On Power Up Get")
    GENERIC_ON_POWER_UP_STATUS = Opcode(0x8212, None, "Generic On Power Up Status")
    GENERIC_ON_POWER_UP_SET = Opcode(0x8213, None, "Generic On Power Up Set")
    GENERIC_ON_POWER_UP_SET_UNACKNOWLEDGED = Opcode(0x8214, None, "Generic On Power Up Set Unacknowledged")

    def __init__(self):
        self.opcodes = [
            (self.GENERIC_ON_POWER_UP_STATUS, self.__generic_on_power_up_status_handler)]
        super(GenericPowerOnOffClient, self).__init__(self.opcodes)

    def get(self):
        self.send(self.GENERIC_ON_POWER_UP_GET)

    def set(self, value, ack=True):
        message = bytearray([value])

        if ack:
            self.send(self.GENERIC_ON_POWER_UP_SET, message)
        else:
            self.send(self.GENERIC_ON_OFF_SET_UNACKNOWLEDGED, message)

    def __generic_on_power_up_status_handler(self, opcode, message):
        logstr = "On Power Up: "
        if message.data[0] == 1:
            logstr += "Default"
        elif message.data[0] == 2:
            logstr += "Restore"
        else:
            logstr += "Off"
        self.logger.info(logstr)
