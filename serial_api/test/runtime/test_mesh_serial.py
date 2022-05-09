import unittest

from runtime.mesh_serial import MeshSerial
from test.dump_aci import DumpOption, DumpApplicationConfig, DumpDevice, DumpModel

from aci.aci_evt import Event, CmdRsp, MeshMessageReceivedUnicast
from aci.aci_utils import EventPacket, CommandPacket

class TestMeshSerial(unittest.TestCase):
    def setUp(self):
        self.serial = MeshSerial(DumpOption(), DumpApplicationConfig())
        self.device_handle = self.serial.create_device(DumpDevice())
        self.command={'model':'SimpleOnOffClient', 'op':'get', 'arg': None}

    @unittest.skip("depending on serial device")
    def test_keys(self):
        address_handle = self.serial._get_key_handles(application=0, address=0xFFFF)

    #  def test_get_callee(self):
        #  callee = self.serial.get_callee(self.command)
        #  self.assertTrue(callable(callee))

    def test_run_model(self):
        # Test only single model and appkey is only one
        session_handle = self.serial.create_session(self.device_handle, None)
        with self.assertLogs() as cm:
            self.serial.run_model(session_handle=session_handle,
                                  application=0, address=0xFFFF,
                                  command=self.command)
            self.assertRegex(str(cm.output), "Sending opcode")


    def test_cmdrsp_queue(self):
        session_handle = self.serial.create_session(self.device_handle, prov_db=None)
        session = self.serial.session_mgr.session(session_handle)
        
        with self.assertLogs() as cm:
            for msg in [[0xAA, 0xBB], [0xCC, 0xDD], [0xEE, 0xFF]]:
                test_event = CmdRsp(bytearray([0x02, 0, *msg]))
                self.assertGreaterEqual(session._MeshSerialSession__event_handler(test_event), 0)
                self.assertRegex(str(cm.output), str(msg))
        for msg in [[0xAA, 0xBB], [0xCC, 0xDD], [0xEE, 0xFF]]:
            event = session.cmdrsp_queue.pop(0)
            self.assertEqual(event._data, {'data':bytearray(msg)})

    def test_event_queue(self):
        session_handle = self.serial.create_session(self.device_handle, prov_db=None)
        session = self.serial.session_mgr.session(session_handle)
        session.model_add(DumpModel())

        import struct
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
        event = session.event_queue.pop(0)
        self.assertEqual(event['data'], {'a': 12, 'b': 13, 'c': 14, 'd': 15})
        #  self.assertEqual(session.event_queue.pop(0)._data, {'data':bytearray(msg)})

if __name__ == '__main__':
    unittest.main()
