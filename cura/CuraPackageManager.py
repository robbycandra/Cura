# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from cura.CuraApplication import CuraApplication #To define installation directories for material and quality profiles.
from UM.PackageManager import PackageManager #The class we inherit from.
from UM.Resources import Resources #To define installation directories for material and quality profiles.

##  Installs packages and manages which packages are currently installed.
class CuraPackageManager(PackageManager):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.installation_dirs_dict["materials"] = Resources.getStoragePath(CuraApplication.ResourceTypes.MaterialInstanceContainer)
        self.installation_dirs_dict["quality"] = Resources.getStoragePath(CuraApplication.ResourceTypes.QualityInstanceContainer)
