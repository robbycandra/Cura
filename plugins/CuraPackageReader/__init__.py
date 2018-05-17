# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from . import CuraPackageReader

from UM.i18n import i18nCatalog
catalog = i18nCatalog("cura")

def getMetaData():
    return {
        "package_reader": [
            {
                "extension": "curapackage",
                "description": catalog.i18nc("@item:inlistbox", "Cura Package")
            }
        ]
    }

def register(app):
    return { "package_reader": CuraPackageReader.CuraPackageReader() }
