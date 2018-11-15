import discord
import matplotlib
import tqdm
import shlex
import time
import copy
from modules.botModule import *
import modules.activity.scraper as scr
import modules.activity.graph as gra
import asyncio
import datetime
import os


class Activity(BotModule):
    name = 'activity'

    description = 'Graphs server activity.'

    help_text = '...'

    trigger_string = 'activity'

    module_version = '1.0.0'

    async def parse_command(self, message, client):
        msg = shlex.split(message.content)
        if msg[1] == 'update':
            scraper = scr.Scraper(database=self.module_db, client=client, server=message.server,
                                  response_channel=message.channel)
            if message.channel_mentions:
                await scraper.update_one(message.channel_mentions[0])
            else:
                await scraper.update_all()
        elif msg[1] == 'graph':
            msg.pop(0) # leave just any graphing properties left
            msg.pop(0)
            grapher = gra.Grapher(database=self.module_db, client=client, server=message.server,
                                  response_channel=message.channel)
            if message.channel_mentions:
                await grapher.fetch_some(message.channel_mentions, msg)
            else:
                await grapher.fetch_all(msg)
