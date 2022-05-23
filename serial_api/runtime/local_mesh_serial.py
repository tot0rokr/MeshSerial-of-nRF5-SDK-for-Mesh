from runtime.mesh_serial_interface import MeshSerialInterface
from runtime.mesh_serial import Command, Service, MeshSerial
from aci.aci_uart import Uart
from aci.aci_config import ApplicationConfig
import mesh.types as mt
import os
import sys

#  STATUS_UNKNOWN = 0x00
#  STATUS_PROVISIONED = 0x01
#  STATUS_COMPOSED = 0x02
#  STATUS_CONFIG_COMPLETE = 0x03

class LocalMeshSerial(MeshSerialInterface):
    def __init__(self, options, db, logger=None):
        CONFIG = ApplicationConfig(
            header_path=os.path.join(os.path.dirname(sys.argv[0]),
                                     ("../nrf5_SDK_for_Mesh_v5.0.0_src/examples/serial/include/"
                                      + "nrf_mesh_config_app.h")))
        mesh = MeshSerial(options, CONFIG)
        self.logger = logger
        super().__init__(mesh, options, db)
        for dev in self.options.devices:
            self.device_handles.append(
                    self.mesh.create_device(
                        Uart(port=dev,
                             baudrate=options.baudrate,
                             device_name=dev.split("/")[-1])))

    def __del__(self):
        for dev in self.device_handles:
            self.mesh.device_mgr.remove_device(dev)
        for ses in self.session_handles:
            self.session_mgr.remove_session(ses)

    def connect_session(self, device_index):
        session_handle = self.mesh.create_session(self.device_handles[device_index], self.db)
        self.session_handles.append(session_handle)
        return session_handle

    def set_provisioner(self, session_handle):
        self.mesh_manager_handle = session_handle
        self.mesh.initialize_provisioner(session_handle, self.db)

    def start_session(self, session_handle):
        self.mesh.start_session(session_handle)

    def register_application(self, application):
        self.applications.append(application)

    def register_node(self, node_address):
        if not node_address in self.nodes:
            if self.__get_node(node_address) is not None:
                self.nodes.append(node_address)
            else:
                raise RuntimeError("%04x node is not found" % node_address)

    def provision_node(self, uuid, name="Node"):
        addr = self.mesh.provision_node(uuid, name)
        self.nodes.append(addr)
        return addr

    def __get_node(self, addr):
        for node in self.db.nodes:
            if node.unicast_address == addr:
                return node
        return None

    def __get_node_address(self, element_address):
        for node in self.db.nodes:
            beg = node.unicast_address
            end = beg + len(node.elements)
            if beg <= element_address < end:
                return beg
        return None

    def appkey_add(self, address, application):
        command = {'model_name':'ConfigurationClient',
                   'op':'appkey_add',
                   'args':(application,)}
        service = {'opcode':'8003', 'cond':lambda x: x['meta']['src'] == address, 'timeout':5,
                   'retransmit_count':3, 'retransmit_interval':1}
        try:
            self.run_model(self.mesh_manager_handle,
                           -address,
                           address,
                           command,
                           service)
        except TimeoutError:
            return False
        return True

    def model_app_bind(self, element_address, application, model_id):
        address = self.__get_node_address(element_address)
        command = {'model_name':'ConfigurationClient',
                   'op':'model_app_bind',
                   'args':(element_address, application, mt.ModelId(model_id))}
        service = {'opcode':'803e', 'cond':lambda x: x['meta']['src'] == address, 'timeout':5,
                   'retransmit_count':3, 'retransmit_interval':1}
        if address is None:
            return False
        try:
            self.run_model(self.mesh_manager_handle,
                           -address,
                           address,
                           command,
                           service)
        except TimeoutError:
            return False
        return True

    def compose_node(self, address):
        #  if target[1] != STATUS_PROVISIONED:
        if self.__get_node(address) is None:
            return False
        command = {'model_name':'ConfigurationClient',
                   'op':'composition_data_get'}
        service = {'opcode':'02', 'cond':lambda x: x['meta']['src'] == address, 'timeout':5,
                   'retransmit_count':3, 'retransmit_interval':1}
        try:
            composition_data = self.run_model(self.mesh_manager_handle,
                                              -address,
                                              address,
                                              command,
                                              service)
        except TimeoutError:
            return False
        #  target[1] = STATUS_COMPOSED
        return True


    def node_reset(self, address):
        command = {'model_name':'ConfigurationClient',
                   'op':'node_reset'}
        service = {'opcode':'804a', 'cond':lambda x: x['meta']['src'] == address, 'timeout':5,
                   'retransmit_count':3, 'retransmit_interval':1}
        try:
            self.run_model(self.mesh_manager_handle,
                           -address,
                           address,
                           command,
                           service)
        except TimeoutError:
            return False
        return True

    #  def __model_get(self, element_address, model_id):
        #  for node in self.prov_db.nodes:
            #  beg = node.unicast_address
            #  end = beg + len(node.elements)
            #  if beg <= element_address < end:
                #  index = int(element_address) - int(node.unicast_address)
                #  element = node.elements[index]
                #  for model in element.models:
                    #  if model.model_id == model_id:
                        #  return model

    def run_model(self, session_handle, application, address, command, service):
        message = Command(**command)
        if service is not None:
            _service = Service(**service)
        else:
            _service = None

        return self.mesh.run_model(session_handle,
                            application,
                            address,
                            message,
                            _service)
