import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import os
import pytz

# ------------------- KONFIGURACJA -------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = 1394086742436614316  # ID serwera Discord
CHANNEL_ID = 1394086743061299349  # ID kanału do pingowania respów
RESP_TIME = timedelta(hours=5, minutes=30)  # Czas między respami czempionów

# Polska strefa czasowa
POLAND_TZ = pytz.timezone("Europe/Warsaw")

# ------------------- DISCORD BOT -------------------
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------- ZMIENNE -------------------
resp_times = {}

# Mapowanie skrótów na pełne nazwy
champion_aliases = {
    "kowal": "Kowal Lugusa",
    "straz": "Straż Lugusa"
}

# Rotacja czempionów Lugusa
lugus_rotation = {
    "Kowal Lugusa": "Straż Lugusa",
    "Straż Lugusa": "Kowal Lugusa"
}

# ------------------- FUNKCJE -------------------
def next_resp(last_resp):
    return last_resp + RESP_TIME

def to_polish_time(dt_utc):
    """Konwertuje datetime UTC na czas polski"""
    return dt_utc.replace(tzinfo=pytz.utc).astimezone(POLAND_TZ)

async def ping_resp(champion, channel):
    await channel.send(f"🔔 @everyone **{champion}** resp w lochu za 30 minut! 🔔")

# ------------------- TASK SPRAWDZAJĄCY RESP -------------------
@tasks.loop(minutes=1)
async def check_resp():
    now = datetime.utcnow()
    for champion, last_resp in resp_times.copy().items():
        next_resp_time = last_resp + RESP_TIME
        remaining_seconds = (next_resp_time - now).total_seconds()
        
        if 0 < remaining_seconds <= 1800:  # 30 minut
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

# ------------------- WYDARZENIA -------------------
@bot.event
async def on_ready():
    print(f'🤖 {bot.user} jest online!')
    guild = bot.get_guild(GUILD_ID)
    if guild:
        print(f'✅ Połączony z serwerem: {guild.name}')
        channel = guild.get_channel(CHANNEL_ID)
        if channel:
            print(f'✅ Dostęp do kanału: {channel.name}')
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
        
        last_resp_pl = to_polish_time(last_resp)
        embed.add_field(
            name=f"🐉 {champion}",
            value=f"Ostatni resp: {last_resp_pl.strftime('%H:%M:%S')} (czas polski)\n{status}",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def set_resp(ctx, *, args: str):
    """
    Ustawia resp czempiona.
    Można podać czas w formacie HH:MM lub 'teraz'.
    Przykład: !set_resp kowal 14:30
    """
    parts = args.split()
    champion_input = parts[0].lower()
    
    if champion_input in champion_aliases:
        champion = champion_aliases[champion_input]
    else:
        champion = champion_input.title()
    
    # Obsługa czasu
    if len(parts) > 1:
        try:
            input_time = parts[1]
            if input_time.lower() == "teraz":
                dt = datetime.utcnow()
            else:
                dt_polish = datetime.strptime(input_time, "%H:%M")
                now_polish = datetime.now(POLAND_TZ)
                dt_polish = POLAND_TZ.localize(datetime(
                    year=now_polish.year,
                    month=now_polish.month,
                    day=now_polish.day,
                    hour=dt_polish.hour,
                    minute=dt_polish.minute
                ))
                dt = dt_polish.astimezone(pytz.utc)
        except:
            await ctx.send("❌ Niepoprawny format czasu! Użyj HH:MM lub 'teraz'.")
            return
    else:
        dt = datetime.utcnow()
    
    resp_times[champion] = dt
    await ctx.send(f"✅ Resp **{champion}** ustawiony na {to_polish_time(dt).strftime('%H:%M')} (czas polski)")

@bot.command()
async def del_resp(ctx, *, champion: str):
    champion = champion.strip().lower()
    if champion in champion_aliases:
        full_name = champion_aliases[champion]
    else:
        full_name = champion.title()
    
    if full_name in resp_times:
        del resp_times[full_name]
        await ctx.send(f"🗑️ Resp **{full_name}** został usunięty z listy respów")
    else:
        await ctx.send(f"❌ Nie znaleziono czempiona **{full_name}** na liście")

@bot.command(name="ping")
async def ping_command(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Opóźnienie: {latency}ms")

@bot.command(name='pomoc')
async def pomoc(ctx):
    embed = discord.Embed(
        title="🤖 Pomoc - Bot respów czempionów",
        description="Bot automatycznie śledzi czasy respów czempionów i pinguje 30 minut przed ich powrotem!",
        color=0x0099ff
    )
    embed.add_field(name="📋 !resp", value="Pokazuje listę wszystkich czempionów i ich czasy respów", inline=False)
    embed.add_field(name="🏓 !ping", value="Wyświetla opóźnienie bota do Discord", inline=False)
    embed.add_field(name="➕ !set_resp [nazwa] [HH:MM/teraz]", value="Dodaje czempiona i ustawia jego czas respu", inline=False)
    embed.add_field(name="🗑️ !del_resp [nazwa]", value="Usuwa czempiona z listy respów", inline=False)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Brakuje argumentu! Użyj `!pomoc` aby zobaczyć jak używać komend.")
    elif isinstance(error, commands.CommandNotFound):
        return
    else:
        print(f"Błąd komendy: {error}")
        await ctx.send("❌ Wystąpił błąd podczas wykonywania komendy.")

# ------------------- URUCHOMIENIE -------------------
async def main():
    if not TOKEN:
        print("❌ Nie znaleziono tokenu Discord bota!")
        return
    try:
        print("🚀 Uruchamianie Discord bota...")
        await bot.start(TOKEN)
    except discord.LoginFailure:
        print("❌ Nieprawidłowy token Discord bota!")
    except KeyboardInterrupt:
        print("🔄 Bot zatrzymany przez użytkownika")
    except Exception as e:
        print(f"❌ BŁĄD: {e}")

def run_bot():
    asyncio.run(main())

if __name__ == "__main__":
    run_bot()
