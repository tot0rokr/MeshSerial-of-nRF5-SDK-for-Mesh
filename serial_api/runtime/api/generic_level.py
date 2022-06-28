def generic_level_get(self, address, application):
    command = {'model_name':'GenericLevelClient',
               'op':'appkey_add'}
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
