import discord
import matplotlib
import tqdm
import shlex
import time
import copy
from tinydb import TinyDB, Query
from modules.botModule import *
import asyncio
import datetime

class Scraper:
    def __init__(self, _database, _client, _server):
        self.database = _database
        self.client = _client
        self.server = _server

    def initial_scrape(self):
        pass

    def determine_start_message(self, li, channel):
        for message in li:
            obj = self.client.get_message(channel, message)
            if obj is not None:
                return obj

    def update(self, c):
        # Open the table
        table = self.database.table(c.id)
        last_scraped = self.database.table('last_scraped')
        last_scraped_msg = last_scraped.get(Query().channel_id == c.id)
        # If the channel has never been scraped before this will be None...
        if not last_scraped_msg:
            pass
        # If the channel has been scraped before, go through the list of last messages...
        else:
            last_scraped_msg = self.determine_start_message(last_scraped_msg['buffer'], c)
        protected_table = self.database.table('protected')
        if protected_table.get(Query().id == c.id):
            return 0 # Just end here.
        last_scraped_buffer = []
        # IDE may complain but that's because it doesn't know self.client is a discord.Client()
        async for fetched_message in self.client.logs_from(c, after=last_scraped_msg, limit=10000000000):
            table.insert({'id': fetched_message.id, 'timestamp': fetched_message.timestamp.timestamp(),
                          'author': fetched_message.author.id, 'content': fetched_message.content})
            last_scraped_buffer.append(fetched_message.id)
        last_scraped.upsert({'channel_id': c.id, 'buffer': last_scraped_buffer[10:]})

    def update_all(self):
        for c in self.server.channels:
            self.update(c)

    def update_one(self, channel_to_update):
        self.update(channel_to_update)


class Activity(BotModule):
    name = 'activity'

    description = 'Graphs server activity.'

    help_text = '...'

    trigger_string = 'activity'

    module_version = '1.0.0'

    async def parse_command(self, message, client):
        msg = shlex.split(message.content)
        if msg[1] == 'update':
            scraper = Scraper(self.module_db, client, message.server)
            if message.channel_mentions:
                scraper.update_one(message.channel_mentions[0])
            else:
                scraper.update_all()
            pass
        else:
            pass
