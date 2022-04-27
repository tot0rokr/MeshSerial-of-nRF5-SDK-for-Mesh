class DeviceMgr(object):
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = super().__new__(cls, *args, **kwargs)
            cls.__instance.__devices = list()
        return cls.__instance

    def create_device(self, device):
        self.__devices.append({'device':device, 'inuse':False})
        return len(self.__devices) - 1

    #  def alloc_device(self):
        #  return hold_device(filter(lambda x: x[device_handle]['inuse'] == False,
                                  #  self.__devices_))

    def device(self, device_handle):
        return self.__devices[device_handle]['device']

    def hold_device(self, device_handle):
        if self.__devices[device_handle]['inuse'] == True:
            return None
        else:
            self.__devices[device_handle]['inuse'] = True
            return self.__devices[device_handle]['device']

    def release_device(self, device_handle):
        if self.__devices[device_handle]['inuse'] == True:
            self.__devices[device_handle]['inuse'] = False
