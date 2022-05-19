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

import aci.aci_cmd as aci_cmd
class HandleMgr(object):
    def __init__(self, session, prov_db):
        self.session = session
        self.send = session.send
        self.prov_db = prov_db

        self.nethandle_allocator  = HandleAllocator(8)    # target: netkey_index
        self.apphandle_allocator  = HandleAllocator(8)    # target: appkey_index
        self.devhandle_allocator  = HandleAllocator(10)   # target: node_address
        self.addrhandle_allocator = HandleAllocator(32)   # target: address

        self.__net_add_handler = self.session.add_service(0x92, lambda x: x['data']['subnet_handle'], None)
        self.__net_delete_handler = self.session.add_service(0x94, lambda x: x['data']['subnet_handle'], None)

        self.__app_add_handler = self.session.add_service(0x97, lambda x: x['data']['appkey_handle'], None)
        self.__app_delete_handler = self.session.add_service(0x99, lambda x: x['data']['appkey_handle'], None)

        self.__dev_add_handler = self.session.add_service(0x9c, lambda x: x['data']['devkey_handle'], None)
        self.__dev_delete_handler = self.session.add_service(0x9d, lambda x: x['data']['devkey_handle'], None)

        self.__addr_pub_add_handler = self.session.add_service(0xa4, lambda x: x['data']['address_handle'], None)
        self.__addr_pub_remove_handler = self.session.add_service(0xa6, lambda x: x['data']['address_handle'], None)

    def get_net_handle(self, net):
        def __get_handle(net):
            self.send(aci_cmd.SubnetAdd(net, self.prov_db.find_netkey(net).key))
            return self.__net_add_handler()
        return self.nethandle_allocator.set_handle(net, __get_handle)

    def put_net_handle(self, handle):
        def __put_handle(handle):
            self.send(aci_cmd.SubnetDelete(handle))
            return self.__net_delete_handler()
        if self.nethandle_allocator.reset_handle(handle, __put_handle) != handle:
            raise RuntimeError("put_net_handle: handle: {}".format(handle))

    def get_app_handle(self, application):
        if application < 0: # device handle
            return self.get_device_handle(-application)
        else:
            def __get_handle(addr):
                net_handle = self.get_net_handle(self.prov_db.find_appkey(addr).bound_net_key)
                self.send(aci_cmd.AppkeyAdd(addr, net_handle, self.prov_db.find_appkey(addr).key))
                return self.__app_add_handler()
            return self.apphandle_allocator.set_handle(application, __get_handle)

    def put_app_handle(self, handle):
        if handle >= 8: # device handle (8~17)
            self.put_device_handle(handle)
        else: # appkey handle (0~7)
            def __put_handle(handle):
                net_handle = self.get_net_handle(self.prov_db.find_appkey(addr).bound_net_key)
                self.put_net_handle(net_handle)
                self.put_net_handle(net_handle)
                self.send(aci_cmd.AppkeyDelete(handle))
                return self.__app_delete_handler()
            if self.apphandle_allocator.reset_handle(handle, __put_handle) != handle:
                raise RuntimeError("put_app_handle: handle: {}".format(handle))

    def get_device_handle(self, node_address):
        def __get_handle(addr):
            # TODO: Any idea need to allow all netkeys.
            #       Devkey is mapped to all netkey. Currently, 0 is enough as default.
            self.send(aci_cmd.DevkeyAdd(addr, 0, self.prov_db.find_devkey(addr)))
            return self.__dev_add_handler()

        return self.devhandle_allocator.set_handle(node_address, __get_handle)

    def put_device_handle(self, handle):
        def __put_handle(handle):
            self.send(aci_cmd.DevkeyDelete(handle))
            return self.__dev_delete_handler()

        if self.devhandle_allocator.reset_handle(handle, __put_handle) != handle:
            raise RuntimeError("put_device_handle: handle: {}".format(handle))

    def get_address_pub_handle(self, address):
        def __get_handle(addr):
            self.send(aci_cmd.AddrPublicationAdd(addr))
            return self.__addr_pub_add_handler()

        return self.addrhandle_allocator.set_handle(address, __get_handle)

    def put_address_pub_handle(self, handle):
        def __put_handle(handle):
            self.send(aci_cmd.AddrPublicationRemove(handle))
            return self.__addr_pub_remove_handler()

        if self.addrhandle_allocator.reset_handle(handle, __put_handle) != handle:
            raise RuntimeError("put_device_handle: handle: {}".format(handle))
