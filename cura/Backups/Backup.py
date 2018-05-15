# Copyright (c) 2018 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
import io
import os
import shutil

from typing import Optional
from zipfile import ZipFile, ZIP_DEFLATED, BadZipfile

from UM import i18nCatalog
from UM.Logger import Logger
from UM.Message import Message
from UM.Platform import Platform
from UM.Preferences import Preferences
from UM.Resources import Resources
from cura.CuraApplication import CuraApplication


class Backup:
    """
    The backup class holds all data about a backup.
    It is also responsible for reading and writing the zip file to the user data folder.
    """

    # These files should be ignored when making a backup.
    IGNORED_FILES = {"cura.log", "cache"}

    # Re-use translation catalog.
    catalog = i18nCatalog("cura")

    def __init__(self, zip_file: bytes = None, meta_data: dict = None):
        self.zip_file = zip_file  # type: Optional[bytes]
        self.meta_data = meta_data  # type: Optional[dict]

    def makeFromCurrent(self) -> (bool, Optional[str]):
        """
        Create a backup from the current user config folder.
        """
        cura_release = CuraApplication.getInstance().getVersion()
        version_data_dir = Resources.getDataStoragePath()

        Logger.log("d", "Creating backup for Cura %s, using folder %s", cura_release, version_data_dir)

        # We copy the preferences file to the user data directory in Linux as it's in a different location there.
        # When restoring a backup on Linux, we move it back.
        if Platform.isLinux():
            preferences_file_name = CuraApplication.getInstance().getApplicationName()
            preferences_file = Resources.getPath(Resources.Preferences, "{}.cfg".format(preferences_file_name))
            backup_preferences_file = os.path.join(version_data_dir, "{}.cfg".format(preferences_file_name))
            Logger.log("d", "Copying preferences file from %s to %s", preferences_file, backup_preferences_file)
            shutil.copyfile(preferences_file, backup_preferences_file)

        # Ensure all current settings are saved.
        CuraApplication.getInstance().saveSettings()

        # Create an empty buffer and write the archive to it.
        buffer = io.BytesIO()
        archive = self._makeArchive(buffer, version_data_dir)
        files = archive.namelist()
        
        # Count the metadata items. We do this in a rather naive way at the moment.
        machine_count = len([s for s in files if "machine_instances/" in s]) - 1
        material_count = len([s for s in files if "materials/" in s]) - 1
        profile_count = len([s for s in files if "quality_changes/" in s]) - 1
        plugin_count = len([s for s in files if "plugin.json" in s])
        
        # Store the archive and metadata so the BackupManager can fetch them when needed.
        self.zip_file = buffer.getvalue()
        self.meta_data = {
            "cura_release": cura_release,
            "machine_count": str(machine_count),
            "material_count": str(material_count),
            "profile_count": str(profile_count),
            "plugin_count": str(plugin_count)
        }

    def _makeArchive(self, buffer: "io.BytesIO", root_path: str) -> Optional[ZipFile]:
        """
        Make a full archive from the given root path with the given name.
        :param root_path: The root directory to archive recursively.
        :return: The archive as bytes.
        """
        contents = os.walk(root_path)
        try:
            archive = ZipFile(buffer, "w", ZIP_DEFLATED)
            for root, folders, files in contents:
                for folder_name in folders:
                    if folder_name in self.IGNORED_FILES:
                        continue
                    absolute_path = os.path.join(root, folder_name)
                    relative_path = absolute_path[len(root_path) + len(os.sep):]
                    archive.write(absolute_path, relative_path)
                for file_name in files:
                    if file_name in self.IGNORED_FILES:
                        continue
                    absolute_path = os.path.join(root, file_name)
                    relative_path = absolute_path[len(root_path) + len(os.sep):]
                    archive.write(absolute_path, relative_path)
            archive.close()
            return archive
        except (IOError, OSError, BadZipfile) as error:
            Logger.log("e", "Could not create archive from user data directory: %s", error)
            self._showMessage(
                self.catalog.i18nc("@info:backup_failed",
                                   "Could not create archive from user data directory: {}".format(error)))
            return None

    def _showMessage(self, message: str) -> None:
        """Show a UI message"""
        Message(message, title=self.catalog.i18nc("@info:title", "Backup"), lifetime=30).show()

    def restore(self) -> bool:
        """
        Restore this backups
        :return: A boolean whether we had success or not.
        """
        if not self.zip_file or not self.meta_data or not self.meta_data.get("cura_release", None):
            # We can restore without the minimum required information.
            Logger.log("w", "Tried to restore a Cura backup without having proper data or meta data.")
            self._showMessage(
                self.catalog.i18nc("@info:backup_failed",
                                   "Tried to restore a Cura backup without having proper data or meta data."))
            return False

        # TODO: handle restoring older data version.

        version_data_dir = Resources.getDataStoragePath()
        archive = ZipFile(io.BytesIO(self.zip_file), "r")
        extracted = self._extractArchive(archive, version_data_dir)

        # Under Linux, preferences are stored elsewhere, so we copy the file to there.
        if Platform.isLinux():
            preferences_file_name = CuraApplication.getInstance().getApplicationName()
            preferences_file = Resources.getPath(Resources.Preferences, "{}.cfg".format(preferences_file_name))
            backup_preferences_file = os.path.join(version_data_dir, "{}.cfg".format(preferences_file_name))
            Logger.log("d", "Moving preferences file from %s to %s", backup_preferences_file, preferences_file)
            shutil.move(backup_preferences_file, preferences_file)

        return extracted

    @staticmethod
    def _extractArchive(archive: "ZipFile", target_path: str) -> bool:
        """
        Extract the whole archive to the given target path.
        :param archive: The archive as ZipFile.
        :param target_path: The target path.
        :return: A boolean whether we had success or not.
        """
        Logger.log("d", "Removing current data in location: %s", target_path)
        shutil.rmtree(target_path)
        Logger.log("d", "Extracting backup to location: %s", target_path)
        archive.extractall(target_path)
        return True