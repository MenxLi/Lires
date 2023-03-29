import warnings
with warnings.catch_warnings():
    warnings.simplefilter("always", DeprecationWarning)
    warnings.warn("RBMWeb backend server is deprecated and is moved to resbibman.server", DeprecationWarning)