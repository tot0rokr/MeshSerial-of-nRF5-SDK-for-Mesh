import unittest

#  loader = unittest.TestLoader()

#  start_dir = 'test'
#  suite = loader.discover(start_dir)

from test.test_dump_aci import TestDumpACI
from test.runtime.test_mesh_serial_session import TestMeshSerialSession
from test.runtime.test_configure_logger import TestConfigureLogger

from test.runtime.test_device_mgr import TestDeviceMgr

def session_suite():
    suite = unittest.TestSuite()
    suite.addTests(TestDumpACI,
                   TestMeshSerialSession,
                   TestConfigureLogger)
    return suite

def api_suite():
    suite = unittest.TestSuite()
    suite.addTests(TestDeviceMgr)
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(session_suite())
    runner.run(api_suite())
    #  print(suite)
    #  runner.run(suite)
