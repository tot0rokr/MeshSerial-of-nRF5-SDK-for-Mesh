import unittest

#  loader = unittest.TestLoader()

#  start_dir = 'test'
#  suite = loader.discover(start_dir)

from test.test_dump_aci import TestDumpACI
from test.runtime.test_mesh_serial_session import TestMeshSerialSession
from test.runtime.test_configure_logger import TestConfigureLogger

from test.runtime.test_device_mgr import TestDeviceMgr
from test.runtime.test_session_mgr import TestSessionMgr
from test.runtime.test_model_mgr import TestModelMgr

def session_suite():
    suite = unittest.TestSuite()
    suite.addTests(TestDumpACI,
                   TestMeshSerialSession,
                   TestConfigureLogger)
    return suite

def mgr_suite():
    suite = unittest.TestSuite()
    suite.addTests(TestDeviceMgr)
    suite.addTests(TestSessionMgr)
    suite.addTests(TestModelMgr)
    return suite

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(session_suite())
    runner.run(api_suite())
    #  print(suite)
    #  runner.run(suite)
