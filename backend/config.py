from datetime import datetime
import platform
import configparser
import os
from pathlib import Path
from web import LCTVER
from web import CFGDEF


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        if platform.system() == "Windows":
            self.cfgfile = os.getenv('APPDATA') + '\lct\lctbackend.ini'
        else:
            self.cfgfile = str(Path.home())+'/.lct/lctbackend.config'
        cfgdir = os.path.dirname(self.cfgfile)
        if not os.path.exists(cfgdir):
            os.makedirs(cfgdir, 0o755)
        if not os.path.isfile(self.cfgfile):
            self.config_default()
            self.cfg_write_close()
        self.config.read(self.cfgfile)


    def cfg_write_close(self):
        with open(self.cfgfile, 'w') as configfile:
            self.config.write(configfile)


    def config_set(self, configstore):
        if 'mysql_user' in configstore.keys():
            self.config.set('MySql', 'mysql_user', configstore['mysql_user'])
        if 'mysql_password' in configstore.keys():
            self.config.set('MySql', 'mysql_password', configstore['mysql_password'])
        if 'mysql_database' in configstore.keys():
            self.config.set('MySql', 'mysql_database', configstore['mysql_database'])
        if 'mysql_host' in configstore.keys():
            self.config.set('MySql', 'mysql_host', configstore['mysql_host'])
        if 'listen_address' in configstore.keys():
            self.config.set('Backend', 'listen_address', configstore['listen_address'])
        if 'listen_port' in configstore.keys():
            self.config.set('Backend', 'listen_port', configstore['listen_port'])
        if 'lct_version' in configstore.keys():
            self.config.set('Backend', 'lct_version', configstore['lct_version'])


    def config_get(self, configstore):
        while not self.config_get_sub(configstore):
            pass

    def config_get_sub(self, configstore):
        global CFGDEF
        try:
            if 'mysql_user' in configstore.keys():
                configstore['mysql_user'] = self.config.get('MySql', 'mysql_user')
            if 'mysql_password' in configstore.keys():
                configstore['mysql_password'] = self.config.get('MySql', 'mysql_password')
            if 'mysql_database' in configstore.keys():
                configstore['mysql_database'] = self.config.get('MySql', 'mysql_database')
            if 'mysql_host' in configstore.keys():
                configstore['mysql_host'] = self.config.get('MySql', 'mysql_host')
            if 'listen_address' in configstore.keys():
                configstore['listen_address'] = self.config.get('Backend', 'listen_address')
            if 'listen_port' in configstore.keys():
                configstore['listen_port'] = self.config.get('Backend', 'listen_port')
            if 'lct_version' in configstore.keys():
                configstore['lct_version'] = self.config.get('Backend', 'lct_version')
            return True
        except configparser.NoSectionError as err:
            self.config.add_section(err.args[0])
            self.cfg_write_close()
            return False
        except configparser.NoOptionError as err:
            self.config_set({err.args[0] : CFGDEF[err.args[0]]})
            self.cfg_write_close()
            return False



    def config_default(self):
        global LCTVER
        self.config.add_section('Backend')
        self.config.set('Backend', 'lct_version', LCTVER)

