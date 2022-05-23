from runtime.mesh_serial_session import MeshSerialSession
from runtime.device_mgr import DeviceMgr
from runtime.session_mgr import SessionMgr

import aci.aci_cmd as cmd

from mesh.provisioning import Provisioner, Provisionee  # NOQA: ignore unused import

class Command(object):
    def __init__(self, model_name, op, args=()):
        self.model_name = model_name
        self.op = op
        self.args = args

    def __str__(self):
        return 'model: %s, op: %s, args: %r' % (self.model_name,
                                                self.op,
                                                self.args)

# TODO: Need to change
class Service(object):
    def __init__(self, opcode, cb=None, cond=None, timeout=10, args=(),
                       retransmit_count=0, retransmit_interval=3):
        self.opcode = opcode
        self.cb = cb
        self.cond = cond
        self.timeout = timeout
        self.args = args
        self.retransmit_count = retransmit_count
        self.retransmit_interval = retransmit_interval

class MeshSerial(object):
    def __init__(self, options, config):
        self.options = options
        self.config = config
        self.device_mgr = DeviceMgr()
        self.session_mgr = SessionMgr(self.options, self.config, self.device_mgr)
        self.model_handles = list()
        self.provisioner = None

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
        #  self.app_handle = session.handle_mgr.get_app_handle(0)

        #  complete_composition_cb = lambda x: x
        #  self.composition_data_get_service = session.add_service('02', complete_composition_cb, None)

        completed_provision_cb = lambda x: x['data']['unicast_address']
        self.provision_service = session.add_service('provision_complete', completed_provision_cb, None)

        session.logger.info("{} session is provisioner".format(session_handle))

    #  def compose_node(self, node_address):
        #  session = self.provisioner.iaci
        #  message = Command('ConfigurationClient', 'composition_data_get', None)
        #  app_handle = session.handle_mgr.get_app_handle(-node_address)
        #  addr_handle = session.handle_mgr.get_address_pub_handle(node_address)
        #  session.send_message(app_handle, addr_handle, message)
        #  try:
            #  composition_data = self.composition_data_get_service(10)
            #  session.logger.info("{} node is configured initially".format(node_address))
        #  except TimeoutError as e:
            #  session.logger.info("{} node is not configured".format(node_address))
            #  session.logger.error(e)
            #  raise
        #  finally:
            #  session.handle_mgr.put_address_pub_handle(addr_handle)
            #  session.handle_mgr.put_app_handle(app_handle)

    def provision_node(self, uuid, name="Node"):
        self.provisioner.provision(uuid=uuid, name=name)
        node_address = self.provision_service()
        self.provisioner.iaci.logger.debug("%04x node is provisioned", node_address)
        return node_address

    def run_model(self, session_handle, application, address, message, service=None):
        session = self.session_mgr.session(session_handle)

        if service is not None:
            service_service = session.add_service(service.opcode, service.cb, service.cond)

        app_handle = session.handle_mgr.get_app_handle(application)
        addr_handle = session.handle_mgr.get_address_pub_handle(address)

        if service is not None:
            retransmit_count = service.retransmit_count
        try:
            while 1 + retransmit_count > 0:
                session.logger.debug("waiting send message")
                try:
                    session.send_message(app_handle, addr_handle, message)
                except TimeoutError as e:
                    session.logger.info("waiting send message timeout: address: %04x %s", address, message)
                    session.logger.error(e)
                    raise

                session.logger.debug("waiting service")
                try:
                    if service is not None:
                        if retransmit_count > 0:
                            timeout = service.retransmit_interval
                        else:
                            timeout = service.timeout
                        ret = service_service(timeout, *service.args)
                    else:
                        ret = None
                    retransmit_count = -1
                except TimeoutError as e:
                    if retransmit_count > 0:
                        retransmit_count -= 1
                        continue
                    session.logger.info("waiting service timeout: address: %04x %s", address, message)
                    session.logger.error(e)
                    raise
        except TimeoutError:
            raise
        finally:
            session.handle_mgr.put_address_pub_handle(addr_handle)
            session.handle_mgr.put_app_handle(app_handle)
            if service is not None:
                session.remove_service(service.opcode, service_service)

        return ret
