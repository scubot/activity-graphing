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
import os


class Scraper:
    def __init__(self, *, database, client, server, response_channel):
        self.database = database
        self.client = client
        self.server = server
        self.response_channel = response_channel

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
        bar = tqdm.tqdm(total=0, unit=' messages', file=open(os.devnull, 'w'))
        message_return = await self.client.send_message(self.response_channel, bar)
        last_edit = time.time()
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
            time_now = time.time()
            table_cache.append({'id': fetched_message.id, 'timestamp': fetched_message.timestamp.timestamp(),
                                'author': fetched_message.author.id, 'content': fetched_message.content})
            bar.update(1)
            if time_now - last_edit >= 2:
                updated = str(bar)
                await self.client.edit_message(message_return, updated)
                last_edit = time.time()
        table_cache.reverse()
        table.insert_multiple(table_cache)
        bar.close()
        del bar

    async def update_all(self):
        for c in self.server.channels:
            await self.client.send_message(self.response_channel, "Now fetching #" + c.name)
            await self.update(c)

    async def update_one(self, channel_to_update):
        await self.client.send_message(self.response_channel, "Now fetching #" + channel_to_update.name)
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
            scraper = Scraper(database=self.module_db, client=client, server=message.server,
                              response_channel=message.channel)
            if message.channel_mentions:
                await scraper.update_one(message.channel_mentions[0])
            else:
                await scraper.update_all()
            pass
        else:
            pass
