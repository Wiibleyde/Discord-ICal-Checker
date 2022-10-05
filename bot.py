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
Timezone="Europe/Paris"

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

def download_ical():
    try:
        r = requests.get(CalUrl, allow_redirects=True)
        open('calendar.ics', 'wb').write(r.content)
    except:
        print("Error downloading calendar")
        sys.exit(1)

def parse_ical():
    try:
        cal = icalendar.Calendar.from_ical(open('calendar.ics', 'rb').read())
    except:
        print("Error parsing calendar")
        sys.exit(1)
    return cal

def getNextEvent(cal):
    for event in cal.walk('vevent'):
        if event.get('dtstart').dt > datetime.datetime.now(pytz.timezone(Timezone)):
            return event

def CalcTimeLeft(event):
    timeleft = event.get('dtstart').dt - datetime.datetime.now(pytz.timezone(Timezone))
    return timeleft

def send_webhook_soon(event):
    webhook = discord_webhook.DiscordWebhook(url=WebhookUrl, content="Le prochain cours : " + event.get('summary') + ", commence dans moins d'une heure !")
    response = webhook.execute()

def send_webhook_nothing(event, timeleft):
    webhook = discord_webhook.DiscordWebhook(url=WebhookUrl, content=f"Il n'y a pas de cours dans les prochaines heures.\nProchain évenement : {event.get('summary')} dans {getHours(timeleft)} heures et {getMinutes(timeleft)} minutes.")
    response = webhook.execute()

def delete_ical():
    os.remove("calendar.ics")

def getMinutes(timeleft):
    return timeleft.seconds // 60

def getHours(timeleft):
    return timeleft.seconds // 3600

if __name__ == "__main__":
    client.run(BotToken)