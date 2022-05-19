from runtime.mesh_serial_session import MeshSerialSession
from runtime.device_mgr import DeviceMgr
from runtime.session_mgr import SessionMgr

import aci.aci_cmd as cmd

from mesh.provisioning import Provisioner, Provisionee  # NOQA: ignore unused import

class Command(object):
    def __init__(self, model_name, op, arg):
        self.model_name = model_name
        self.op = op
        self.arg = arg

# TODO: Need to change
class Service(object):
    def __init__(self, opcode, cb, cond=None):
        self.opcode = opcode
        self.cb = cb
        self.cond = cond

class MeshSerial(object):
    def __init__(self, options, config):
        self.options = options
        self.config = config
        self.device_mgr = DeviceMgr()
        self.session_mgr = SessionMgr(self.options, self.config, self.device_mgr)
        self.model_handles = list()

    def create_device(self, device):
        return self.device_mgr.create_device(device)

    def create_session(self, device_handle, prov_db):
        return self.session_mgr.create_session(device_handle, prov_db)

    def start_session(self, session_handle):
        session = self.session_mgr.session(session_handle)
        session.start()
        session.logger.info("{} session start".format(session_handle))

    def initialize_provisioner(self, session_handle, db):
        session = self.session_mgr.session(session_handle)
        session.start()
        self.provisioner = Provisioner(session, db)

        self.net_handle = session.handle_mgr.get_net_handle(0)

        complete_composition_cb = lambda x: x
        self.composition_data_get_service = session.add_service('02', complete_composition_cb, None)

        completed_provision_cb = lambda x: x['data']['unicast_address']
        self.provision_service = session.add_service('provision_complete', completed_provision_cb, None)

        session.logger.info("{} session is provisioner".format(session_handle))

    def compose_node(self, node_address):
        session = self.provisioner.iaci
        message = Command('ConfigurationClient', 'composition_data_get', None)
        app_handle = session.handle_mgr.get_app_handle(-node_address)
        addr_handle = session.handle_mgr.get_address_pub_handle(node_address)
        session.run_model(app_handle, addr_handle, message)
        composition_data = self.composition_data_get_service()
        session.handle_mgr.put_address_pub_handle(addr_handle)
        session.handle_mgr.put_app_handle(app_handle)
        session.logger.debug("{} node is configured initially".format(node_address))
        #  print(composition_data)

    def provision_node(self, uuid, name="Node"):
        self.provisioner.provision(uuid=uuid, name=name)
        node_address = self.provision_service()
        self.provisioner.iaci.logger.debug("{} node is provisioned".format(node_address))
        return node_address

    def run_model(self, session_handle, application, address, command, service=None):
        session = self.session_mgr.session(session_handle)
        if service is not None:
            service_service = session.add_service(service['opcode'], service['cb'], service['cond'])
        else:
            service_service = lambda *args: None
        if 'arg' in command:
            arg = command['arg']
        else:
            arg = None
        message = Command(command['model'], command['op'], arg)


        app_handle = session.handle_mgr.get_app_handle(application)
        addr_handle = session.handle_mgr.get_address_pub_handle(address)

        #  test_filter = lambda x: x['meta']['src'] == address
        #  test_filter = session.add_service('804a', None, test_filter)
        session.run_model(app_handle, addr_handle, message)


        #  ack_handler = lambda x: x
        #  cmdrsp_serv = session.add_service(command['op'], ack_handler, None)
        ret = service_service()
        session.handle_mgr.put_app_handle(app_handle)
        session.handle_mgr.put_address_pub_handle(addr_handle)


        if service is not None:
            session.remove_service(service['opcode'], service_service)

        return ret

