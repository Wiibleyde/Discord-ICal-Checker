import discord 
import os
import requests
import icalendar
import datetime
import pytz
import sys
import asyncio

CalUrl="https://hp22.ynov.com/BOR/Telechargements/ical/Edt_BONNELL.ics?version=2022.0.3.1&idICal=BB1309C5D04314FC29CBCE40092D7C09&param=643d5b312e2e36325d2666683d3126663d31"
BotToken="MTAyNzIxOTY0MjY0NjgwNjYzOA.GWN6_v.YQYWI78QIsfPD9ljgjBcBcRqKLfuRRzh2vvuec"
Timezone="Europe/Paris"
AdminId="461807010086780930"

client = discord.Client()

@client.event
async def on_ready():
    stderr("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$next'):
        cal = parse_ical()
        event = getNextEvent(cal)
        timeleft = CalcTimeLeft(event)
        if isMoreThanDay(timeleft):
            await message.channel.send("Prochain cours dans plus d'un jour : " + getTitle(event.get('summary')))
        else:
            await message.channel.send("Le prochain évenement est " + event.get('summary') + " dans " + str(getHours(timeleft)) + "h" + str(getMinutes(timeleft)) + "m")

    if message.content.startswith('$help'):
        await message.channel.send("Commands : $next, $help")

    if message.content.startswith('$update') and message.author.id == AdminId:
        download_ical()
        await message.channel.send("Calendar updated")

async def my_background_task():
    await client.wait_until_ready()
    count=0
    while not client.is_closed():
        if count == 30:
            delete_ical()
            download_ical()
            count=0
        else:
            count=count+1
            stderr("Waiting " + str(30-count) + " minutes")
        cal=parse_ical()
        event=getNextEvent(cal)
        timeleft=CalcTimeLeft(event)
        stderr("Next event in : " + str(timeleft) + " : " + event.get('summary') + " : " + getEventDate(event).strftime("%d/%m/%Y %H:%M:%S"))
        stderr("Reload status")
        if isMoreThanDay(timeleft):
            await client.change_presence(activity=discord.Game(name=getTitle(event.get('summary')) + " dans plus d'un jour"))
        else:
            await client.change_presence(activity=discord.Game(name=getTitle(event.get('summary')) + " dans " + str(getHours(timeleft)) + "h" + str(getMinutes(timeleft)) + "m"))
        await asyncio.sleep(60)

client.loop.create_task(my_background_task())

def download_ical():
    try:
        r = requests.get(CalUrl, allow_redirects=True)
        open('calendar.ics', 'wb').write(r.content)
    except:
        stderr("Error downloading calendar")
        sys.exit(1)

def parse_ical():
    try:
        cal = icalendar.Calendar.from_ical(open('calendar.ics', 'rb').read())
        return cal
    except:
        stderr("Error parsing calendar")
        sys.exit(1)

def getNextEvent(cal):


def stderr(message):
    sys.stderr.write(message)

def getEventDate(event):
    return event.get('dtstart').dt

def getAllEvents(cal):
    events = []
    for event in cal.walk('vevent'):
        events.append(event)
    return events[0]

def CalcTimeLeft(event):
    timeleft = event.get('dtstart').dt - datetime.datetime.now(pytz.timezone(Timezone))
    if getHours(timeleft) < 0:
        return 0
    return timeleft

def delete_ical():
    try:
        os.remove("calendar.ics")
    except:
        stderr("Error deleting calendar")

def getMinutes(timeleft):
    return timeleft.seconds // 60 - getHours(timeleft) * 60

def getHours(timeleft):
    return timeleft.seconds // 3600

def getTitle(event):
    return event.split(" - ")[0]

def isMoreThanDay(timeleft):
    return getHours(timeleft) > 24

def InEvent(cal):
    for event in cal.walk('vevent'):
        if getEventDate(event) < datetime.datetime.now(pytz.timezone(Timezone)) and getEventDate(event) + datetime.timedelta(hours=2) > datetime.datetime.now(pytz.timezone(Timezone)):
            return True
    return False

if __name__ == "__main__":
    delete_ical()
    download_ical()
    client.run(BotToken)