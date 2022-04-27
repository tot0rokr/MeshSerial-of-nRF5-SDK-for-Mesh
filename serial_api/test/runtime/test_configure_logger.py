import unittest

import logging

from runtime.configure_logger import configure_logger
from runtime.mesh_serial_session import MeshSerialSession
from test.dump_aci import DumpOption, DumpDevice, DumpApplicationConfig


class TestConfigureLogger(unittest.TestCase):
    def setUp(self):
        options = DumpOption()
        logger = configure_logger(options.log_level, options.devices[0].split("/")[-1])
        self.session = MeshSerialSession(DumpDevice(), logger, DumpApplicationConfig())
        self.session.logger.error("Test error")
        self.session.logger.warning("Test warn")
        self.session.logger.info("Test info")
        self.session.logger.debug("Test debug")

    def test_check_logger_singleton(self):
        options = DumpOption()
        logger = configure_logger(options.log_level, options.devices[0].split("/")[-1])
        self.assertIs(logger, self.session.logger)

if __name__ == '__main__':
    unittest.main()
