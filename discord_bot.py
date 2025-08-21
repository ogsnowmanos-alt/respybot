import discord
from discord.ext import commands
from datetime import datetime, timedelta
import os
import pytz
import json

# ------------------- KONFIGURACJA -------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

GUILD_ID = 1394086742436614316
CHANNEL_ID = 1394086743061299349

RESP_TIME = timedelta(hours=5, minutes=30)
PING_BEFORE = timedelta(minutes=30)
FUTURE_RESPS = 50  # ile przyszłych respów wygenerować

POLAND_TZ = pytz.timezone("Europe/Warsaw")
RESP_FILE = "resp_schedule.json"

# ------------------- DISCORD BOT -------------------
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

champion_aliases = {
    "kowal": "Kowal Lugusa",
    "straz": "Straż Lugusa"
}

lugus_rotation = {
    "Kowal Lugusa": "Straż Lugusa",
    "Straż Lugusa": "Kowal Lugusa"
}

# ------------------- FUNKCJE -------------------
def next_resp(last_resp):
    return last_resp + RESP_TIME

def utc_to_poland(utc_dt):
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(POLAND_TZ)

def load_resps():
    if os.path.exists(RESP_FILE):
        with open(RESP_FILE, "r") as f:
            data = json.load(f)
            # konwertujemy string na datetime
            return {champ: datetime.fromisoformat(time_str) for champ, time_str in data.items()}
    return {}

def save_resps(resps):
    with open(RESP_FILE, "w") as f:
        json.dump({champ: time.isoformat() for champ, time in resps.items()}, f)

def generate_future_resps(start_champ, start_time):
    schedule = {}
    current_champ = start_champ
    current_time = start_time
    for _ in range(FUTURE_RESPS):
        schedule[current_champ] = current_time
        if current_champ in lugus_rotation:
            current_champ = lugus_rotation[current_champ]
        current_time = next_resp(current_time)
    return schedule

# ------------------- KOMENDY -------------------
@bot.command()
async def resp(ctx):
    resp_times = load_resps()
    if not resp_times:
        await ctx.send("📋 Brak zapisanych respów czempionów.")
        return

    now = datetime.utcnow()
    embed = discord.Embed(title="⏰ Status respów czempionów", color=0x00ff00)
    for champion, resp_time in resp_times.items():
        remaining = resp_time - now
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours}h {minutes}m {seconds}s"
            status = f"🕐 Za: **{time_str}**"
        else:
            status = "✅ **DOSTĘPNY TERAZ!**"

        embed.add_field(
            name=f"🐉 {champion}",
            value=f"Czas respu: {utc_to_poland(resp_time).strftime('%H:%M:%S')}\n{status}",
            inline=True
        )
    await ctx.send(embed=embed)

@bot.command()
async def set_resp(ctx, champion: str, time_str: str = None):
    champion = champion.strip().lower()
    full_name = champion_aliases.get(champion, champion.title())
    now_poland = datetime.now(POLAND_TZ)

    if time_str:
        try:
            hour, minute = map(int, time_str.split(":"))
            resp_time_poland = now_poland.replace(hour=hour, minute=minute, second=0, microsecond=0)
            resp_time_utc = resp_time_poland.astimezone(pytz.utc).replace(tzinfo=None)
        except:
            await ctx.send("❌ Niepoprawny format godziny! Użyj `HH:MM`.")
            return
    else:
        resp_time_utc = datetime.utcnow()

    schedule = generate_future_resps(full_name, resp_time_utc)
    save_resps(schedule)

    await ctx.send(f"✅ Wygenerowano {FUTURE_RESPS} przyszłych respów dla **{full_name}**!")

# ------------------- URUCHOMIENIE BOTA -------------------
@bot.event
async def on_ready():
    print(f'🤖 {bot.user} jest online!')

bot.run(TOKEN)
