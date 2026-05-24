import discord
from discord.ext import tasks
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import os

TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ROLE_ID = int(os.getenv("ROLE_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

WAR_START = datetime(2026, 5, 31, tzinfo=ZoneInfo("Europe/Malta"))

sent_cache = set()

def is_war_week(now):
    delta_days = (now.date() - WAR_START.date()).days

    if delta_days < 0:
        return False

    week_number = delta_days // 7
    return week_number % 2 == 0

def get_event_name(now):
    weekday = now.weekday()

    crimson_hours = [7, 15, 23]
    spider_dragon_hours = [2, 10, 18]

    if now.hour in crimson_hours:
        return "Crimson Moon"

    if now.hour in spider_dragon_hours:
        if weekday in [6, 0]:  # Sunday + Monday
            return "Spider"
        else:
            return "Dragon"

    return None

@tasks.loop(minutes=1)
async def reminder_loop():
    now = datetime.now(ZoneInfo("Europe/Malta"))

    if not is_war_week(now):
        return

    if now.minute != 0:
        return

    event_name = get_event_name(now)

    if not event_name:
        return

    unique_key = f"{now.strftime('%Y-%m-%d-%H')}"

    if unique_key in sent_cache:
        return

    sent_cache.add(unique_key)

    channel = client.get_channel(CHANNEL_ID)

    if channel:
        await channel.send(f"<@&{ROLE_ID}> Time for {event_name}!")

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    reminder_loop.start()

client.run(TOKEN)