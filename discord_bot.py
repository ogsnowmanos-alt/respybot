import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta, time
import os
import pytz

# ------------------- KONFIGURACJA -------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Ustawienia serwera i kanału:
GUILD_ID = 1394086742436614316  # ID serwera Discord
CHANNEL_ID = 1394086743061299349  # ID kanału do pingowania respów

RESP_TIME = timedelta(hours=5, minutes=30)  # Czas między respami czempionów

# Strefa czasowa Polska
POLAND_TZ = pytz.timezone("Europe/Warsaw")

# ------------------- DISCORD BOT -------------------
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------- ZMIENNE -------------------
# Przechowuje czasy respów w formacie {czempion: datetime}
resp_times = {}

# Mapowanie skrótów na pełne nazwy
champion_aliases = {
    "kowal": "Kowal Lugusa",
    "straz": "Straż Lugusa"
}

# System rotacji czempionów Lugusa
lugus_rotation = {
    "Kowal Lugusa": "Straż Lugusa",
    "Straż Lugusa": "Kowal Lugusa"
}

# ------------------- FUNKCJE -------------------
def next_resp(last_resp):
    return last_resp + RESP_TIME

async def ping_resp(champion, channel):
    await channel.send(f"🔔 @everyone **{champion}** resp w lochu za 30 minut! 🔔")

def utc_to_poland(utc_dt):
    return utc_dt.replace(tzinfo=pytz.utc).astimezone(POLAND_TZ)

# ------------------- TASK SPRAWDZAJĄCY RESP -------------------
@tasks.loop(minutes=1)
async def check_resp():
    now = datetime.utcnow()
    for champion, last_resp in resp_times.copy().items():
        next_resp_time = last_resp + RESP_TIME
        remaining_seconds = (next_resp_time - now).total_seconds()
        
        if 0 < remaining_seconds <= 1800:  # 30 minut = 1800 sekund
            channel = bot.get_channel(CHANNEL_ID)
            if channel:
                await ping_resp(champion, channel)
            
            if champion in lugus_rotation:
                next_champion = lugus_rotation[champion]
                resp_times[next_champion] = next_resp_time
                if champion in resp_times:
                    del resp_times[champion]
            else:
                resp_times[champion] = next_resp_time

# ------------------- EVENTY -------------------
@bot.event
async def on_ready():
    print(f'🤖 {bot.user} jest online!')
    print(f'📊 Bot jest na {len(bot.guilds)} serwerach')
    
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f'✅ Połączony z serwerem: {guild.name}')
        channel = guild.get_channel(CHANNEL_ID)
        if channel:
            print(f'✅ Dostęp do kanału: {channel.name}')
            permissions = channel.permissions_for(guild.me)
            print(f'📋 Uprawnienia: read_messages={permissions.read_messages}, send_messages={permissions.send_messages}')
        else:
            print(f'❌ Brak dostępu do kanału o ID: {CHANNEL_ID}')
    else:
        print(f'❌ Brak dostępu do serwera o ID: {GUILD_ID}')
    
    if not check_resp.is_running():
        check_resp.start()
        print("⏰ Timer sprawdzania respów uruchomiony!")

@bot.event
async def on_message(message):
    if message.content.startswith('!') and not message.author.bot:
        print(f'📨 Odebrano komendę: {message.content} od {message.author}')
    await bot.process_commands(message)

# ------------------- KOMENDY -------------------
@bot.command()
async def resp(ctx):
    """Pokazuje kiedy respił się czempion w czasie polskim"""
    if not resp_times:
        await ctx.send("📋 **Brak zapisanych respów czempionów.**\n\nUżyj `!set_resp [nazwa]` aby dodać czempiona.")
        return
    
    now = datetime.utcnow()
    embed = discord.Embed(title="⏰ Status respów czempionów", color=0x00ff00)
    
    for champion, last_resp in resp_times.items():
        next_resp_time = next_resp(last_resp)
        remaining = next_resp_time - now
        
        if remaining.total_seconds() > 0:
            hours, remainder = divmod(int(remaining.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours}h {minutes}m {seconds}s"
            status = f"🕐 Za: **{time_str}**"
        else:
            status = "✅ **DOSTĘPNY TERAZ!**"
        
        embed.add_field(
            name=f"🐉 {champion}",
            value=f"Ostatni resp: {utc_to_poland(last_resp).strftime('%H:%M:%S')}\n{status}",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def set_resp(ctx, champion: str, time_str: str = None):
    """Ustawia resp czempiona na konkretną godzinę lub teraz (czas polski)"""
    champion = champion.strip().lower()
    
    if champion in champion_aliases:
        full_name = champion_aliases[champion]
    else:
        full_name = champion.title()
    
    now_poland = datetime.now(POLAND_TZ)
    
    if time_str:
        try:
            hour, minute = map(int, time_str.split(":"))
            resp_time_poland = now_poland.replace(hour=hour, minute=minute, second=0, microsecond=0)
            # Jeśli ustawiona godzina jest w przeszłości, ustaw na dzisiaj lub wczoraj
            if resp_time_poland > now_poland:
                resp_time_utc = resp_time_poland.astimezone(pytz.utc).replace(tzinfo=None)
            else:
                resp_time_utc = resp_time_poland.astimezone(pytz.utc).replace(tzinfo=None)
        except:
            await ctx.send("❌ Niepoprawny format godziny! Użyj `HH:MM`.")
            return
    else:
        resp_time_utc = datetime.utcnow()
    
    resp_times[full_name] = resp_time_utc
    
    embed = discord.Embed(
        title="✅ Resp zapisany!",
        description=f"**{full_name}** - czas respu ustawiony",
        color=0x00ff00
    )
    embed.add_field(
        name="Następny resp za:",
        value=f"{RESP_TIME.total_seconds() / 3600:.1f} godzin",
        inline=False
    )
    
    if full_name in lugus_rotation:
        next_champion = lugus_rotation[full_name]
        embed.add_field(
            name="🔄 Rotacja Lugusa:",
            value=f"Po śmierci **{full_name}** → następny resp: **{next_champion}**",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def del_resp(ctx, *, champion: str):
    """Usuwa zapisany czas respu czempiona"""
    champion = champion.strip().lower()
    
    if champion in champion_aliases:
        full_name = champion_aliases[champion]
    else:
        full_name = champion.title()
    
    if full_name in resp_times:
        del resp_times[full_name]
        embed = discord.Embed(
            title="🗑️ Resp usunięty",
            description=f"**{full_name}** został usunięty z listy respów",
            color=0xff6b6b
        )
    else:
        embed = discord.Embed(
            title="❌ Nie znaleziono",
            description=f"Nie znaleziono czempiona **{full_name}** na liście",
            color=0xff6b6b
        )
    
    await ctx.send(embed=embed)

@bot.command(name="ping")
async def ping_command(ctx):
    """Wyświetla ping bota"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Ping Bota",
        description=f"**Opóźnienie:** {latency}ms",
        color=0x00ff00 if latency < 100 else 0xff9900 if latency < 300 else 0xff0000
    )
    await ctx.send(embed=embed)

@bot.command(name='pomoc')
async def pomoc(ctx):
    """Pokazuje pomoc dla komend bota"""
    embed = discord.Embed(
        title="🤖 Pomoc - Bot respów czempionów",
        description="Bot automatycznie śledzi czasy respów czempionów i pinguje 30 minut przed ich powrotem!",
        color=0x0099ff
    )
    
    embed.add_field(
        name="📋 !resp",
        value="Pokazuje listę wszystkich czempionów i ich czasy respów w czasie polskim",
        inline=False
    )
    
    embed.add_field(
        name="➕ !set_resp [nazwa] [HH:MM]",
        value="Dodaje czempiona i ustawia jego czas respu.\n"
              "Jeśli godzina nie zostanie podana, ustawia respa na teraz.\n"
              "Przykłady: `!set_resp kowal`, `!set_resp kowal 12:21`",
        inline=False
    )
    
    embed.add_field(
        name="🗑️ !del_resp [nazwa]",
        value="Usuwa czempiona z listy respów",
        inline=False
    )
    
    embed.add_field(
        name="🔄 Specjalne skróty Lugusa",
        value="• `kowal` → Kowal Lugusa\n• `straz` → Straż Lugusa\n"
              "• Po Kowalu automatycznie respi Straż\n• Po Straży automatycznie respi Kowal",
        inline=False
    )
    
    embed.set_footer(text="⏰ Wszystkie czasy wyświetlane są w czasie polskim (CET/CEST)")
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Brakuje argumentu w komendzie!")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Nieznana komenda! Użyj `!pomoc` aby zobaczyć listę komend.")
    else:
        await ctx.send(f"❌ Wystąpił błąd: {error}")

# ------------------- URUCHOMIENIE BOTA -------------------
bot.run(TOKEN)
