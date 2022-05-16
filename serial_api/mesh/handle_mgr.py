from collections import deque
#  from queue import Queue
import threading

class HandleMgr(object):
    class HandleAllocator(object):
        def __init__(self, nr):
            self.handle_max = nr
            self.handles = [None for _ in range(nr)]
            self.waiters = deque()

        def get_handle(self, value):
            if value in self.handles:
                return self.handles.index(value)
            return self.set_handle(value)

        def set_handle(self, value):
            if not None in self.handles or len(self.waiters) > 0:
                waiter = threading.Event()
                self.waiters.append(waiter)
                waiter.wait()
            index = self.handles.index(None)
            self.handles[index] = value
            return index

        def reset_handle(self, handle):
            self.handles[handle] = None
            try:
                waiter = self.waiters.popleft()
                waiter.set()
            except:
                pass

            
    def __init__(self):
        self.devkey_allocator  = self.HandleAllocator(10)   # value: unicast_address
        self.appkey_allocator  = self.HandleAllocator(8)    # value: appkey_index
        self.netkey_allocator  = self.HandleAllocator(8)    # value: netkey_index
        self.addrkey_allocator = self.HandleAllocator(32)   # value: address

    def devkey_handle_set(self, value):
        return self.devkey_allocator.get_handle(value) + 8

    def devkey_handle_reset(self, handle):
        self.devkey_allocator.reset_handle(handle + 8)

    def appkey_handle_set(self, value):
        return self.appkey_allocator.get_handle(value)

    def appkey_handle_reset(self, handle):
        self.appkey_allocator.reset_handle(handle)

    def netey_handle_set(self, value):
        return self.netkey_allocator.get_handle(value)

    def netkey_handle_reset(self, handle):
        self.netkey_allocator.reset_handle(handle)

    def addrkey_handle_set(self, value):
        return self.addrkey_allocator.get_handle(value)

    def addrkey_handle_reset(self, handle):
        self.addrkey_allocator.reset_handle(handle)


