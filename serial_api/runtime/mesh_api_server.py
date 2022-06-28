from mesh import types as mt                            # NOQA: ignore unused import
from mesh.database import MeshDB                        # NOQA: ignore unused import

from runtime.local_mesh_serial import LocalMeshSerial

import threading
#  import concurrent.futures
from multiprocessing.connection import Listener

# Add api---------------------------
from functools import partial

import runtime.api.config
import runtime.api.generic_level
import runtime.api.provision
# ----------------------------------

class MeshAPIServer(object):
    def __init__(self, options, db_name, provisioner_on=True):
        self.address = options.address
        self.db = MeshDB(db_name)
        self.provisioner_on = provisioner_on
        self.mesh = LocalMeshSerial(options, self.db)
        self.worker = threading.Thread(target=self.runner)
        self.worker.daemon = True
        self.is_running = threading.Event()
        self.__is_terminated = False
        #  self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

        # Set Provisioner API and Add ConfigurationClient API
        if self.provisioner_on:
            self.mesh_manager_handle = self.mesh.connect_session(0)
            self.mesh.set_provisioner(self.mesh_manager_handle)
            self.update_module(runtime.api.provision)
            self.mesh.start_session(self.mesh_manager_handle)
            self.update_module(runtime.api.config)

        # Add modules API
        self.update_module(runtime.api.generic_level)

        # Start worker
        self.start()

    def start(self):
        self.is_running.set()
        if self.worker.ident is None:
            self.worker.start()

    def stop(self):
        self.is_running.clear()

    def __del__(self):
        self.stop()
        self.__is_terminated = True
        del self.mesh
        super().__del__()

    def update_module(self, module):
        for m in dir(module):
            if not m.startswith('_'):
                if hasattr(self, m):
                    delattr(self, m)
                setattr(self, m, partial(getattr(module, m), self))

    def runner(self):
        with Listener(self.address, authkey=b'1234') as listener:
            while not self.__is_terminated:
                self.is_running.wait()
                with listener.accept() as conn:
                    print('connection accepted from', listener.last_accepted)
                    func_name, args, kwargs = conn.recv()
                    func = getattr(self, func_name)
                    ret = func(*args, **kwargs)
                    conn.send(ret)
