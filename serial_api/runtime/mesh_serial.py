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
    def __init__(self, opcode, cb=None, args=(), cond=None, timeout=5,
                       retransmit_count=3, retransmit_interval=1):
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

        self.net_handle = session.handle_mgr.get_net_handle(0)  # Default NetKey 0

        session.logger.info("{} session is provisioner".format(session_handle))

    def scan_start(self):
        session = self.provisioner.iaci
        self.provisioner.scan_start()
        session.logger.info("Scan start")

    def scan_stop(self):
        session = self.provisioner.iaci
        self.provisioner.scan_stop()
        session.logger.info("Scan stop")

    def device_list(self):
        session = self.provisioner.iaci
        self.provisioner.device_list()
        session.logger.info("Scan stop")

    def provision_node(self, uuid, key_index=0, name="Node", context_id=0, attention_duration_s=0):
        session = self.provisioner.iaci
        net_handle = session.handle_mgr.get_net_handle(key_index)
        provision_cb = lambda x: x['data']['unicast_address']
        provision_cond = lambda x: x['meta']['context_id'] == context_id
        self.provision_service = session.add_service('provision_complete', provision_cb, provision_cond)
        self.provisioner.provision(uuid, key_index, name, context_id, attention_duration_s)
        node_address = self.provision_service()
        session.handle_mgr.put_net_handle(net_handle)
        session.logger.debug("%04x node is provisioned", node_address)
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
