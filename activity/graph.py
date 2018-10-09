from tqdm import tqdm
import argparse
import datetime
import time
import copy

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Grapher:
    # the variable pack refers to what get_from_db returns.
    def __init__(self, *, database, client, server):
        self.database = database
        self.client = client
        self.server = server

    def get_from_db(self, channel):
        table = self.database.table(channel.id)
        if not table:
            return None
        else:
            list_to_return = table.all()
            for entry in list_to_return:
                entry['timestamp'] = datetime.datetime.utcfromtimestamp(entry['timestamp'])
            return list_to_return

    @staticmethod
    def refine_user(author, pack):
        return [entry for entry in pack if pack['author'] == author.id]

    @staticmethod
    def refine_time(time_range, pack):
        return [entry for entry in pack if time_range[0] < pack['timestamp'] < time_range[1]]

    @staticmethod
    def refine_search(search, pack):
        return [entry for entry in pack if str(search) in pack['content']]

    def graph_users(self, pack):
        pass

    def graph_long(self, pack):
        for line in pack:
            line['timestamp'] = datetime.date.fromtimestamp(line[0])
            line.pop('content', None)
        flat = [x['timestamp'] for x in pack]
        flat = [[x, flat.count(x)] for x in set(flat)]
        r = np.asarray(flat)
        r = r[r[:,0].argsort()]
        years = mdates.YearLocator()
        months = mdates.MonthLocator()
        yearsFmt = mdates.DateFormatter('%Y')
        fig, ax = plt.subplots()
        ax.plot(r[:,0],r[:,1])
        ax.xaxis.set_major_locator(years)
        ax.xaxis.set_major_formatter(yearsFmt)
        ax.xaxis.set_minor_locator(months)
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        ax.grid(True)
        fig.autofmt_xdate()
        plt.xlabel("Date")
        plt.ylabel("Messages")

    @staticmethod
    def graph_weekhour(pack):
        for line in pack:
            second = datetime.timedelta(seconds=int((line['timestamp']-345600) % 604800))
            hour = datetime.datetime(1, 1, 1) + second
            line['timestamp'] = hour.hour + ((hour.day-1)*24)
        hour_list = [x['timestamp'] for x in pack]
        hour_list = [[x, hour_list.count(x)] for x in set(hour_list)]
        hour_list = np.asarray(hour_list)
        r = np.asarray(hour_list)
        r = r[r[:, 0].argsort()]
        fig, ax = plt.subplots()
        ax.plot(r[:, 0], r[:, 1])
        ax.grid(True)
        plt.xlabel("Day of Week (Starts Sunday 0000UTC)")
        plt.ylabel("Messages")
        plt.xticks([0, 24, 48, 72, 96, 120, 144, 168],
                   ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        plt.xlim([0, 168])





