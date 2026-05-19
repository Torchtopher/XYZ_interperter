"""
Defines an XYZ source to be read and reported.
"""

from io import StringIO

class XYZSource:
    """
    An XYZ source. Could be a file, anonymous code string, etc.

    Attributes:
      string:
        A StringIO for the source code.
      name:
        A file name for error reporting.
    """
    string: StringIO
    name: str

    def __init__(self, string, name):
        self.string = string
        self.name = name
