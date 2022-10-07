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

client = discord.Client()

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

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

async def my_background_task():
    await client.wait_until_ready()
    count=0
    while not client.is_closed():
        if count == 30:
            download_ical()
            count=0
        else:
            count=count+1
        cal=parse_ical()
        event=getNextEvent(cal)
        timeleft=CalcTimeLeft(event)
        print("Reload status")
        if isMoreThanDay(timeleft):
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=getTitle(event.get('summary')) + " dans plus d'un jour"))
        else:
            await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=getTitle(event.get('summary')) + " dans " + str(getHours(timeleft)) + "h" + str(getMinutes(timeleft)) + "m"))
        await asyncio.sleep(60)

client.loop.create_task(my_background_task())

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
    if getHours(timeleft) < 0:
        return 0
    elif getHours(timeleft) > 4:
        return datetime.timedelta(hours=0,minutes=0)
    return timeleft

def delete_ical():
    os.remove("calendar.ics")

def getMinutes(timeleft):
    return timeleft.seconds // 60

def getHours(timeleft):
    return timeleft.seconds // 3600

def getTitle(event):
    return event.split(" - ")[0]

def isMoreThanDay(timeleft):
    return timeleft.days > 0

if __name__ == "__main__":
    client.run(BotToken)