import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import os

# ------------------- KONFIGURACJA -------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# Ustaw te wartości dla swojego serwera i kanału:
GUILD_ID = None  # Wklej ID serwera (opcjonalne)
CHANNEL_ID = None  # Wklej ID kanału, gdzie bot będzie pingował (opcjonalne - użyje aktualnego kanału)

RESP_TIME = timedelta(hours=5, minutes=30)  # Czas między respami czempionów

# ------------------- DISCORD BOT -------------------
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------- ZMIENNE -------------------
# Przechowuje czasy respów w formacie {czempion: datetime}
resp_times = {}

# ------------------- FUNKCJE -------------------
def next_resp(last_resp):
    return last_resp + RESP_TIME

async def ping_resp(champion, channel):
    await channel.send(f"🔔 @everyone **{champion}** resp w lochu za 30 minut! 🔔")

# ------------------- TASK SPRAWDZAJĄCY RESP -------------------
@tasks.loop(minutes=1)
async def check_resp():
    now = datetime.utcnow()
    for champion, last_resp in resp_times.copy().items():
        next_resp_time = last_resp + RESP_TIME
        remaining_seconds = (next_resp_time - now).total_seconds()
        
        # Jeśli zostało 30 minut lub mniej do respu
        if 0 < remaining_seconds <= 1800:  # 30 minut = 1800 sekund
            # Znajdź kanał do pingowania
            channel = None
            if CHANNEL_ID:
                channel = bot.get_channel(CHANNEL_ID)
            else:
                # Jeśli nie ma ustawionego kanału, użyj pierwszego dostępnego kanału tekstowego
                for guild in bot.guilds:
                    for ch in guild.text_channels:
                        if ch.permissions_for(guild.me).send_messages:
                            channel = ch
                            break
                    if channel:
                        break
            
            if channel:
                await ping_resp(champion, channel)
            
            # Ustaw następny czas respu
            resp_times[champion] = next_resp_time

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} jest online!')
    print(f'📊 Bot jest na {len(bot.guilds)} serwerach')
    
    # Uruchom sprawdzanie respów
    if not check_resp.is_running():
        check_resp.start()
        print("⏰ Timer sprawdzania respów uruchomiony!")

# ------------------- KOMENDY -------------------
@bot.command()
async def resp(ctx):
    """Pokazuje kiedy respił się czempion"""
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
            value=f"Ostatni resp: {last_resp.strftime('%H:%M:%S')}\n{status}",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def set_resp(ctx, *, champion: str):
    """Ręcznie ustawia czas resp czempiona na teraz"""
    champion = champion.strip().title()
    resp_times[champion] = datetime.utcnow()
    
    embed = discord.Embed(
        title="✅ Resp zapisany!",
        description=f"**{champion}** - czas respu ustawiony na teraz",
        color=0x00ff00
    )
    embed.add_field(
        name="Następny resp za:",
        value=f"{RESP_TIME.total_seconds() / 3600:.1f} godzin",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command()
async def del_resp(ctx, *, champion: str):
    """Usuwa zapisany czas respu czempiona"""
    champion = champion.strip().title()
    
    if champion in resp_times:
        del resp_times[champion]
        embed = discord.Embed(
            title="🗑️ Resp usunięty",
            description=f"**{champion}** został usunięty z listy respów",
            color=0xff6b6b
        )
    else:
        embed = discord.Embed(
            title="❌ Nie znaleziono",
            description=f"Nie znaleziono czempiona **{champion}** na liście",
            color=0xff6b6b
        )
    
    await ctx.send(embed=embed)

@bot.command(name='pomoc')
async def pomoc(ctx):
    """Pokazuje pomoc dla komend bota"""
    embed = discord.Embed(
        title="🤖 Pomoc - Bot respów czempionów",
        description="Bot automatycznie śledzi czasy respów czempionów i pinguje 5 minut przed ich powrotem!",
        color=0x0099ff
    )
    
    embed.add_field(
        name="📋 !resp",
        value="Pokazuje listę wszystkich czempionów i ich czasy respów",
        inline=False
    )
    
    embed.add_field(
        name="➕ !set_resp [nazwa]",
        value="Dodaje czempiona i ustawia jego czas respu na teraz\nPrzykład: `!set_resp Smok Lodowy`",
        inline=False
    )
    
    embed.add_field(
        name="🗑️ !del_resp [nazwa]",
        value="Usuwa czempiona z listy respów\nPrzykład: `!del_resp Smok Lodowy`",
        inline=False
    )
    
    embed.add_field(
        name="ℹ️ Informacje",
        value=f"• Czas między respami: **{RESP_TIME.total_seconds() / 3600:.1f} godzin**\n• Bot pinguje @everyone 30 minut przed respem\n• Wszystkie czasy w UTC",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Obsługa błędów komend"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Brakuje argumentu! Użyj `!pomoc` aby zobaczyć jak używać komend.")
    elif isinstance(error, commands.CommandNotFound):
        return  # Ignoruj nieznane komendy
    else:
        print(f"Błąd komendy: {error}")
        await ctx.send("❌ Wystąpił błąd podczas wykonywania komendy.")

# ------------------- URUCHOMIENIE -------------------
async def main():
    if not TOKEN:
        print("❌ BŁĄD: Nie znaleziono tokenu Discord bota!")
        print("📝 Ustaw zmienną środowiskową DISCORD_BOT_TOKEN")
        return
    
    try:
        print("🚀 Uruchamianie Discord bota...")
        async with bot:
            await bot.start(TOKEN)
    except discord.LoginFailure:
        print("❌ BŁĄD: Nieprawidłowy token Discord bota!")
    except Exception as e:
        print(f"❌ BŁĄD: {e}")

if __name__ == "__main__":
    asyncio.run(main())