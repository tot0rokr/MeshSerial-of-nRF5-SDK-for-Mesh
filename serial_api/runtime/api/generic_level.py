def generic_level_get(self, address, application):
    command = {'model_name':'GenericLevelClient',
               'op':'get'}
    service = {'opcode':'8208',
               'cb':lambda x: x['data'],
               'cond':lambda x: x['meta']['src'] == address}
    try:
        ret = self.mesh.run_model(self.mesh_manager_handle,
                            application,
                            address,
                            command,
                            service)
    except TimeoutError:
        return None
    return ret

def generic_level_set(self, address, application, level):
    command = {'model_name':'GenericLevelClient',
               'op':'set',
               'args':(level,)}
    service = {'opcode':'8208',
               'cb':lambda x: x['data'],
               'cond':lambda x: x['meta']['src'] == address}
    try:
        ret = self.mesh.run_model(self.mesh_manager_handle,
                            application,
                            address,
                            command,
                            service)
    except TimeoutError:
        return None
    return ret
