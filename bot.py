import discord 
from discord.ext import commands
import os
import requests
import icalendar
import datetime
import pytz
import sys
import os

CalUrl="https://hp22.ynov.com/BOR/Telechargements/ical/Edt_BONNELL.ics?version=2022.0.3.1&idICal=BB1309C5D04314FC29CBCE40092D7C09&param=643d5b312e2e36325d2666683d3126663d31"
BotToken=""

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('$edt'):
        await message.channel.send('Voici ton emploi du temps :')
        await message.channel.send(file=discord.File('edt.png'))

if __name__ == "__main__":
    client.run(BotToken)