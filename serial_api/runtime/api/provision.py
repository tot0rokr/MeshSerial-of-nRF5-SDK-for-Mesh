def provision_node(self, uuid, key_index=0, name="Node", context_id=0, attention_duration_s=0):
    addr = self.mesh.provision_node(uuid, key_index, name, context_id, attention_duration_s)
    return addr

def fast_provision_nodes(self, uuids=[], key_index=0, names=[], attention_duration_s=0):
    import concurrent.futures
    MAX_WORKERS = 5

    if len(names) != len(uuids):
        names = ["Node_" + str(i) for i in range(len(uuids))]

    addrs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = []
        for i in range(len(uuids)):
            futures.append(pool.submit(self.mesh.provision_node,
                                      uuids[i],
                                      key_index,
                                      names[i],
                                      i % 5,
                                      attention_duration_s))
        for future in concurrent.futures.as_completed(futures):
            addrs.append(future.result())

    return addrs

def device_list(self, duration=5):
    self.mesh.device_list(duration)
