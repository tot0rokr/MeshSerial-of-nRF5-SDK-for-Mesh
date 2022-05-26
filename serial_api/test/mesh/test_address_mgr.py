import unittest

from mesh.address_mgr import AddressMgr, UnicastAddressMgr

def bit_ceil(x):
    import math
    return math.ceil(math.log2(x))

class TestAddressMgr(unittest.TestCase):
    def setUp(self):
        self.low = 19
        self.high = 2222
        self.mgr = UnicastAddressMgr(self.low, self.high) # chd 2204개(12bit) [0001 0011, 1000 1010 1110]
        self.devices = list()
        self.devices.append((3, self.mgr.hold(3)))
        self.devices.append((22, self.mgr.hold(22)))
        self.devices.append((300, self.mgr.hold(300)))
        self.devices.append((7, self.mgr.hold(7)))
        #  for q in self.mgr.address_spaces:
            #  print(q)
        #  print("-----------------")

    def test_merge_spaces(self):
        for d in self.devices:
            self.mgr.release(d[1], d[0])
            #  for q in self.mgr.address_spaces:
                #  print(q)
            #  print("-----------------")

        self.assertEqual(self.mgr.hold(2000), 19)
        #  for q in self.mgr.address_spaces:
            #  print(q)
        #  print("-----------------")

        self.assertEqual(self.mgr.hold(110), 2067)
        #  for q in self.mgr.address_spaces:
            #  print(q)
        #  print("-----------------")



if __name__ == '__main__':
    unittest.main()
