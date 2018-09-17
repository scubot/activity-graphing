import discord
import matplotlib
import tqdm
import shlex
import time
import copy
from tinydb import TinyDB, Query
from modules.botModule import *


class Scraper:
    def __init__(self, _database, _client, _server):
        database = _database
        client = _client
        server = _server

    def initial_scrape(self):
        pass

    def last_scraped(self, table):
        pass

    def update(self):
        for c in self.server.channels:
            # Open the table
            table = self.database.table(c.id)
            last = self.client.get_message(c, self.last_scraped(table))


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
            pass
        else:
            pass
