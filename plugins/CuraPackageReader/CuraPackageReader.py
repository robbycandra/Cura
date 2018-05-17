# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.

from UM.MimeTypeDatabase import MimeTypeDatabase, MimeType
from UM.Application import Application
from cura.ReaderWriters.PackageReader import PackageReader

import zipfile

MimeTypeDatabase.addMimeType(
    MimeType(
        name = "application/x-cura-package",
        comment = "Cura Package",
        suffixes = ["curapackage"]
    )
)

class CuraPackageReader(PackageReader):
    def __init__(self):
        super().__init__()
        # self._application = Application.getInstance()
        # self._package_manager = None
        # Application.getInstance().initializationFinished.connect(self._onAppInitialized)

    # This is a plugin, so most of the components required are not ready when
    # this is initialized. Therefore, we wait until the application is ready.
    # def _onAppInitialized(self) -> None:
        # self._package_manager = Application.getInstance().getCuraPackageManager()

    # Everything is handled by the CuraPackageManger. Pass it there instead.
    def read(self, file_name):
        try:
            with zipfile.ZipFile(file_name, "r") as archive:
                print("!!!!! TRYNA OPEN DIS BITCH", file_name)
                # results = []
                # for profile_id in archive.namelist():
                #     with archive.open(profile_id) as f:
                #         serialized = f.read()
                #     profile = self._loadProfile(serialized.decode("utf-8"), profile_id)
                #     if profile is not None:
                #         results.append(profile)
                # return results

        except zipfile.BadZipFile:
            # It must be an older profile from Cura 2.1.
            with open(file_name, encoding = "utf-8") as fhandle:
                serialized = fhandle.read()
            return [self._loadProfile(serialized, profile_id) for serialized, profile_id in self._upgradeProfile(serialized, file_name)]