
class LiresError:
    class LiresErrorBase(Exception): ...
    class LiresUserDuplicationError(LiresErrorBase):...
    class LiresUserNotFoundError(LiresErrorBase):...

    class LiresEntryNotFoundError(LiresErrorBase):...

    class LiresSizeTooLargeError(LiresErrorBase):...
    class LiresDiskFullError(LiresSizeTooLargeError):...

    class LiresToBeImplementedError(LiresErrorBase, NotImplementedError):...
    class LiresDocTypeNotSupportedError(LiresToBeImplementedError):...

    class LiresProhibitedKeywordError(LiresErrorBase):...

    class LiresConnectionError(LiresErrorBase):...
    class LiresConnectionAuthError(LiresConnectionError):...    # 401 or 403
    class LiresResourceNotFoundError(LiresConnectionError):...  # 404
