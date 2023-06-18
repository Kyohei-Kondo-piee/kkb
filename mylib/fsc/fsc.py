# 1.standard
# 2.third_party
import numpy as np
# 3.self_maid


def zscore(x, axis = None):
    """
    feature scaling(standardization)
    https://aiacademy.jp/texts/show/?id=555

    Args:
        x(numpy.ndarray): data before processing
    """
    x_mean  = x.mean(axis=axis, keepdims=True) # ave
    x_std   = np.std(x, axis=axis, keepdims=True) # standard div
    z_score = (x-x_mean)/x_std # standard error

    return z_score, x_mean, x_std
