import numpy as np
from src.data_generator.config import config

class RandomState:
    _rng = None

    @classmethod
    def get_rng(cls):
        if cls._rng is None:
            seed = config.dataset.get('random_seed', 42)
            cls._rng = np.random.default_rng(seed)
        return cls._rng
    
    @classmethod
    def reset(cls, seed=None):
        if seed is None:
            seed = config.dataset.get('random_seed', 42)
        cls._rng = np.random.default_rng(seed)

def get_rng():
    return RandomState.get_rng()
