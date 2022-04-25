import unittest

from test.dump_aci import DumpACI, CommandPacket, EventPacket

class TestDumpACI(unittest.TestCase):
    def setUp(self):
        self.device = DumpACI()

    def test_acidev(self):
        acidev = self.device.acidev
        self.assertIsNone(acidev.write_aci_cmd("NOT CommandPacket data"))
        test_packet = CommandPacket(0x13, bytearray([0x12, 0x11, 0x00]))
        self.assertIsNotNone(acidev.write_aci_cmd(test_packet))
        acidev.add_packet_recipient(lambda event: print("%x: %r" % (event._opcode, event._data)) if event._opcode == 0x82 else 0)
        test_event = EventPacket("Echo", 0x82, {"key": [0, 1], "index": 42})
        acidev.process_packet(test_event)

    def test_aci(self):
        device = self.device
        device.event_filter_add([0xAB])
        device.event_filter_add([0xCD])
        device.event_filter_add([0xEF])

        def __event_handler(self, event):
            if event._opcode == 0xAA:
                self.assertIs(event._data['is'], 1)
            if event._opcode == 0xCD:
                self.assertIs(event._data['is'], 2)
            if event._opcode == 0xEF:
                self.assertIs(event._data['is'], 3)

        device.acidev.add_packet_recipient(__event_handler)
        test_event = EventPacket("AB", 0xAB, {"is": 1})
        test_event = EventPacket("CD", 0xCD, {"is": 2})
        test_event = EventPacket("EF", 0xEF, {"is": 3})


if __name__ == '__main__':
    unittest.main()
