"""
Defines an XYZEnvironment.
"""

from xyz.interpreter.scoped_env import Scope
from xyz.interpreter.types import XYZType

class XYZEnvironment(Scope):
    """An environment to be the global scope of an XYZ script.
    
    Can be initialized with a dictionary of names to values, which will be accessible to the script.
    For example, can make external functions available for XYZ to call.
    XYZ values can be retrieved from the scope at any time.
    """

    def __init__(self, userdata: dict[str, XYZType] = {}):
        """Initializes the environment, optionally with a dictionary of initial values."""
        Scope.__init__(self, None, "global")
        for k in userdata.keys():
            self.external_define(k, userdata[k])
