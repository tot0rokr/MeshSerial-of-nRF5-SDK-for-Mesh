import unittest

from runtime.device_mgr import DeviceMgr
from runtime.session_mgr import SessionMgr
from runtime.model_mgr import ModelMgr
from test.dump_aci import DumpOption, DumpDevice, DumpApplicationConfig
from mesh.access import Opcode

class TestModelMgr(unittest.TestCase):
    def setUp(self):
        self.mgr = ModelMgr(None)
        self.device_mgr = DeviceMgr()
        self.session_mgr = SessionMgr(DumpOption(), DumpApplicationConfig(), self.device_mgr)
        self.device_handle = self.device_mgr.create_device(device=DumpDevice())
        self.session_handle = self.session_mgr.create_session(device_handle=self.device_handle)
        self.session = self.session_mgr.session(self.session_handle)
        #  self.model_names = ['ConfigurationClient',
                            #  'SimpleOnOffClient',
                            #  'GenericOnOffClient',
                            #  'GenericLevelClient',
                            #  'GenericDefaultTransitionTimeClient',
                            #  'GenericPowerOnOffClient',
                            #  'GenericPowerLevelClient']
        self.model_names = self.mgr.all_model_names()
        self.model_handles = list(map(lambda x: self.mgr.model_handle(x),
                                      self.model_names))
        print(self.model_handles)

    def test_models(self):
        model = self.mgr.model(len(self.model_names))
        self.assertIsNone(model)
        for model_handle in self.model_handles:
            with self.subTest(handle=model_handle):
                model = self.mgr.model(model_handle)
                self.assertIsNotNone(model)
                self.session.model_add(model)
                model.publish_set(0xFF, 0xFF)
                with self.assertLogs() as cm:
                    if hasattr(model, 'node_reset'):
                        model.node_reset()
                    elif hasattr(model, 'get'):
                        model.get()
                self.assertRegex(str(cm.output), "Sending opcode")
if __name__ == '__main__':
    unittest.main()
