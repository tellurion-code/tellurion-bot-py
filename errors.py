class LBIException(Exception):
    """
    Base exception class for LBI

    All other exceptions are subclasses
    """
    pass


class ModuleException(LBIException):
    """
    Base exception class for all module errors
    """
    pass


class ModuleNotInstalled(ModuleException):
    """
    Raised when a module is not found in module directory
    """
    pass


class IncompatibleModule(ModuleException):
    """
    Raised when a module is not compatible with bot version
    """
    pass
