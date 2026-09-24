import numpy as np

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

def logistic_probability(base_logit, effects, noise_scale=0.5, rng=None):
    """
    Computes a probability using a logistic function:
    logit = base_logit + sum(effects) + noise
    p = sigmoid(logit)
    """
    logit = base_logit + sum(effects)
    if rng is not None and noise_scale > 0:
        logit += rng.normal(0, noise_scale, size=np.shape(logit))
    return sigmoid(logit)
