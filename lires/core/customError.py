
class RBMError(Exception):
    """Base class for exceptions in this module."""
    pass

class RBMToBeImplementedError(RBMError, NotImplementedError):
    def __init__(self, err_msg=None):
        if err_msg is None:
            err_msg = "This feature is not yet implemented."
        super().__init__(err_msg)

class RBMDocTypeNotSupportedError(RBMToBeImplementedError):
    pass