from mesh.access import Model
from models.config import ConfigurationClient                                         # NOQA: ignore unused import
from models.simple_on_off import SimpleOnOffClient                                    # NOQA: ignore unused import
from models.generic_on_off import GenericOnOffClient                                  # NOQA: ignore unused import
from models.generic_level import GenericLevelClient                                   # NOQA: ignore unused import
from models.generic_default_transition_time import GenericDefaultTransitionTimeClient # NOQA: ignore unused import
from models.generic_power_on_off import GenericPowerOnOffClient                       # NOQA: ignore unused import
from models.generic_power_level import GenericPowerLevelClient                        # NOQA: ignore unused import

class ModelMgr(object):
    def __init__(self, prov_db):
        self.__models = dict()
        self.__next_model_handle = 0
        self.create_model(ConfigurationClient(prov_db), "ConfigurationClient")
        self.create_model(SimpleOnOffClient(), "SimpleOnOffClient")
        self.create_model(GenericOnOffClient(), "GenericOnOffClient")
        self.create_model(GenericLevelClient(), "GenericLevelClient")
        self.create_model(GenericDefaultTransitionTimeClient(), "GenericDefaultTransitionTimeClient")
        self.create_model(GenericPowerOnOffClient(), "GenericPowerOnOffClient")
        self.create_model(GenericPowerLevelClient(), "GenericPowerLevelClient")

    def create_model(self, model, name):
        if not isinstance(model, Model):
            raise Exception("model is not Model")
        self.__models[self.__next_model_handle] = model
        self.__next_model_handle += 1

    def model_handle(self, name):
        for k, v in self.__models.items():
            if v.__class__.__name__ == name:
                return k

    def __valid_handle(self, model_handle):
        return model_handle in self.__models

    def model(self, model_handle):
        if not self.__valid_handle(model_handle):
            return None
        else:
            return self.__models[model_handle]
        
