# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from UM.PluginObject import PluginObject

##  A type of plug-in that reads packages.
class PackageReader(PluginObject):
    def __init__(self):
        super().__init__()

    def read(self, file_name):
        raise NotImplementedError("Package reader plug-in was not correctly implemented. The read function was not implemented.")
