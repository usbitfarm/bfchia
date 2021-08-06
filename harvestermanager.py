import subprocess

class HarvesterManager:
    def __init__(self, app):
        self.app = app

    def run(self):
        active = self.app.get_state('harvester', 'active')
        chia_path = self.app.get_state('harvester', 'chia_path')
        
        if active == "0":
            return
        init = self.app.get_state('harvester', 'init')
        if init:
            self.init_chia(chia_path)
            
        self.start_harvester()
            
    def init_chia(self, chia_path):
        certs_dir = self.app.get_state('harvester', 'certs_dir')
        farmer_host = self.app.get_state('harvester', 'farmer_host')
        farmer_port = self.app.get_state('harvester', 'farmer_port')
        
        cmd = '{} init -c {}'.format(chia_path, certs_dir)
        output = subprocess.check_output(cmd, shell=True)
        self.app.logger.info(output)
        
        cmd = '{} configure --set-farmer-peer {}:{}'.format(chia_path, farmer_host, farmer_port)
        output = subprocess.check_output(cmd, shell=True)
        self.app.logger.info(output)
        
    def start_harvester(self):
        cmd = '{} start harvester -r'
        output = subprocess.check_output(cmd, shell=True)
        self.app.logger.info(output)