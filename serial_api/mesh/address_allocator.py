from collections import deque
import threading

def bit_ceil(x):
    import math
    return math.ceil(math.log2(x))

class AddressMgr(object):
    def __init__(self, low, high):
        self.low_address = low
        self.high_address = high
        self.address_spaces = []
        self.lock = threading.RLock()

    def hold(self):
        pass

    def release(self):
        pass

class UnicastAddressMgr(AddressMgr):
    def __init__(self, low, high):
        super().__init__(low, high)
        max_space_size_log = bit_ceil(self.high_address - self.low_address + 1)
        for _ in range(max_space_size_log):
            self.address_spaces.append(deque())

        next_address = self.low_address

        for space_index in range(len(self.address_spaces) - 1, 0 - 1, -1):
            size = 1 << space_index
            if self.high_address - next_address + 1 < size:
                continue
            self.release(next_address, size)
            next_address += size

    def merge_spaces(self):
        self.lock.acquire()
        for space_index in range(len(self.address_spaces) - 1):
            address_space = self.address_spaces[space_index]
            space_list = []
            size = 1 << space_index
            while len(address_space) > 0:
                space_list.append(address_space.pop())
            space_list.sort()

            while len(space_list) > 0:
                addr = space_list.pop(0)
                if len(space_list) > 0 and addr + size == space_list[0]:
                    space_list.pop(0)
                    self.release(addr, size << 1)
                else:
                    self.release(addr, size)

        self.lock.release()

    def release(self, addr, size):
        self.lock.acquire()
        self.address_spaces[bit_ceil(size)].append(addr)
        self.lock.release()

    def _hold(self, size):
        addr = None
        size_log = bit_ceil(size)
        if size_log < len(self.address_spaces):
            if len(self.address_spaces[size_log]) > 0:
                addr = self.address_spaces[size_log].popleft()
            else:
                addr = self._hold(size << 1)
                if addr is not None:
                    self.release(addr + (1 << size_log), (1 << size_log))
        return addr

    def hold(self, size):
        self.lock.acquire()
        addr = self._hold(size)
        if addr is None:
            self.merge_spaces()
            addr = self._hold(size)
        self.lock.release()

        return addr
