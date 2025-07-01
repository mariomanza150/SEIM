from ...config_model import ConfigModel

class ProgramType(ConfigModel):
    def __str__(self):
        return self.name
