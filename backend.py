import requests
import os
import re
import subprocess
from jsonrpc_pyclient.connectors import socketclient
import socket

"""
Client to communicate with backend dashboard
"""

class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


class Backend:
    def __init__(self, app, token):
        self.app = app
        self.token = token
        self.api_host = app.get_state('system', 'api_host')
        self.heartbeat = app.get_state('system', 'heartbeat_timer')
        self.mac = '' # To identify individual mining rig in backend

    def run(self):
        try:
            self.mac = self.app.get_state('system', 'mac')
            osversion = self.app.get_state('system', 'os')
            version = self.app.get_state('system', 'version')
            tz = self.app.get_state('system', 'tz')
            res = self.post_request(
                'xch/rigs', {'mac': self.mac, 'os': osversion, 'v': version, 'tz': tz})
            if 'rig_id' in res:
                self.app.set_state('system', 'rig_id', res['rig_id'])
            if 'last_growth_ts' in res:
                self.app.set_state('system', 'last_growth_ts',
                                   res['last_growth_ts'])
        except Exception as e:
            self.app.logger.warning(f"Unable to register rig {str(e)}")

        return True

    def new_networkcard(self):
        return {
            "name": "",
            "mac": "",
            "ip": ""
        }

    def get_networks_info(self):
        networks = []
        nameRE = r"\d+: (.*): <.*"
        macRE = r"link/.* (.*) brd"
        ipRE = r"inet (.*) brd"

        netinfo = self.new_networkcard()
        if os.name == 'nt':
            netinfo['ip'] = self.get_lan_ip()
        else:
            hwinfo = subprocess.check_output(
                'ip address show'.split()).decode('utf-8').rstrip().split('\n')
            for line in hwinfo:
                if 'mtu' in line:
                    if netinfo['name'] != '' and netinfo['name'] != 'lo':
                        networks.append(netinfo)
                    netinfo = self.new_networkcard()
                if netinfo['name'] == '':
                    matches = re.findall(nameRE, line)
                    if len(matches) == 1:
                        netinfo['name'] = matches[0]
                else:
                    if netinfo['mac'] == '':
                        matches = re.findall(macRE, line)
                        if len(matches) == 1:
                            netinfo['mac'] = matches[0]
                    else:
                        matches = re.findall(ipRE, line)
                        if len(matches) == 1:
                            netinfo['ip'] = matches[0]
        if netinfo:
            networks.append(netinfo)
        return networks

    def post_request(self, endpoint, data):
        try:
            resp = requests.post('{}/{}'.format(self.api_host, endpoint), json=data,
                                 headers={'Authorization': 'Bearer {}'.format(self.token), 'Accept': 'application/json'})
            if resp.status_code == 200:
                return resp.json()
            raise APIError(resp.status_code)
        except Exception as e:
            self.app.logger.warning(f'API POST error: {str(e)}')

    def get_request(self, endpoint):
        try:
            resp = requests.get('{}/{}'.format(self.api_host, endpoint),
                                headers={'Authorization': 'Bearer {}'.format(self.token), 'Accept': 'application/json'})
            if resp.status_code == 200:
                return resp.json()
            raise APIError(resp.status_code)
        except Exception as e:
            self.app.logger.warning(f'API GET error: {str(e)}')

    def report_growth(self, report):
        networks = self.get_networks_info()
        report.update({'w': self.get_wan_ip(
        ), 'networks': networks, 'ssh_addr': self.get_tunnel_path()})
        result = self.post_request(
            'xch/rigs/' + self.mac + '/growth', report)
        return result

    def get_tunnel_path(self):
        # Tunneling only available in linux system
        if os.name == 'nt':
            return ''

        sshpath = ''
        urlpath = '/var/tmp/url.txt'
        if not os.path.isfile(urlpath):
            urlpath = '/opt/bftunnel/url.txt'
        if os.path.isfile(urlpath):
            file = open(urlpath, 'r')
            line = file.readline()
            try:
                sshpath = re.search('your url is: (.*)',
                                    line, re.IGNORECASE).group(1)
            except:
                sshpath = ''

        return sshpath

    def get_wan_ip(self):
        ip = ''
        try:
            ip = requests.get(self.api_host+'/ip').text.strip()
        except:
            ip = ''
        return ip

    def get_lan_ip(self):
        ip = ''
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = ''
        return ip
