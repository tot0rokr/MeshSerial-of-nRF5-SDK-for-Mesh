class DeviceMgr(object):
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance.__devices = dict()
            cls.__instance.__next_device_handle = 0
        return cls.__instance

    def create_device(self, device):
        self.__devices[self.__next_device_handle] = {'device':device, 'inuse':False}
        self.__next_device_handle += 1
        return self.__next_device_handle - 1

    def remove_device(self, device_handle):
        if not self.__valid_handle(device_handle) \
            or self.__devices[device_handle]['inuse'] == True:
            return
        del self.__devices[device_handle]

    def __valid_handle(self, device_handle):
        return device_handle in self.__devices

    def device(self, device_handle):
        if not self.__valid_handle(device_handle):
            return None
        else:
            return self.__devices[device_handle]['device']

    def hold_device(self, device_handle):
        if not self.__valid_handle(device_handle) \
            or self.__devices[device_handle]['inuse'] == True:
            return None
        else:
            self.__devices[device_handle]['inuse'] = True
            return self.__devices[device_handle]['device']

    def release_device(self, device_handle):
        if not self.__valid_handle(device_handle):
            return
        if self.__devices[device_handle]['inuse'] == True:
            self.__devices[device_handle]['inuse'] = False
