import unittest

from mesh.handle_mgr import HandleMgr

import threading

import time

class TestHandleMgr(unittest.TestCase):
    def setUp(self):
        self.mgr = HandleMgr()
        self.result = [i for i in range(20)]
        for i in range(2):
            self.mgr.appkey_handle_set(i+1)
        for i in range(18, 20):
            self.mgr.appkey_handle_set(i+1)

    def __runner(self, i):
        starttime = time.time() + 0.2
        handle = self.mgr.appkey_handle_set(i)
        time.sleep(1)
        self.mgr.appkey_handle_reset(handle)
        self.result[i-1] = time.time() - starttime


    def test_handle_set(self):
        print("This test spends 3 secs")
        starttime = time.time() + 0.2
        keys = [i for i in range(1, 21)]
        threads = list()
        for i in range(20):
            threads.append(threading.Thread(target=self.__runner, args=(keys[i],)))

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        for i in range(20):
            with self.subTest(i=i):
                if i < 2 or i >= 18:
                    self.assertLess(self.result[i], 1)

        self.assertLess(time.time() - starttime, 3)

if __name__ == '__main__':
    unittest.main()
