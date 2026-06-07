import discord
from discord.ext import tasks
from datetime import datetime
from zoneinfo import ZoneInfo
import os

TOKEN = os.getenv("DISCORD_TOKEN")

WAR_ROLE_ID = int(os.getenv("WAR_ROLE_ID"))
BATTLEFIELD_ROLE_ID = int(os.getenv("BATTLEFIELD_ROLE_ID"))

WAR_CHANNEL_ID = 1484346112696516729
BATTLEFIELD_CHANNEL_ID = 1513181468325576734

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

def is_battlefield_dragon_time(now):
    return now.hour in [3, 9, 15, 21]

@tasks.loop(minutes=1)
async def reminder_loop():
    now = datetime.now(ZoneInfo("Europe/Malta"))

    if now.minute != 0:
        return

    # War Inc clan war reminders
    if is_war_week(now):
        event_name = get_event_name(now)

        if event_name:
            unique_key = f"war-{now.strftime('%Y-%m-%d-%H')}"

            if unique_key not in sent_cache:
                sent_cache.add(unique_key)

                war_channel = client.get_channel(WAR_CHANNEL_ID)

                if war_channel:
                    await war_channel.send(
                        f"<@&{WAR_ROLE_ID}> Time for {event_name}!"
                    )

    # Battlefield Dragon reminders
    if is_battlefield_dragon_time(now):
        unique_key = f"battlefield-{now.strftime('%Y-%m-%d-%H')}"

        if unique_key not in sent_cache:
            sent_cache.add(unique_key)

            battlefield_channel = client.get_channel(BATTLEFIELD_CHANNEL_ID)

            if battlefield_channel:
                await battlefield_channel.send(
                    f"<@&{BATTLEFIELD_ROLE_ID}> Battlefield Dragon is available!"
                )

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    if not reminder_loop.is_running():
        reminder_loop.start()

client.run(TOKEN)