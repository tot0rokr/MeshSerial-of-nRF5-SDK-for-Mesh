import unittest

from runtime.mesh_serial import MeshSerial
from test.dump_aci import DumpOption, DumpApplicationConfig, DumpDevice, DumpModel

from aci.aci_cmd import Echo
from aci.aci_evt import Event, CmdRsp, MeshMessageReceivedUnicast, DeviceEchoRsp
from aci.aci_utils import EventPacket, CommandPacket

import time

@unittest.skip("Deprecated")
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

    def test_service(self):
        session_handle = self.serial.create_session(self.device_handle, prov_db=None)
        session = self.serial.session_mgr.session(session_handle)
        session.start()


    @unittest.skip("depending on serial device")
    def test___send_commands(self):
        session_handle = self.serial.create_session(self.device_handle, prov_db=None)
        session = self.serial.session_mgr.session(session_handle)

        cmd = Echo("Hello world")
        send_commands = getattr(session, "_" + session.__class__.__name__ + "__send_commands")
        send_commands(cmd)

if __name__ == '__main__':
    unittest.main()
