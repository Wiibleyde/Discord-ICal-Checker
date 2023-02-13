import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import requests
import datetime
import sqlite3
import os
import asyncio
import pytz
import icalendar
import sys

class Config:
    def __init__(self, fileName):
        self.fileName = fileName
        self.data = self.loadFile()
        self.token = self.data["Token"]
        self.CalUrl = self.data["ICal Link"]
        self.timezone = self.data["Timezone"]
        self.adminName = self.data["AdminName"]

    def createFile(self):
        with open(self.fileName, "w") as f:
            json.dump({"Token": "", "ICal Link": "", "Timezone": "Europe/Paris","AdminName":""}, f, indent=4)

    def loadFile(self):
        try:
            with open(self.fileName, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            self.createFile()
            print("Created config file")
            print("Please fill in the config file")
            exit()

    def setKey(self, key, value):
        self.data[key] = value
        self.saveFile()

    def getKey(self, key):
        return self.data[key]

    def saveFile(self):
        with open(self.fileName, "w") as f:
            json.dump(self.data, f, indent=4)

class DataLogs:
    def __init__(self, fileName):
        self.fileName = fileName
        req = "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, command TEXT, date TEXT)"
        self.conn = sqlite3.connect(self.fileName)
        self.cursor = self.conn.cursor()
        self.cursor.execute(req)
        self.conn.commit()
    
    def addLog(self, user_id, command):
        req = "INSERT INTO logs (user_id, command, date) VALUES (?, ?, ?)"
        self.cursor.execute(req, (user_id, command, datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        self.conn.commit()

    def getLogs(self):
        req = "SELECT * FROM logs"
        self.cursor.execute(req)
        return self.cursor.fetchall()

    def getLogsByUser(self, user_id):
        req = "SELECT * FROM logs WHERE user_id=?"
        self.cursor.execute(req, (user_id,))
        return self.cursor.fetchall()

    def getLogsByCommand(self, command):
        req = "SELECT * FROM logs WHERE command=?"
        self.cursor.execute(req, (command,))
        return self.cursor.fetchall()

    def getLogsByDate(self, date):
        req = "SELECT * FROM logs WHERE date=?"
        self.cursor.execute(req, (date,))
        return self.cursor.fetchall()

    def getLogsByUserAndCommand(self, user_id, command):
        req = "SELECT * FROM logs WHERE user_id=? AND command=?"
        self.cursor.execute(req, (user_id, command))
        return self.cursor.fetchall()

    def getLogsByUserAndDate(self, user_id, date):
        req = "SELECT * FROM logs WHERE user_id=? AND date=?"
        self.cursor.execute(req, (user_id, date))
        return self.cursor.fetchall()

    def getLogsByCommandAndDate(self, command, date):
        req = "SELECT * FROM logs WHERE command=? AND date=?"
        self.cursor.execute(req, (command, date))
        return self.cursor.fetchall()

    def getLogsByUserAndCommandAndDate(self, user_id, command, date):
        req = "SELECT * FROM logs WHERE user_id=? AND command=? AND date=?"
        self.cursor.execute(req, (user_id, command, date))
        return self.cursor.fetchall()

def download_ical():
    try:
        r = requests.get(CalUrl, allow_redirects=True)
        open('calendar.ics', 'wb').write(r.content)
        showerfunc("Calendar downloaded")
    except:
        showerfunc("Error downloading calendar")
        sys.exit(1)

def parse_ical():
    try:
        cal = icalendar.Calendar.from_ical(open('calendar.ics', 'rb').read())
        return cal
    except:
        showerfunc("Error parsing calendar")

def getEventDate(event):
    if type(event.get('dtstart').dt) is datetime.date:
        return datetime.datetime.combine(event.get('dtstart').dt, datetime.time(0, 0, 0), tzinfo=pytz.timezone(Timezone))
    return event.get('dtstart').dt

def getNextEvent(cal):
    """Return the next event in the calendar

    Args:
        cal (icalendar.Calendar): The calendar

    Returns:
        icalendar.Event: The next event
    """
    events = getAllEvents(cal)
    sorted_events = sorted(events, key=lambda event: getEventDate(event))
    now=datetime.datetime.now(pytz.timezone(Timezone))
    for event in sorted_events:
        if getEventDate(event) > now:
            if getTitle(event.get('summary')) == "Férié":
                continue
            return event

def showerfunc(message):
    """Print a message to showerfunc
    
    Args:
        message (string): The message to print

    Returns:
        None
    """
    print(message)

def getAllEvents(cal):
    """Return all events in the calendar

    Args:
        cal (icalendar.Calendar): The calendar

    Returns:
        list: List of icalendar.Event
    """
    events = []
    for event in cal.walk('vevent'):
        events.append(event)
    return events

def CalcTimeLeft(event):
    """Return the time left before the event

    Args:
        event (icalendar.Event): The event

    Returns:
        datetime.timedelta: The time left
    """
    timeleft=getEventDate(event)-datetime.datetime.now(pytz.timezone(Timezone))
    if getHours(timeleft) < 0:
        return 0
    return timeleft

def delete_ical():
    """Delete the calendar file

    Returns:
        None
    """
    try:
        os.remove("calendar.ics")
        showerfunc("Calendar deleted")
    except:
        showerfunc("Error deleting calendar")

def getMinutes(timeleft):
    """Return the minutes left before the event
    
    Args:
        timeleft (datetime.timedelta): The time left

    Returns:
        int: The minutes left
    """
    return timeleft.seconds // 60 - getHours(timeleft) * 60

def getHours(timeleft):
    """Return the hours left before the event

    Args:
        timeleft (datetime.timedelta): The time left

    Returns:
        int: The hours left
    """
    return timeleft.seconds // 3600

def getTitle(event):
    """Return the title of the event

    Args:
        event (string): The event

    Returns:
        string: The title
    """
    return event.split(" - ")[0]

def isMoreThanDay(timeleft):
    """Return if the time left is more than a day

    Args:
        timeleft (datetime.timedelta): The time left

    Returns:
        bool: True if more than a day, False otherwise
    """
    return timeleft.days > 0

def InEvent(cal):
    """Return if the bot is in an event

    Args:
        cal (icalendar.Calendar): The calendar

    Returns:
        bool: True if in an event, False otherwise
    """
    for event in cal.walk('vevent'):
        if getEventDate(event) < datetime.datetime.now(pytz.timezone(Timezone)) and getEventDate(event) + datetime.timedelta(minutes=30) > datetime.datetime.now(pytz.timezone(Timezone)):
            return True
    return False

def getEventsWeek(cal):
    """Return the events of the week

    Args:
        cal (icalendar.Calendar): The calendar

    Returns:
        list: List of icalendar.Event
    """
    events = []
    sorted_events = sortEvents(cal)
    for event in sorted_events:
        if getEventDate(event) > datetime.datetime.now(pytz.timezone(Timezone)) and getEventDate(event) < datetime.datetime.now(pytz.timezone(Timezone)) + datetime.timedelta(days=7):
            if getTitle(event.get('summary')) == "Férié":
                continue
            events.append(event)
    return events

def sortEvents(cal):
    """Return the events sorted by date

    Args:
        cal (icalendar.Calendar): The calendar

    Returns:
        list: List of icalendar.Event
    """    
    events = []
    for event in cal.walk('vevent'):
        events.append(event)
    return sorted(events, key=lambda event: getEventDate(event))

async def tryDownloadCalendar():
    """Try to download the calendar

    Returns:
        None
    """
    CalDownloaded=False
    while not CalDownloaded:
        try:
            download_ical()
            CalDownloaded=True
        except:
            await asyncio.sleep(60)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Bot is ready")
    ChangeStatus.start()
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
        print(f"Commands: {synced}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.tree.command(name="next", description="Affiche le prochain cours")
async def nextCourse(interaction: discord.Interaction):
    logs.addLog(interaction.user.id,"next")
    calenderParsed = parse_ical()
    try:
        event = getNextEvent(calenderParsed)
        timeleft = CalcTimeLeft(event)
    except:
        embed = discord.Embed(title="Prochain cours", description="Pas de cours", color=0x00ff00)
        await interaction.response.send_message(embed=embed)
        return
    if isMoreThanDay(timeleft):
        embed = discord.Embed(title="Prochain cours", description=f"Le prochain cours à venir.", color=0x00ff00)
        embed.add_field(name=f"{getTitle(event.get('summary'))}", value=f"Dans {timeleft.days} jours", inline=False)
    else:
        embed = discord.Embed(title="Prochain cours", description=f"Le prochain cours à venir.", color=0x00ff00)
        embed.add_field(name=f"{getTitle(event.get('summary'))}", value=f"Dans {getHours(timeleft)}h{getMinutes(timeleft)}", inline=False)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="week", description="Affiche les cours de la semaine")
async def weekCourse(interaction: discord.Interaction):
    logs.addLog(interaction.user.id,"week")
    cal = parse_ical()
    WeekEvents = getEventsWeek(cal)
    if len(WeekEvents) == 0:
        embed=discord.Embed(title="Cours de la semaine", description="Pas de cours", color=0xff0000)
        await interaction.response.send_message(embed=embed)
        return
    embed = discord.Embed(title="Cours de la semaine", description="Liste des cours de la semaine", color=0x00ff00)
    for event in WeekEvents:
        timeleft = CalcTimeLeft(event)
        eventdate = getEventDate(event)
        if eventdate.strftime("%H:%M") == "00:00":
            eventdate = eventdate.strftime("%d/%m")
        else:
            eventdate = (eventdate + datetime.timedelta(hours=1)).strftime("%d/%m %H:%M")
        embed.add_field(name=getTitle(event.get('summary')), value=eventdate, inline=False)  
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="update", description="Mets à jour le calendrier")
async def updateCalendar(interaction: discord.Interaction):
    logs.addLog(interaction.user.id,"update")
    if interaction.author.id != 200954812481282049:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande")
        return
    await interaction.response.send_message("Mise à jour du calendrier...")
    await tryDownloadCalendar()
    await interaction.response.send_message("Mise à jour terminée")

@bot.tree.command(name="help", description="Affiche l'aide")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="Aide", description="Liste des commandes", color=0x00ff00)
    for command in bot.tree.commands:
        embed.add_field(name=command.name, value=command.description, inline=False)
    await interaction.response.send_message(embed=embed)

@tasks.loop(seconds=60)
async def ChangeStatus():
    await bot.wait_until_ready()
    count=0
    while not bot.is_closed():
        try:
            if count == 30:
                delete_ical()
                download_ical()
                count=0
            else:
                count=count+1
                showerfunc("Waiting " + str(30-count) + " minutes")
            cal=parse_ical()
            try:
                event=getNextEvent(cal)
                timeleft=CalcTimeLeft(event)
                if isMoreThanDay(timeleft):
                    await bot.change_presence(activity=discord.Game(name=getTitle(event.get('summary')) + " dans " + str(timeleft.days) + " jours"))
                else:
                    await bot.change_presence(activity=discord.Game(name=getTitle(event.get('summary')) + " dans " + str(getHours(timeleft)) + "h" + str(getMinutes(timeleft)) + "m"))
            except:
                showerfunc("No event found or error")
                await bot.change_presence(activity=discord.Game(name="Aucun cours prévu ou erreur"))
            await asyncio.sleep(60)
        except Exception as e:
            await bot.change_presence(activity=discord.Game(name=f"Erreur: {e}"))
            await asyncio.sleep(60)

if __name__ == "__main__":
    config = Config("config.json")
    TOKEN = config.token
    CalUrl = config.CalUrl
    Timezone = config.timezone
    logs = DataLogs("database.db")
    delete_ical()
    download_ical()
    bot.run(TOKEN)
