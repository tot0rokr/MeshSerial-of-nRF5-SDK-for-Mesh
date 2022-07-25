def appkey_add(self, address, application):
    command = {'model_name':'ConfigurationClient',
               'op':'appkey_add',
               'args':(application,)}
    service = {'opcode':'8003', 'cond':lambda x: x['meta']['src'] == address}
    try:
        self.mesh.run_model(self.mesh_manager_handle,
                            -address,
                            address,
                            command,
                            service)
    except TimeoutError:
        return False
    return True

def model_app_bind(self, element_address, application, model_id):
    import mesh.types as mt
    address = self.mesh.get_node_address(element_address)
    command = {'model_name':'ConfigurationClient',
               'op':'model_app_bind',
               'args':(element_address, application, mt.ModelId(model_id))}
    service = {'opcode':'803e', 'cond':lambda x: x['meta']['src'] == address}
    if address is None:
        return False
    try:
        self.mesh.run_model(self.mesh_manager_handle,
                            -address,
                            address,
                            command,
                            service)
    except TimeoutError:
        return False
    return True

def compose_node(self, address):
    if self.mesh.get_node(address) is None:
        return False
    command = {'model_name':'ConfigurationClient',
               'op':'composition_data_get'}
    service = {'opcode':'02', 'cond':lambda x: x['meta']['src'] == address}
    try:
        self.mesh.run_model(self.mesh_manager_handle,
                            -address,
                            address,
                            command,
                            service)
    except TimeoutError:
        return False
    return True

def node_reset(self, address):
    command = {'model_name':'ConfigurationClient',
               'op':'node_reset'}
    service = {'opcode':'804a', 'cond':lambda x: x['meta']['src'] == address}
    try:
        self.mesh.run_model(self.mesh_manager_handle,
                            -address,
                            address,
                            command,
                            service)
    except TimeoutError:
        return False
    return True

def hb_sub_get(self, address):
    command = {'model_name': 'ConfigurationClient',
               'op': 'heartbeat_subscription_get'}
    service = {'opcode':'803c',
               'cb':lambda x: x['data'],
               'cond':lambda x: x['meta']['src'] == address}
    try:
        ret = self.mesh.run_model(self.mesh_manager_handle,
                            -address,
                            address,
                            command,
                            service)
    except TimeoutError:
        return None
    return ret

def hb_pub_get(self, address):
    command = {'model_name': 'ConfigurationClient',
               'op': 'heartbeat_publication_get'}
    service = {'opcode':'06',
               'cb':lambda x: x['data'],
               'cond':lambda x: x['meta']['src'] == address}
    try:
        ret = self.mesh.run_model(self.mesh_manager_handle,
                            -address,
                            address,
                            command,
                            service)
    except TimeoutError:
        return None
    return ret

def hb_sub_set(self, address, src, dst, period):
    command = {'model_name': 'ConfigurationClient',
               'op': 'heartbeat_subscription_set',
               'args': (src, dst, period)}
    service = {'opcode':'803c',
               'cb':lambda x: x['data'],
               'cond':lambda x: x['meta']['src'] == address}
    try:
        ret = self.mesh.run_model(self.mesh_manager_handle,
                            -address,
                            address,
                            command,
                            service)
    except TimeoutError:
        return None
    return ret

def hb_pub_set(self, address, dst, count, period, ttl=64,feature_bitfield=0, netkey_index=0):
    command = {'model_name': 'ConfigurationClient',
               'op': 'heartbeat_publication_set',
               'args': (dst, count, period, ttl, feature_bitfield, netkey_index)}
    service = {'opcode':'06',
               'cb':lambda x: x['data'],
               'cond':lambda x: x['meta']['src'] == address}
    try:
        ret = self.mesh.run_model(self.mesh_manager_handle,
                            -address,
                            address,
                            command,
                            service)
    except TimeoutError:
        return None
    return ret
