import yaml
import os

class Config:
    _instance = None
    _config_data = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):
        config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
        with open(config_path, 'r') as file:
            cls._config_data = yaml.safe_load(file)

    @property
    def dataset(self):
        return self._config_data.get('dataset', {})
    
    @property
    def quality(self):
        return self._config_data.get('quality', {})

    def reload(self):
        self._load_config()

config = Config()
