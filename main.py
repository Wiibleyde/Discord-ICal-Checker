import discord
from discord import app_commands
from discord.ext import commands, tasks
import requests
import datetime
import os
import asyncio
import pytz
import icalendar
import sys

from src.config import Config
from src.db import Database, CommandLog, Message

def download_ical():
    try:
        r = requests.get(calendar_url, allow_redirects=True)
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
        return datetime.datetime.combine(event.get('dtstart').dt, datetime.time(0, 0, 0), tzinfo=pytz.timezone(timezone))
    return event.get('dtstart').dt

def getEventEndDate(event):
    if type(event.get('dtend').dt) is datetime.date:
        return datetime.datetime.combine(event.get('dtend').dt, datetime.time(0, 0, 0), tzinfo=pytz.timezone(timezone))
    return event.get('dtend').dt

def getNowEvent(cal):
    # Return the event that is happening now (so beginning before now and ending after now)
    now = datetime.datetime.now(pytz.timezone(timezone))
    for event in cal.walk('vevent'):
        if getEventDate(event) < now and getEventEndDate(event) > now:
            return event
    return None

def getNextEvent(cal):
    """Return the next event in the calendar

    Args:
        cal (icalendar.Calendar): The calendar

    Returns:
        icalendar.Event: The next event
    """
    events = getAllEvents(cal)
    sorted_events = sorted(events, key=lambda event: getEventDate(event))
    now=datetime.datetime.now(pytz.timezone(timezone))
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
    timeleft=getEventDate(event)-datetime.datetime.now(pytz.timezone(timezone))
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
    try:
        return event.split(" - ")[0]
    except:
        return event

def getTeacher(event):
    """Return the teacher of the event

    Args:
        event (string): The event

    Returns:
        string: The teacher
    """
    try:
        return event.split(" - ")[1]
    except:
        return ""

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
        if getEventDate(event) < datetime.datetime.now(pytz.timezone(timezone)) and getEventDate(event) + datetime.timedelta(minutes=30) > datetime.datetime.now(pytz.timezone(timezone)):
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
        if getEventDate(event) > datetime.datetime.now(pytz.timezone(timezone)) and getEventDate(event) < datetime.datetime.now(pytz.timezone(timezone)) + datetime.timedelta(days=7):
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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Starting..."))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
        print(f"Commands: {synced}")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    if not os.path.exists("calendar.ics"):
        RedownloadCalendar.start()
    if not os.path.exists("calendar.ics"):
        await ForceUpdate.start()
    ChangeStatus.start()
    print("Bot has started and all tasks are running")

@bot.tree.command(name="next", description="Affiche le prochain cours")
async def nextCourse(interaction: discord.Interaction):
    logs.insert_log(CommandLog(date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), user=interaction.user.id, command="next"))
    calenderParsed = parse_ical()
    try:
        event = getNextEvent(calenderParsed)
        timeleft = CalcTimeLeft(event)
    except:
        embed = discord.Embed(title="Prochain cours", description="Pas de cours", color=0x00ff00)
        embed.set_footer(text="NatCalBot",icon_url="https://cdn.discordapp.com/avatars/1027219642646806638/6f2d37b52874067f006b5b249bfd65a9")
        await interaction.response.send_message(embed=embed)
        return
    if isMoreThanDay(timeleft):
        embed = discord.Embed(title="Prochain cours", description=f"Le prochain cours à venir.", color=0x00ff00)
        embed.set_footer(text="NatCalBot",icon_url="https://cdn.discordapp.com/avatars/1027219642646806638/6f2d37b52874067f006b5b249bfd65a9")
        if event.get('location') == None:
            event['location'] = "Nowhere"
        embed.add_field(name=f"{getTitle(event.get('summary'))}", value=f"Avec {getTeacher(event.get('summary')) or 'personne'}\nÀ {event.get('location')}\n**Dans {timeleft.days} jours**", inline=False)
    else:
        embed = discord.Embed(title="Prochain cours", description=f"Le prochain cours à venir.", color=0x00ff00)
        embed.set_footer(text="NatCalBot",icon_url="https://cdn.discordapp.com/avatars/1027219642646806638/6f2d37b52874067f006b5b249bfd65a9")
        if event.get('location') == None:
            event['location'] = "Nowhere"
        embed.add_field(name=f"{getTitle(event.get('summary'))}", value=f"Avec {getTeacher(event.get('summary')) or 'personne'}\nÀ {event.get('location')}\n**Dans {getHours(timeleft)}h{getMinutes(timeleft)}**", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="week", description="Affiche les cours de la semaine")
async def weekCourse(interaction: discord.Interaction):
    logs.insert_log(CommandLog(date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), user=interaction.user.id, command="week"))
    cal = parse_ical()
    WeekEvents = getEventsWeek(cal)
    if len(WeekEvents) == 0:
        embed=discord.Embed(title="Cours de la semaine", description="Pas de cours", color=0xff0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    embed = discord.Embed(title="Cours de la semaine", description="Liste des cours de la semaine", color=0x00ff00)
    embed.set_footer(text="NatCalBot",icon_url="https://cdn.discordapp.com/avatars/1027219642646806638/6f2d37b52874067f006b5b249bfd65a9")
    for event in WeekEvents:
        # timeleft = CalcTimeLeft(event)
        eventdate = getEventDate(event)
        if eventdate.strftime("%H:%M") == "00:00":
            eventdate = eventdate.strftime("%d/%m")
        else:
            eventdate = (eventdate + datetime.timedelta(hours=2)).strftime("%d/%m %H:%M")
        if event.get('location') == None:
            event['location'] = "Nowhere"
        embed.add_field(name=f"{getTitle(event.get('summary'))} - {getTeacher(event.get('summary')) or 'personne'}", value=f"{eventdate} à {event.get('location')}", inline=False)  
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="update", description="Mets à jour le calendrier")
async def updateCalendar(interaction: discord.Interaction):
    logs.insert_log(CommandLog(date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), user=interaction.user.id, command="update"))
    if interaction.user.id != 461807010086780930:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande", ephemeral=True)
        return
    await tryDownloadCalendar()
    await interaction.response.send_message("Mise à jour effectuée", ephemeral=True)

@bot.tree.command(name="reload", description="Recharge le status")
async def updateCalendar(interaction: discord.Interaction):
    logs.insert_log(CommandLog(date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), user=interaction.user.id, command="reload"))
    if interaction.user.id != 461807010086780930:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande", ephemeral=True)
        return
    ChangeStatus.restart()
    await interaction.response.send_message("Rechargement effectué", ephemeral=True)

@bot.tree.command(name="help", description="Affiche l'aide")
async def help(interaction: discord.Interaction):
    logs.insert_log(CommandLog(date=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), user=interaction.user.id, command="help"))
    embed = discord.Embed(title="Aide", description="Liste des commandes", color=0x00ff00)
    embed.add_field(name="next", value="Affiche le prochain cours", inline=False)
    embed.add_field(name="week", value="Affiche les cours de la semaine", inline=False)
    embed.add_field(name="update", value="Mets à jour le calendrier", inline=False)
    embed.set_footer(text="NatCalBot",icon_url="https://cdn.discordapp.com/avatars/1027219642646806638/6f2d37b52874067f006b5b249bfd65a9")
    await interaction.response.send_message(embed=embed, ephemeral=True)

@tasks.loop(seconds=120)
async def ChangeStatus():
    calenderParsed = parse_ical()
    try:
        event = getNextEvent(calenderParsed)
        timeleft = CalcTimeLeft(event)
        nowCourse = getNowEvent(calenderParsed)
    except:
        await bot.change_presence(activity=discord.Game(name="Pas de cours"))
        return
    if isMoreThanDay(timeleft):
        await bot.change_presence(activity=discord.Game(name=f"{getTitle(event.get('summary'))} dans {timeleft.days} jours"))
    else:
        await bot.change_presence(activity=discord.Game(name=f"{getTitle(event.get('summary'))} dans {getHours(timeleft)}h{getMinutes(timeleft)}"))
    if nowCourse:
        embed = discord.Embed(title="Cours", description=f"# Cours actuel", color=0x00ff00)
        embed.add_field(name=f"{getTitle(nowCourse.get('summary'))}", value=f"Avec {getTeacher(nowCourse.get('summary')) or 'personne'}\nA {nowCourse.get('location')}\n**Commencé <t:{int(getEventDate(nowCourse).timestamp())}:R>**", inline=False)
        embed.add_field(name=f"Prochain cours : {getTitle(event.get('summary'))}", value=f"Avec {getTeacher(event.get('summary')) or 'personne'} <t:{int(getEventDate(event).timestamp())}:R>", inline=False)
        embed.set_footer(text="NatCalBot",icon_url="https://cdn.discordapp.com/avatars/1027219642646806638/6f2d37b52874067f006b5b249bfd65a9")
        if logs.get_message("now") == None:
            channel = bot.get_channel(channel_update_id)
            message = await channel.send(embed=embed)
            logs.insert_message(Message(message_id=message.id, name="now"))
        else:
            try:
                message = await bot.get_channel(channel_update_id).fetch_message(logs.get_message("now")[1])
                await message.edit(embed=embed)
            except:
                logs.delete_message("now")
                channel = bot.get_channel(channel_update_id)
                message = await channel.send(embed=embed)
                logs.insert_message(Message(message_id=message.id, name="now"))
    else:
        embed = discord.Embed(title="Cours en cours", description=f"Le cours actuel.", color=0x00ff00)
        embed.add_field(name='Aucun cours', value='Pas de cours actuellement', inline=False)
        embed.add_field(name=f"{getTitle(event.get('summary'))}", value=f"Avec {getTeacher(event.get('summary')) or 'personne'} <t:{int(getEventDate(event).timestamp())}:R>", inline=False)
        embed.set_footer(text="NatCalBot",icon_url="https://cdn.discordapp.com/avatars/1027219642646806638/6f2d37b52874067f006b5b249bfd65a9")
        if logs.get_message("now") == None:
            channel = bot.get_channel(channel_update_id)
            message = await channel.send(embed=embed)
            logs.insert_message(Message(message_id=message.id, name="now"))
        else:
            message = await bot.get_channel(channel_update_id).fetch_message(logs.get_message("now")[1])
            await message.edit(embed=embed)

@tasks.loop(hours=1)
async def RedownloadCalendar():
    await tryDownloadCalendar()

@tasks.loop(seconds=30)
async def ForceUpdate():
    if os.path.exists("calendar.ics"):
        await tryDownloadCalendar()
        ForceUpdate.cancel()

if __name__ == "__main__":
    config = Config("config.yaml")
    token = config.get("bot_token")
    calendar_url = config.get("calendar_url")
    timezone = config.get("timezone")
    channel_update_id = int(config.get("channel_update_id"))
    logs = Database("logs.db")
    delete_ical()
    download_ical()
    bot.run(token=token)
