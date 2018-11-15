from tqdm import tqdm
import argparse
import datetime
import time
import copy

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class Grapher:

    graph_path = './modules/activity/graphs/graph.png'

    # the variable messages refers to what get_from_db returns.
    def __init__(self, *, database, client, server, response_channel):
        self.database = database
        self.client = client
        self.server = server
        self.response_channel = response_channel

    def get_from_db(self, channel):

        table = self.database.table(channel.id)
        if not table:
            return []  # return an empty list of messages
        else:
            list_to_return = table.all()
            for entry in list_to_return:
                entry['timestamp'] = datetime.datetime.utcfromtimestamp(entry['timestamp'])
            return list_to_return

    @staticmethod
    def refine_user(author, messages):
        return [entry for entry in messages if messages['author'] == author.id]

    @staticmethod
    def refine_time(time_range, messages):
        return [entry for entry in messages if time_range[0] < messages['timestamp'] < time_range[1]]

    @staticmethod
    def refine_search(search, messages):
        return [entry for entry in messages if str(search) in messages['content']]

    async def fetch_some(self, channels, mode):
        messages = []
        for channel in channels:
            messages += self.get_from_db(channel)
        messages = await self.filter_messages(mode, messages)
        graph = self.make_graph(messages)
        self.client.send_file(self.response_channel, graph, "Graph")


    async def fetch_all(self, mode):
        messages = []
        for channel in self.server.channels:
            messages += self.get_from_db(channel)
        messages = await self.filter_messages(mode, messages)
        graph = self.make_graph(messages)
        self.client.send_file(self.response_channel, graph)

    async def filter_messages(self, mode, messages):
        if not mode:
            pass

        elif mode[0] == 'user':
            if len(mode) != 2:
                self.client.send_message(self.response_channel, "[!] Invalid number of arguments for specified mode.")
                return 0
            else:
                messages = self.refine_user(mode[1], messages)
                pass
            
        elif mode[0] == 'time':
            if len(mode) != 3:
                self.client.send_message(self.response_channel, "[!] Invalid number of arguments for specified mode.")
                return 0
            else:
                messages = self.refine_time([mode[1], mode[2]], messages)
                pass

        elif mode[0] == 'search':
            if len(mode) != 2:
                self.client.send_message(self.response_channel, "[!] Invalid number of arguments for specified mode.")
                return 0
            else:
                messages = self.refine_search(mode[1], messages)
                pass
        else:
            await self.client.send_message(self.response_channel, "[!] Invalid graphing mode.")
            return 0

        return messages

    def make_graph(self, messages):
        for line in messages:
            raw_ts = line['timestamp'].timestamp()
            second = datetime.timedelta(seconds=int((raw_ts-345600) % 604800))
            hour = datetime.datetime(1, 1, 1) + second
            line['timestamp'] = hour.hour + ((hour.day-1)*24)
        hour_list = [x['timestamp'] for x in messages]
        hour_list = [[x, hour_list.count(x)] for x in set(hour_list)]
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

        plt.savefig(self.graph_path)
        return open(self.graph_path, 'rb')

