def provision_node(self, uuid, key_index=0, name="Node", context_id=0, attention_duration_s=0):
    addr = self.mesh.provision_node(uuid, key_index, name, context_id, attention_duration_s)
    return addr

def device_list(self, duration=5):
    self.mesh.device_list(duration)
