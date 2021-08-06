from configparser import ConfigParser
from os.path import isfile
import pathlib
from getmac import get_mac_address as gma
import subprocess
import uuid
import tzlocal

class StateManager:
    def __init__(self):
        self.system_params = {
            'version': '0.2',
            'retry_timer': 15,
            'heartbeat_timer': 15,
            'expandtabs': 30,
            'dashboard_url': 'https://usbitfarm.com',
            'api_host': 'https://usbitfarm.com/api',
            'workers': [],
            'last_growth_ts': 0,
            'tz': tzlocal.get_localzone().zone
        }
        self.bitfarm_path = '{}/config.ini'.format(
            pathlib.Path(__file__).parent.absolute())
        bitfarm_defaults = {
            'bitfarm': {
                'token': ""
            },
            'bfchia': {
                'farms[]': "",
            },
            'chiaplotter': {
                "active": "0",
                "dir_temp": "",
                "dir_temp2": "",
                "dir_dest[]": "",
                "pool_key": "",
                "contract_address": "",
                "farmer_key": "",
                "threads": "2",
                "buckets": "256",
                "K": "1"
            },
            'harvester':{
                "active": "0",
                "init": "0",
                "chia_path": "",
                "certs_dir": "",
                "farmer_host": "",
                "farmer_port": ""
            }
        }
        self.bitfarm_config = ConfigParser()

        # Set default values
        for section in bitfarm_defaults:
            self.bitfarm_config.add_section(section)
            for opt in bitfarm_defaults[section]:
                self.bitfarm_config.set(
                    section, opt, bitfarm_defaults[section][opt])

        # Initialize config file
        if not isfile(self.bitfarm_path):
            self.save('bitfarm')

        self.system_params['mac'] = gma().replace(':', '')

        if len(self.system_params['mac']) == 0:
            self.system_params['mac'] = "%x" % (uuid.getnode())
        self.system_params['os'] = self.get_os_version()

    def get_os_version(self):
        v = '1.0'
        try:
            v = subprocess.check_output(
                'grep -oP \'(?<=BitfarmOS ).+\' /etc/lsb-release | tr -d \'"\'', shell=True).decode('UTF-8').rstrip()
        except:
            pass
        if not v:
            v = '1.0'
        return v

    def load_configs(self):
        self.bitfarm_config.read(self.bitfarm_path)

    def get_val(self, section, option):
        val = None
        if section == 'system':
            val = self.system_params.get(option)
        else:
            val = self.bitfarm_config.get(section, option)
            if '[]' in option and isinstance(val, str):
                val = list(filter(None, [x.strip() for x in val.splitlines()]))
        return val

    def set_val(self, section, option, val):
        if section == 'system':
            self.system_params[option] = val
        else:
            if isinstance(val, list):
                val = '\n' + '\n'.join(val)
            self.bitfarm_config.set(section, option, val)

    def save(self, config_type):
        if config_type == 'bitfarm':
            with open(self.bitfarm_path, 'w') as configfile:
                self.bitfarm_config.write(configfile)
