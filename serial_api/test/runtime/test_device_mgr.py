import unittest

from runtime.device_mgr import DeviceMgr
from test.dump_aci import DumpOption, DumpDevice, CommandPacket, EventPacket

class TestDeviceMgr(unittest.TestCase):
    def setUp(self):
        self.mgr = DeviceMgr()
        self.options = DumpOption()
        self.device_handles = list()
        for dev_com in self.options.devices:
            self.device_handles.append(self.mgr.create_device(device=DumpDevice(device_name=dev_com)))

    def test_device(self):
        options = self.options
        device_handles = self.device_handles
            #  device_handle = self.mgr.create_device(Uart(port=dev_com,
                                                        #  baudrate=options.baudrate,
                                                        #  device_name=dev_com.split("/")[-1]))
        device = self.mgr.device(device_handle=device_handles[0])
        self.assertIs(device.device_name, options.devices[0])
        self.assertIsNone(device.write_aci_cmd("NOT CommandPacket data"))
        test_packet = CommandPacket(0x13, bytearray([0x12, 0x11, 0x00]))
        self.assertIsNotNone(device.write_aci_cmd(test_packet))

        device1 = self.mgr.device(device_handle=device_handles[1])
        self.assertIs(device1.device_name, options.devices[1])
        device1.add_packet_recipient(lambda event: self.assertEqual(event._opcode, 0x82))
        test_event = EventPacket("Echo", 0x82, {"key": [0, 1], "index": 42})
        device1.process_packet(test_event)

    def test_hold_device(self):
        options = self.options
        device_handles = self.device_handles
        device = self.mgr.hold_device(device_handle=device_handles[0])
        self.assertIsNotNone(device)
        self.assertIs(device.device_name, options.devices[0])
        device1 = self.mgr.hold_device(device_handle=device_handles[1])
        self.assertIsNotNone(device1)
        self.assertIs(device1.device_name, options.devices[1])
        device2 = self.mgr.hold_device(device_handle=device_handles[1])
        self.assertIsNone(device2)
        self.mgr.release_device(device_handle=device_handles[1])
        device3 = self.mgr.hold_device(device_handle=device_handles[1])
        self.assertIsNotNone(device3)
        self.assertIs(device3.device_name, options.devices[1])

    def test_check_device_mgr_singleton(self):
        mgr = DeviceMgr()
        self.assertIs(self.mgr, mgr)

if __name__ == '__main__':
    unittest.main()
