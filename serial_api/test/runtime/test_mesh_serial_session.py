import unittest

from runtime.mesh_serial_session import MeshSerialSession
from aci.aci_evt import Event, CmdRsp
from aci.aci_utils import EventPacket, CommandPacket
from test.dump_aci import DumpLogger, DumpDevice, DumpApplicationConfig

class TestMeshSerialSession(unittest.TestCase):
    def setUp(self):
        self.session = MeshSerialSession(DumpDevice(), DumpLogger("Dump"), DumpApplicationConfig())

    def test_event_filter_add(self):
        session = self.session
        self.assertNotIn(0xFF, session._event_filter)
        session.event_filter_add([0xFF])
        self.assertIn(0xFF, session._event_filter)
        session.event_filter_add([0xFF, 0x00])
        self.assertIn(0x00, session._event_filter)

    def test_event_filter_remove(self):
        session = self.session
        session.event_filter_add([0xFF, 0x00])
        session.event_filter_remove([0xFF])
        self.assertIn(0x00, session._event_filter)
        self.assertNotIn(0xFF, session._event_filter)
        session.event_filter_add([0x00])
        session.event_filter_remove([0x00])
        self.assertNotIn(0x00, session._event_filter)

    def test___event_handler(self):
        session = self.session
        session.event_filter_add([Event.DEVICE_STARTED])
        test_event = EventPacket("TEST filtered event packet(DEVICE_STARTED)", Event.DEVICE_STARTED, {})
        self.assertIn(Event.DEVICE_STARTED, session._event_filter)
        self.assertLess(session._MeshSerialSession__event_handler(test_event), 0)
        session.event_filter_disable()
        self.assertGreaterEqual(session._MeshSerialSession__event_handler(test_event), 0)
        session.event_filter_enable()
        self.assertLess(session._MeshSerialSession__event_handler(test_event), 0)

        test_event = CmdRsp(bytearray([0xFF, 0]))
        self.assertGreaterEqual(session._MeshSerialSession__event_handler(test_event), 0)

        test_event = EventPacket("TEST other event packet", 0xFF, {"is": 1})
        self.assertGreaterEqual(session._MeshSerialSession__event_handler(test_event), 0)
        test_event = EventPacket("TEST other event packet", 0xFF, {"is": 2})
        self.assertGreaterEqual(session._MeshSerialSession__event_handler(test_event), 0)
        self.assertIsInstance(session.event_pop(), EventPacket)
        self.assertIsInstance(session.event_pop(), EventPacket)
        self.assertIsNone(session.event_pop())

    def test_chore(self):
        session = self.session
        self.assertEqual(session.device_port_get(), "dump_serial")

    def test_send(self):
        session = self.session
        test_packet = CommandPacket(0x13, bytearray([0x12, 0x11, 0x00]))
        self.assertEqual(session.send(test_packet), b'\x04\x13\x12\x11\x00')

if __name__ == '__main__':
    unittest.main()
