import platform
import configparser
import os
from pathlib import Path
CONST_CFGVER = '0.0.2'


class Config:
    def __init__(self, directory='cfg', filename='config'):
        """
        Create a config object with associated file

        On a windows system the config file is created at %APPDATA% dir
            with a coosen directory and suffix .ini
        On a Linux system the config file is created at the user dir ~
            with a coosen directory and suffix .config

        If no file is present a file is created an the version of
        the config class is added

        :param directory:
            The direcory created to store the config file
        :param filename:
            The filename without the added suffix which is OS dependant
        """
        self.config = configparser.ConfigParser()
        if platform.system() == "Windows":
            self.cfgfile = os.getenv('APPDATA') + '\\' + directory + '\\' + filename + '.ini'
        else:
            self.cfgfile = str(Path.home()) + '/' + directory + '/' + filename + '.config'
        cfgdir = os.path.dirname(self.cfgfile)
        if not os.path.exists(cfgdir):
            os.makedirs(cfgdir, 0o755)
        if not os.path.isfile(self.cfgfile):
            self.config_default()
            self.cfg_write_close()
        self.config.read(self.cfgfile)

    def cfg_write_close(self):
        """
        Writes the configuration changes and close the file

        :return:
            Nothing
        """
        with open(self.cfgfile, 'w') as configfile:
            self.config.write(configfile)

    def add_cfg(self, section, key, value):
        """
        Add a configuration option in a section

        If the section doesn't exist it's created
        :param section:
            The section for the configuration
        :param key:
            The key for the configuration
        :param value:
            The value for the key
        :return:
            0 for successful configuration add
            1 if the section/key already exist nothing is updated
        """
        if not self.config.has_section(section):
            self.config.add_section(section)
        if self.config.has_option(section, key):
            return 1
        self.config.set(section, key, value)
        self.cfg_write_close()
        return 0

    def upd_cfg(self, section, key, value):
        """
        Update a configuration option in a section

        Update the value of the section/key configuration

        :param section:
            The section for the configuration
        :param key:
                The key to be updated
        :param value:
            The value to update to
        :return:
            0 for successful configuration update
            1 if the section/key doesn't exist
        """
        if not self.config.has_option(section, key):
            return 1
        self.config.set(section, key, value)
        self.cfg_write_close()
        return 0

    def set_cfg(self, section, key, value):
        """
        Force a set of a configuration in a section

        :param section:
            The section for the configuration
        :param key:
            The key to be updated
        :param value:
            The value to force set
        :return:
            Always 0
        """
        if self.upd_cfg(section, key, value) == 1:
            self.add_cfg(section, key, value)
        return 0

    def get_cfg(self, section, key):
        """
        Get a configuration option in a section by key

        :param section:
             The section for the configuration
        :param key:
            The key to get value for
        :return:
            The value for the section, key
        """
        if not self.config.has_option(section, key):
            return False
        return self.config.get(section, key)

    def del_cfg(self, section, key):
        """
        Delete a configuration option in a section

        :param section:
            The section for the configuration
        :param key:
            The key to be deleted
        :return:
            0 for a successful configuration delete
            1 if the section/key doesn't exist
        """
        if not self.config.has_option(section, key):
            return 1
        self.config.remove_option(section, key)
        # If the option is last in section also remove section
        self.cfg_write_close()
        return 0

    def config_default(self):
        """
        Add the configs own section and the veriosn for the config class
        :return:
        """
        self.config.add_section('config')
        self.config.set('config', 'cfgver', CONST_CFGVER)
