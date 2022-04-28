import unittest

from runtime.device_mgr import DeviceMgr
from runtime.session_mgr import SessionMgr
from test.dump_aci import DumpOption, DumpDevice, CommandPacket, EventPacket, DumpApplicationConfig

class TestSessionMgr(unittest.TestCase):
    def setUp(self):
        self.device_mgr = DeviceMgr()
        self.mgr = SessionMgr(DumpOption(), DumpApplicationConfig(), self.device_mgr)
        self.device_handle = self.device_mgr.create_device(device=DumpDevice())

    def test_session(self):
        self.assertRaises(Exception, self.mgr.create_session, device_handle=999)
        session_handle = self.mgr.create_session(device_handle=self.device_handle)
        session = self.mgr.session(999)
        self.assertIsNone(session)
        session = self.mgr.session(session_handle)
        self.assertIsNotNone(session)

        session.event_filter_add([0xFF])
        self.assertIn(0xFF, session._event_filter)
        test_event = EventPacket("TEST event", 0xFF, {})
        self.assertLess(session._MeshSerialSession__event_handler(test_event), 0)

        test_packet = CommandPacket(0x13, bytearray([0x12, 0x11, 0x00]))
        self.assertEqual(session.send(test_packet), b'\x04\x13\x12\x11\x00')

        # Create session of in-used device_handle
        self.assertRaises(Exception, self.mgr.create_session, device_handle=self.device_handle)

    def test_remove_session(self):
        session_handle = self.mgr.create_session(device_handle=self.device_handle)
        session = self.mgr.session(session_handle)
        self.assertIsNotNone(session)
        self.assertIsNone(self.device_mgr.hold_device(self.device_handle))
        self.mgr.remove_session(session_handle)
        session = self.mgr.session(session_handle)
        self.assertIsNone(session)
        self.assertIsNotNone(self.device_mgr.hold_device(self.device_handle))

if __name__ == '__main__':
    unittest.main()
