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

    async def determine_start_message(self, table, channel):
        table_last = len(table)
        while True:
            obj = await self.client.get_message(channel, table.get(doc_id=table_last)['id'])
            if obj is not None:
                return obj
            else:
                table_last -= 1

    async def update(self, c):
        # Open the table
        x = tqdm.tqdm(mininterval=2, unit=' messages')
        table = self.database.table(c.id)
        # If the channel has never been scraped before...
        if len(table) == 0:
            last_scraped_msg = None
        # If the channel has been scraped before, go through the list of last messages...
        else:
            last_scraped_msg = await self.determine_start_message(table, c)
        protected_table = self.database.table('protected')
        if protected_table.get(Query().id == c.id):
            return 0  # Just end here.
        # IDE may complain but that's because it doesn't know self.client is a discord.Client()
        table_cache = []
        async for fetched_message in self.client.logs_from(c, after=last_scraped_msg, limit=10000000000):
            table_cache.append({'id': fetched_message.id, 'timestamp': fetched_message.timestamp.timestamp(),
                                'author': fetched_message.author.id, 'content': fetched_message.content})
            x.update(1)
        table_cache.reverse()
        table.insert_multiple(table_cache)
        x.close()
        del x

    async def update_all(self):
        for c in self.server.channels:
            print("Now scraping" + c.name)
            await self.update(c)

    async def update_one(self, channel_to_update):
        await self.update(channel_to_update)


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
                await scraper.update_one(message.channel_mentions[0])
            else:
                await scraper.update_all()
            pass
        else:
            pass
