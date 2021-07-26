from state import StateManager
from dashboard import Dashboard
from backend import Backend
import threading
import requests
import platform
from os import path
import logging
from logging.handlers import TimedRotatingFileHandler
import sys

sys.stdout.reconfigure(encoding='utf-8')
class App:
    def __init__(self):
        self.dashboard = None
        self.stateManager = StateManager()
        self.sanity_counter = 0
        self.sanity_checks = [self.sanity_check_network,
                              self.sanity_check_token, self.sanity_check_farms, self.sanity_check_rig]
        self.logger = None
        self.logformatter = None

    def run(self):
        if self.logger is None:
            self.setup_logger()
        retry_timer = self.get_state("system", "retry_timer")
        total_checks = len(self.sanity_checks)
        for i in range(self.sanity_counter, total_checks):
            check_func = self.sanity_checks[i]
            self.logger.info('Sanity check {}/{}: '.format(self.sanity_counter +
                                                           1, total_checks))
            if not check_func():
                self.logger.info("failed")
                self.logger.info("Retrying in {} seconds".format(retry_timer))
                threading.Timer(retry_timer, self.run).start()
                return
            else:
                self.logger.info("ok")
                self.sanity_counter = self.sanity_counter + 1

        self.welcome_message()
        self.dashboard.run()

    def setup_logger(self):
        self.logformatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
        self.logger = logging.getLogger(__name__)
        file_handler = TimedRotatingFileHandler(
            'logs/app.log', when='midnight', encoding='utf8')
        file_handler.setFormatter(self.logformatter)
        self.logger.addHandler(file_handler)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.logformatter)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)

    def welcome_message(self):
        expandtabs = self.get_state('system', 'expandtabs')
        header = """

██████╗░██╗████████╗███████╗░█████╗░██████╗░███╗░░░███╗  ░█████╗░██╗░░██╗██╗░█████╗░
██╔══██╗██║╚══██╔══╝██╔════╝██╔══██╗██╔══██╗████╗░████║  ██╔══██╗██║░░██║██║██╔══██╗
██████╦╝██║░░░██║░░░█████╗░░███████║██████╔╝██╔████╔██║  ██║░░╚═╝███████║██║███████║
██╔══██╗██║░░░██║░░░██╔══╝░░██╔══██║██╔══██╗██║╚██╔╝██║  ██║░░██╗██╔══██║██║██╔══██║
██████╦╝██║░░░██║░░░██║░░░░░██║░░██║██║░░██║██║░╚═╝░██║  ╚█████╔╝██║░░██║██║██║░░██║
╚═════╝░╚═╝░░░╚═╝░░░╚═╝░░░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░░░░╚═╝  ░╚════╝░╚═╝░░╚═╝╚═╝╚═╝░░╚═╝
                                                                            
        """
        self.logger.info(header)
        self.logger.info("OS version: \t".expandtabs(
            expandtabs) + ' ' + platform.version())
        self.logger.info("Management software version: \t".expandtabs(
            expandtabs)+' ' + self.get_state('system', 'version'))
        self.logger.info("Rig ID: \t".expandtabs(expandtabs) + ' ' +
                         self.get_state('system', 'rig_id'))

    def sanity_check_network(self):
        self.logger.info("Internet connection...")
        url = self.get_state('system', 'dashboard_url')
        status_code = 0
        try:
            request_response = requests.head(url)
            status_code =  request_response.status_code
        except:
            pass
        if status_code != 200:
            self.logger.warning("Network error")
        return True

    def sanity_check_token(self):
        self.logger.info("Token...")
        self.stateManager.load_configs()
        token = self.get_state("bitfarm", "token")
        return token is not None

    def sanity_check_farms(self):
        self.logger.info("Farms...")
        farms = self.get_state("bfchia", "farms[]")
        all_ok = True
        for x in farms:
            path_ok = path.exists(x)
            self.logger.info(f'  {x}\t...' + ('ok' if path_ok else 'failed'))
            if not path_ok:
                all_ok = False

        return all_ok

    def sanity_check_rig(self):
        self.logger.info("Register rig...")

        self.stateManager.load_configs()
        token = self.get_state("bitfarm", "token")

        self.backend = Backend(self, token)
        self.dashboard = Dashboard(self, token)

        return self.backend.run()

    def reload_configs(self):
        self.stateManager.load_configs()

    def get_state(self, section, option):
        return self.stateManager.get_val(section, option)

    def set_state(self, section, option, val):
        return self.stateManager.set_val(section, option, val)

    def commit_state(self, config_type):
        self.stateManager.save(config_type)


if __name__ == '__main__':
    app = App()
    app.run()
