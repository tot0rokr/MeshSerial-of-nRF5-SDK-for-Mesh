import unittest

from runtime.mesh_serial_session import MeshSerialSession
from aci.aci_cmd import Echo
from aci.aci_evt import Event, CmdRsp, MeshMessageReceivedUnicast
from aci.aci_utils import EventPacket, CommandPacket
from test.dump_aci import DumpLogger, DumpDevice, DumpApplicationConfig, DumpModel

import struct

class TestMeshSerialSession(unittest.TestCase):
    def setUp(self):
        pass

    def test_cmdrsp_queue(self):
        session = MeshSerialSession(DumpDevice(), DumpLogger("Dump"), DumpApplicationConfig(), None)

        for msg in [[0xAA, 0xBB], [0xCC, 0xDD], [0xEE, 0xFF]]:
            test_event = CmdRsp(bytearray([0x02, 0, *msg]))
            session._MeshSerialSession__event_handler(test_event)
            #  self.assertRegex(str(cm.output), str(msg))
        events = session.cmdrsp_queue
        for msg in [[0xAA, 0xBB], [0xCC, 0xDD], [0xEE, 0xFF]]:
            event = events.popleft()
            self.assertEqual(event._data, {'data':bytearray(msg)})
            #  print("%r" % event)

    def test_event_queue(self):
        session = MeshSerialSession(DumpDevice(), DumpLogger("Dump"), DumpApplicationConfig(), None)
        session.model_add(DumpModel())

        dst = struct.pack("H", session.local_unicast_address_start)

        # access handler
        test_event = MeshMessageReceivedUnicast(bytearray([0xAB, 0xCD]) + # src
                                                dst                     + # dst
                                                bytearray([0x00, 0x10     # appkey
                                                         , 0x10, 0x00     # netkey
                                                         , 0x99           # ttl
                                                         , 0x00           # adv_addr_type
                                                         , 0, 0, 0, 0, 0, 0 # adv_addr
                                                         , 0xF6           # rssi
                                                         , 0x04, 0x00     # actual_length
                                                         , 0xAA, 0xBB     # opcode
                                                         , 0x0C, 0x0D     # data
                                                         , 0x0E, 0x0F
                                                         ]))
        session.access._Access__event_handler(test_event)
        event = session.event_queue.popleft()
        self.assertEqual(event['data'], {'a': 12, 'b': 13, 'c': 14, 'd': 15})
        #  print("%r" % event)

    def test_chore(self):
        session = MeshSerialSession(DumpDevice(), DumpLogger("Dump"), DumpApplicationConfig(), None)
        self.assertEqual(session.device_port_get(), "dump_serial")

    def test_cmd_queue(self):
        session = MeshSerialSession(DumpDevice(), DumpLogger("Dump"), DumpApplicationConfig(), None)
        test_packet = CommandPacket(0x13, bytearray([0x12, 0x11, 0x00]))
        session.send(test_packet)
        cmd = session.cmd_queue.popleft()
        self.assertEqual(cmd.serialize(), b'\x04\x13\x12\x11\x00')

    def test___send_commands(self):
        session = MeshSerialSession(DumpDevice(), DumpLogger("Dump"), DumpApplicationConfig(), None)

        cmd = Echo("Hello world")
        session.send(cmd)
        send_commands = getattr(session, "_" + session.__class__.__name__ + "__send_commands")
        #  with self.assertLogs() as cm:
        send_commands()
        #  self.assertRegex(str(cm.output), "cmd: Hello world")

    def test_service_handler(self):
        session = MeshSerialSession(DumpDevice(), DumpLogger("Dump"), DumpApplicationConfig(), None)
        session.start()

        msg = [0xAA, 0xBB]
        cmdrsp = CmdRsp(bytearray([0x02, 0, *msg]))
        cmdrsp_event_handler = getattr(session, "_" + session.__class__.__name__ + "__event_handler")
        cmd_cb = lambda x: self.assertEqual(x['data'], {'data':bytearray(msg)})
        #  cmd = Echo("Hello world")
        #  session.send(cmd)
        cmdrsp_serv = session.add_service(0x02, cmd_cb, None)

        dst = struct.pack("H", session.local_unicast_address_start)
        test_event = MeshMessageReceivedUnicast(bytearray([0xAB, 0xCD]) + # src
                                                dst                     + # dst
                                                bytearray([0x00, 0x10     # appkey
                                                         , 0x10, 0x00     # netkey
                                                         , 0x99           # ttl
                                                         , 0x00           # adv_addr_type
                                                         , 0, 0, 0, 0, 0, 0 # adv_addr
                                                         , 0xF6           # rssi
                                                         , 0x04, 0x00     # actual_length
                                                         , 0xAA, 0xBB     # opcode
                                                         , 0x0C, 0x0D     # data
                                                         , 0x0E, 0x0F
                                                         ]))
        evt_cb = lambda x: self.assertEqual(x['data'], {'a': 12, 'b': 13, 'c': 14, 'd': 15})
        evt_serv = session.add_service("aabb", evt_cb, None)
        session.model_add(DumpModel())

        session.access._Access__event_handler(test_event)
        cmdrsp_event_handler(cmdrsp)

        cmdrsp_serv(6)
        evt_serv()

        session.stop()
        #  session.join()

@unittest.skip("Deprecated")
class TestMeshSerialSessionDeprecated(unittest.TestCase):
    def setUp(self):
        self.session = MeshSerialSession(DumpDevice(), DumpLogger("Dump"), DumpApplicationConfig(), None)

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
