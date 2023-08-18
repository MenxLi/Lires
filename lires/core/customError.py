
class LiresError(Exception):
    """Base class for exceptions in this module."""
    pass

class LiresToBeImplementedError(LiresError, NotImplementedError):
    def __init__(self, err_msg=None):
        if err_msg is None:
            err_msg = "This feature is not yet implemented."
        super().__init__(err_msg)

class LiresDocTypeNotSupportedError(LiresToBeImplementedError):
    pass