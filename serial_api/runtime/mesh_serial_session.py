from aci.aci_utils import STATUS_CODE_LUT
import aci.aci_cmd as aci_cmd
import aci.aci_evt as aci_evt

from mesh import access

from runtime.model_mgr import ModelMgr
from mesh.handle_mgr import HandleMgr
from collections import deque
import threading
import time

class ServiceHandler(object):
    def __init__(self, func, cond, destructor=None):
        self.event = threading.Event()
        self.func = func
        if cond is None:
            self.cond = lambda *args: True
        else:
            self.cond = cond
        self.data = None
        self.is_available = True
        self.destructor = destructor #RFU

    def __del__(self):
        if self.destructor is not None:
            self.destructor(self)

    def __call__(self, timeout=None, *args):
        self.event.wait(timeout)
        if not self.event.is_set():
            raise TimeoutError("It does receive any response for timeout")
        data, self.data = self.data, None
        self.event.clear()
        if callable(self.func):
            return self.func(data, *args)
        return None

    def filter(self, *args):
        #  print(*args)
        return self.cond(*args) and self.data is None

    def put(self, data):
        self.data = data
        self.event.set()

class MeshSerialSession(threading.Thread):
    DEFAULT_APP_KEY = bytearray([0xAA] * 16)
    DEFAULT_SUBNET_KEY = bytearray([0xBB] * 16)
    DEFAULT_VIRTUAL_ADDRESS = bytearray([0xCC] * 16)
    DEFAULT_STATIC_AUTH_DATA = bytearray([0xDD] * 16)
    DEFAULT_LOCAL_UNICAST_ADDRESS_START = 0x0001

    def __init__(self, acidev, logger, config, prov_db, quantum=0.1, *args):
        super(MeshSerialSession, self).__init__()
        self.daemon = True

        self.acidev = acidev
        # TODO: This must be modified.
        #       Because device doesn't depend on the session.
        self.acidev.write_aci_cmd(aci_cmd.RadioReset())

        self.CONFIG = config
        self.logger = logger
        self.send = self.put_command
        self.model_mgr = ModelMgr(prov_db)
        self.model_handles = list()

        # Handling events
        self.cmdrsp_queue = deque()
        self.event_queue = deque()
        self.cmd_queue = deque()
        self.wake_up_worker = threading.Event()
        self.__quantum = int(quantum * 1000) # unit: milliseconds
        self.service_handlers = dict()

        # Increment the local unicast address range
        # for the next Meshserialsession instance
        self.local_unicast_address_start = (
            self.DEFAULT_LOCAL_UNICAST_ADDRESS_START)
        MeshSerialSession.DEFAULT_LOCAL_UNICAST_ADDRESS_START += (
            self.CONFIG.ACCESS_ELEMENT_COUNT)

        self.access = access.Access(self, self.local_unicast_address_start,
                                    self.CONFIG.ACCESS_ELEMENT_COUNT)
        self.model_add = self.access.model_add

        # Adding the packet recipient will start dynamic behavior.
        # We add it after all the member variables has been defined
        self.acidev.add_packet_recipient(self.__event_handler)

        self.handle_mgr = HandleMgr(self, prov_db)

        #  self.map_packet_send_rsp = [None for _ in range(1000)]
        #  self.map_tx_completed    = [None for _ in range(1000)]
        #  packet_send_cb      = lambda x: (self.map_packet_send_rsp[x['data']['serial_tid'] % 1000] = x['data']['token'])
        #  packet_send_service = self.add_service(0xAB, packet_send_cb, None)
        #  tx_complete_cb      = lambda x: (self.map_tx_completed[x['data']['token'] % 1000] = x['data']['token'])
        #  tx_complete_service = self.add_service('tx_complete', tx_complete_cb, None)
        self.map_packet_send_rsp = [None for _ in range(1000)]
        self.map_tx_completed    = [None for _ in range(1000)]
        def packet_send_cb(x):
            self.map_packet_send_rsp[x['data']['serial_tid'] % 1000] = x['data']['token']
        self.packet_send_service = self.add_service(0xAB, packet_send_cb, None)
        def tx_complete_cb(x):
            self.map_tx_completed[x['data']['token'] % 1000] = x['data']['token']
        self.tx_complete_service = self.add_service('tx_complete', tx_complete_cb, None)

    def __del__(self):
        self.join()
        del self.access
        del self.handle_mgr

    def get_model(self, model_name):
        model_handle = self.model_mgr.model_handle(model_name)
        model = self.model_mgr.model(model_handle)
        if model is None:
            return None
        if not model_handle in self.model_handles:
            self.model_add(model)
            self.model_handles.append(model_handle)
        return model

    def send_message(self, app_handle, addr_handle, message):
        model = self.get_model(message.model_name)
        if model is None:
            raise Exception("%s is not found" % message.model_name)
        op = getattr(model, message.op)

        model.publish_set(app_handle, addr_handle)

        if message.args is None:
            serial_tid = op()
        elif isinstance(message.args, dict):
            serial_tid = op(**message.args)
        elif isinstance(message.args, (list, tuple, set)):
            serial_tid = op(*message.args)
        else:
            raise Exception("send_message: Invalid Arguments of {}.{}".format(
                            message.model_name, message.op))

        self.packet_send_service(6)
        while self.map_packet_send_rsp[serial_tid % 1000] is None:
            time.sleep(0.2)
        token = self.map_packet_send_rsp[serial_tid % 1000]
        self.map_packet_send_rsp[serial_tid % 1000] = None

        self.tx_complete_service(6)
        while self.map_tx_completed[token % 1000] is None:
            time.sleep(0.2)
        self.map_tx_completed[token % 1000] = None
        self.logger.debug("complete send message")

    def event_filter_add(self, event_filter):
        pass # Deprecated

    def event_filter_remove(self, event_filter):
        pass # Deprecated

    def event_filter_disable(self):
        pass # Deprecated

    def event_filter_enable(self):
        pass # Deprecated

    def device_port_get(self):
        return self.acidev.serial.port

    def start(self):
        if self.ident is None:
            super().start()
        self.wake_up_worker.set()

    def stop(self):
        self.wake_up_worker.clear()

    def join(self):
        self.stop()
        if self.ident is not None:
            super().join()

    def __time_ms(self):
        return time.time_ns() // 1000000

    def __put(self, queue, x):
        queue.append(x)

    def put_command(self, cmd):
        self.__put(self.cmd_queue, cmd)

    def put_event(self, evt):
        self.__put(self.event_queue, evt)

    def put_command_response(self, rsp):
        self.__put(self.cmdrsp_queue, rsp)

    def __get(self, queue):
        return queue.popleft()

    def get_command(self):
        return self.__get(self.cmd_queue)

    def get_event(self):
        return self.__get(self.event_queue)

    def get_command_response(self):
        return self.__get(self.cmdrsp_queue)

    # This must be called before receiving message
    # Keep this order: run add_service -> receiving message -> call service_handler
    def add_service(self, opcode, func, cond, destructor=None):
        if not opcode in self.service_handlers:
            self.service_handlers[opcode] = deque()
        service_handler = ServiceHandler(func, cond, destructor)
        self.service_handlers[opcode].append(service_handler)
        return service_handler

    def remove_service(self, opcode, service_handler):
        try:
            self.service_handlers[opcode].remove(service_handler)
        except ValueError:
            self.aci.logger.error("remove_service: Service {}({}) is not registered.".format(opcode, service_handler))

    def run(self):
        while True:
            self.wake_up_worker.wait()
            self.__receive_command_responses()
            self.__receive_events()
            self.__send_commands()
            completed_time = self.__time_ms()
            sleep_time = (self.__quantum - completed_time % self.__quantum) / 1000
            time.sleep(sleep_time)

    def __send_commands(self):
        while True:
            try:
                cmd = self.get_command()
            except IndexError:
                break

            if hasattr(aci_cmd, cmd.__class__.__name__):
                self.acidev.write_aci_cmd(cmd)
            else:
                raise RuntimeError("%s aci command is not defined" % cmd.__class__.__name__)

    def __receive_command_responses(self):
        while True:
            try:
                rsp = self.get_command_response()
            except IndexError:
                break

            # Command response must be received by one request.
            if not rsp._opcode in self.service_handlers:
                self.logger.debug("receive_command_responses: Unknown response for %s is received",
                                 rsp._command_name)
                continue
            for svc in self.service_handlers[rsp._opcode]:
                data = {'opcode':rsp._opcode, 'data':rsp._data}
                if svc.filter(data):
                    svc.put(data)

    def __receive_events(self):
        while True:
            try:
                evt = self.get_event()
            except IndexError:
                break

            if not evt['opcode'] in self.service_handlers:
                self.logger.debug("receive_events: No handle for %s", evt['opcode'])
                continue    # No waiting for evt
            for svc in self.service_handlers[evt['opcode']]:
                if svc.filter(evt):
                    self.logger.debug("receive_events: %r", evt)
                    svc.put(evt)

    def __event_handler(self, event):
        if event._opcode == aci_evt.Event.DEVICE_STARTED:
            self.logger.info("Device rebooted.")

        elif event._opcode == aci_evt.Event.CMD_RSP:
            if event._data["status"] != 0:
                self.logger.error("{}: {}".format(
                    aci_cmd.response_deserialize(event),
                    STATUS_CODE_LUT[event._data["status"]]["code"]))
            else:
                data = aci_cmd.response_deserialize(event)
                text = str(data)
                if text == "None":
                    text = "Success"
                else:
                    self.put_command_response(data)
                self.logger.info(text)
        elif event._opcode == aci_evt.Event.MESH_TX_COMPLETE:
            self.put_event({'opcode':'tx_complete',
                            'meta': {},
                            'data': {'token':event._data['token']}})
        #  else:
            #  self.logger.debug("event_handler: " + str(event))
