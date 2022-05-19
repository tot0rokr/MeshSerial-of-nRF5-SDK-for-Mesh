from collections import deque
import threading

class HandleAllocator(object):
    def __init__(self, nr):
        self.handles = [None for _ in range(nr)] # [target, handle, ref_count]
        self.semaphore = threading.Semaphore(nr)
        self.lock = threading.RLock()
        self.resources = deque(maxlen=nr) # self.handles indexes queue
        for i in range(nr):
            self.resources.append(i)

    def __get_handle(self, target):
        ret = None
        for elm in self.handles:
            if elm is not None and elm[0] == target:
                elm[2] += 1
                ret = elm[1]
                break
        return ret

    def set_handle(self, target, cb):
        self.lock.acquire()
        ret = self.__get_handle(target)
        if ret is None:
            self.semaphore.acquire()
            index = self.resources.popleft()
            ret = cb(target)
            self.handles[index] = [target, ret, 1]
        self.lock.release()
        return ret

    def reset_handle(self, handle, cb):
        self.lock.acquire()
        ret = None
        for i in range(len(self.handles)):
            elm = self.handles[i]
            if elm is not None and elm[1] == handle:
                elm[2] -= 1
                if elm[2] <= 0:
                    self.handles[i] = None
                    ret = cb(handle)
                    self.resources.append(i)
                    self.semaphore.release()
                break
        self.lock.release()
        return ret

class HandleMgr(object):
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


