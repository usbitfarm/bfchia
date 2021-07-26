import threading
import datetime
from datetime import datetime
import os
import shutil
import math
import subprocess
import threading
import logging
import sys
import glob
import time


class Dashboard:
    def __init__(self, app, token):
        self.app = app
        self.heartbeat_interval = 15 * 60
        self.token = token
        self.plot_size = 101.4
        self.pending_plots = {}
        self.transfer_queue = []
        self.plot_in_transfer = None
        self.is_windows = (os.name == 'nt')

    def run(self):
        self.heartbeat()
        self.spawn_plotter()

    def can_plot(self):
        self.app.reload_configs()
        res = self.app.get_state('chiaplotter', 'active') == '1'
        if res:
            res = self.check_capacity(len(self.pending_plots) + 1)
            if not res:
                self.app.logger.info('No available disk')
        else:
            self.app.logger.info('chiaplotter inactive')
        return res

    def startofday(self, ts):
        d = datetime.fromtimestamp(ts)
        daystart = datetime(year=d.year, month=d.month,
                            day=d.day, hour=0, minute=0, second=0)
        return math.floor(datetime.timestamp(daystart))

    def heartbeat(self):
        report = self.scan_farms()
        result = self.app.backend.report_growth(report)
        last_growth_ts = report['last_growth_ts'] if (result and 'last_growth_ts' not in result) else result['last_growth_ts']
        self.app.set_state('system', 'last_growth_ts', last_growth_ts)
        self.app.logger.info(f"Last growth: {last_growth_ts}")
        threading.Timer(self.heartbeat_interval, self.heartbeat).start()

    def scan_farms(self):
        drive_stats = []
        folders = self.app.get_state('bfchia', 'farms[]')
        last_growth_ts = self.app.get_state('system', 'last_growth_ts')

        todayts = self.startofday(datetime.now().timestamp())
        size_total = 0
        growth_today = 0

        reports = {}
        datelist = []
        logs = []

        # Consolidate daily growth if last_growth_ts is earlier than today, otherwise return fine growth report
        for folder in folders:
            if not folder.endswith('/') and not folder.endswith('\\'):
                folder = folder + "/"
            for filepath in glob.iglob(f'{folder}**/*.plot', recursive=True):
                file_stat = os.stat(filepath)
                size = round(file_stat.st_size / (2**30), 2)
                mtime = math.floor(file_stat.st_mtime)
                size_total += size
                if mtime >= todayts:
                    growth_today += size

                if mtime > last_growth_ts:
                    datets = self.startofday(mtime)

                    if datets not in reports:
                        datelist.append(datets)
                        reports[datets] = {
                            'ts': datets,
                            'growth': 0,
                        }

                    data = reports[datets]
                    data['growth'] = data['growth'] + size
                    if mtime > data['ts']:
                        data['ts'] = mtime
                    reports[datets] = data

            disk_usage_stat = shutil.disk_usage(folder)
            report_stat = [folder, round(disk_usage_stat.free / (2**30), 2),
                           round(disk_usage_stat.used / (2**30), 2),
                           round(disk_usage_stat.total / (2**30), 2)]
            drive_stats.append(report_stat)

        datelist.sort()

        for ts in datelist:
            logs.append(reports[ts])

        last_growth_ts = math.floor(datetime.now().timestamp())
        report = {
            'growth_today': growth_today,
            'size_total': size_total,
            'last_growth_ts': last_growth_ts,
            'drives': drive_stats,
            'logs': logs
        }
        
        return report

    def spawn_plotter(self):
        # check config file
        self.app.logger.info(f'Spawning plotter')

        if not self.can_plot():
            self.app.set_state('chiaplotter', 'active', '0')
            self.app.commit_state('chiaplotter')
            return

        pool_key = self.app.get_state("chiaplotter", "pool_key")
        contract_address = self.app.get_state(
            "chiaplotter", "contract_address")
        farmer_key = self.app.get_state("chiaplotter", "farmer_key")
        num_threads = self.app.get_state("chiaplotter", "threads")
        buckets = self.app.get_state("chiaplotter", "buckets")
        temp = self.app.get_state("chiaplotter", "dir_temp")
        temp2 = self.app.get_state("chiaplotter", "dir_temp2")
        rmulti2 = self.app.get_state("chiaplotter", "K")

        # sanitize values
        if temp2 is None:
            temp2 = temp
        if not temp.endswith('/') and not temp.endswith('\\'):
            temp = temp + "/"
        if not temp2.endswith('/') and not temp2.endswith('\\'):
            temp2 = temp2 + "/"

        cmd = 'plugins\plotters\chia_plot.exe' if self.is_windows else 'plugins/plotters/chia_plot'
        cmd = cmd + ' -n 1 -f {} -r {} -u {} -t {} -2 {} -K {}'.format(
            farmer_key, num_threads, buckets, temp, temp2, rmulti2)

        if len(contract_address) > 0:
            cmd = cmd + ' -c {}'.format(contract_address)
        else:
            cmd = cmd + ' -p {}'.format(pool_key)

        self.app.logger.info("Plot command:" + cmd)

        process_handle = subprocess.Popen(cmd,
                                          shell=True,
                                          bufsize=1,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          universal_newlines=True)
        plotter_meta = {
            "id": "",
            "handle": process_handle
        }
        t = threading.Thread(target=self.monitor_plotter,
                             args=(plotter_meta, temp))
        t.start()

    def monitor_plotter(self, plotter_meta, dest):
        process_handle = plotter_meta['handle']
        plotname = ''
        logger = None
        while True and process_handle != None:
            output = process_handle.stdout.readline().strip()
            if len(output) > 0:
                if logger is None and 'Plot Name: ' in output:
                    plotname = output[11:]
                    handler = logging.FileHandler(
                        f'logs/{plotname}.log', encoding='utf8')
                    handler.setFormatter(self.app.logformatter)
                    logger = logging.getLogger(plotname)
                    logger.propagate = True
                    logger.addHandler(handler)
                    console_handler = logging.StreamHandler(sys.stdout)
                    console_handler.setFormatter(self.app.logformatter)
                    logger.addHandler(console_handler)
                    logger.setLevel(logging.DEBUG)
                    self.pending_plots[plotname] = {"path": os.path.join(
                        dest, f'{plotname}.plot'), 'status': 0}

                if 'Total plot creation time was' in output:
                    self.spawn_plotter()

                if logger is not None:
                    logger.info(output)
                else:
                    self.app.logger.info(output)

            try:
                return_code = process_handle.poll()
                if return_code is not None:
                    if len(plotname) > 0:
                        self.app.logger.info(f'Plot {plotname} completed')
                    self.pending_plots[plotname]['status'] = 1
                    process_handle = None
                    t = threading.Thread(target=self.transfer_plot)
                    t.start()
                    break
            except:
                pass

    def transfer_plot(self):
        if self.plot_in_transfer or len(self.pending_plots) == 0:
            reason = f'Transferring plot {self.plot_in_transfer}' if self.plot_in_transfer else 'No plot to transfer'
            self.app.logger.info(f'Skipping transfer, reason: {reason}')
            return

        plot = None
        for k in self.pending_plots.keys():
            if self.pending_plots[k]['status']:
                plot = k
        if plot:
            self.plot_in_transfer = plot
            try:
                self.app.reload_configs()
                dest = self.get_destination_dir()
                if dest:
                    new_dir = os.path.join(
                        dest, f'{os.path.basename(self.plot_in_transfer)}.plot')
                    self.app.logger.info(f'Move {plot} > {dest}')
                    ts = time.time()
                    shutil.move(self.pending_plots[plot]['path'],  new_dir)
                    elapsed = math.floor(time.time() - ts)
                    self.app.logger.info(
                        f'Move {plot} completed in {elapsed} secs')
                    self.pending_plots.pop(plot)
                    self.plot_in_transfer = None
                    t = threading.Thread(target=self.transfer_plot)
                    t.start()
                else:
                    self.app.logger.info("Unable to get destination dir")
                    self.plot_in_transfer = None
            except Exception as e:
                self.plot_in_transfer = None
                self.app.logger.warning(str(e))

    def get_destination_dir(self):
        folders = self.app.get_state('chiaplotter', 'dir_dest[]')
        result = False
        for folder in folders:
            disk_usage_stat = shutil.disk_usage(folder)
            free_gib = round(disk_usage_stat.free / (2**30), 2)
            capacity = math.floor(free_gib / self.plot_size)
            self.app.logger.info(
                f'  >> {folder} free {free_gib} GiB capacity {capacity}')
            if capacity:
                result = folder
                break
        return result

    def check_capacity(self, amount):
        self.app.logger.info(f'Check capacity for {amount} plots')
        folders = self.app.get_state('chiaplotter', 'dir_dest[]')
        result = False
        total_capacity = 0
        for folder in folders:
            disk_usage_stat = shutil.disk_usage(folder)
            free_gib = round(disk_usage_stat.free / (2**30), 2)
            capacity = math.floor(free_gib / self.plot_size)
            total_capacity = total_capacity + capacity
            if total_capacity >= amount:
                result = True
                break
        self.app.logger.info(f'Total >= {total_capacity}')
        return result
