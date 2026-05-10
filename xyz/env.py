from xyz.interpreter.scoped_env import Scope
from xyz.interpreter.types import XYZType

class XYZEnvironment(Scope):
    def __init__(self, userdata: dict[str, XYZType] = {}):
        Scope.__init__(self, None, "global")
        for k in userdata.keys():
            self.define(k, userdata[k], True)
