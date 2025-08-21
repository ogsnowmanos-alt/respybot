#!/usr/bin/env python3
"""
Discord Bot Workflow Runner
Uruchamia Discord bota w trybie workflow z obsługą błędów i restartów
"""

import asyncio
import os
import signal
import sys
from datetime import datetime
import logging

# Importy Discord bota
import discord
from discord.ext import commands, tasks
from datetime import timedelta

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('discord_bot_workflow.log')
    ]
)
logger = logging.getLogger('discord_bot_workflow')

# ------------------- KONFIGURACJA -------------------
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = 1394086742436614316  # ID serwera Discord
CHANNEL_ID = 1394086743061299349  # ID kanału do pingowania respów
RESP_TIME = timedelta(hours=5, minutes=30)  # Czas między respami czempionów

# ------------------- DISCORD BOT -------------------
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------- ZMIENNE -------------------
resp_times = {}

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
            channel = bot.get_channel(CHANNEL_ID)
            
            if channel:
                await ping_resp(champion, channel)
            
            # Jeśli to czempion Lugusa, ustaw rotację na następnego
            if champion in lugus_rotation:
                next_champion = lugus_rotation[champion]
                resp_times[next_champion] = next_resp_time
                # Usuń poprzedniego czempiona
                if champion in resp_times:
                    del resp_times[champion]
            else:
                # Dla innych czempionów - normalny resp
                resp_times[champion] = next_resp_time

@bot.event
async def on_ready():
    logger.info(f'🤖 {bot.user} jest online!')
    logger.info(f'📊 Bot jest na {len(bot.guilds)} serwerach')
    
    # Sprawdź czy bot ma dostęp do konkretnego serwera i kanału
    guild = bot.get_guild(GUILD_ID)
    if guild:
        logger.info(f'✅ Połączony z serwerem: {guild.name}')
        channel = guild.get_channel(CHANNEL_ID)
        if channel:
            logger.info(f'✅ Dostęp do kanału: {channel.name}')
            permissions = channel.permissions_for(guild.me)
            logger.info(f'📋 Uprawnienia: read_messages={permissions.read_messages}, send_messages={permissions.send_messages}')
        else:
            logger.error(f'❌ Brak dostępu do kanału o ID: {CHANNEL_ID}')
    else:
        logger.error(f'❌ Brak dostępu do serwera o ID: {GUILD_ID}')
    
    # Uruchom sprawdzanie respów
    if not check_resp.is_running():
        check_resp.start()
        logger.info("⏰ Timer sprawdzania respów uruchomiony!")

@bot.event
async def on_message(message):
    # Debug - loguj otrzymane wiadomości zaczynające się od !
    if message.content.startswith('!') and not message.author.bot:
        logger.info(f'📨 Odebrano komendę: {message.content} od {message.author}')
    
    # Ważne: pozwól botowi przetwarzać komendy
    await bot.process_commands(message)

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
    champion = champion.strip().lower()
    
    # Sprawdź czy to skrót
    if champion in champion_aliases:
        full_name = champion_aliases[champion]
        short_name = champion
    else:
        full_name = champion.title()
        short_name = champion
    
    now = datetime.utcnow()
    resp_times[full_name] = now
    
    embed = discord.Embed(
        title="✅ Resp ustawiony",
        description=f"**{full_name}** - resp ustawiony na teraz",
        color=0x00ff00
    )
    
    next_resp_time = next_resp(now)
    embed.add_field(
        name="⏰ Następny resp",
        value=f"{next_resp_time.strftime('%H:%M:%S')} UTC",
        inline=True
    )
    
    # Jeśli to Lugus, wyjaśnij rotację
    if full_name in lugus_rotation:
        next_champion = lugus_rotation[full_name]
        embed.add_field(
            name="🔄 Po tym respie",
            value=f"Automatycznie ustawiony: **{next_champion}**",
            inline=True
        )
    
    await ctx.send(embed=embed)

@bot.command()
async def del_resp(ctx, *, champion: str):
    """Usuwa czempiona z listy respów"""
    champion = champion.strip().lower()
    
    # Sprawdź czy to skrót
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
    latency = round(bot.latency * 1000)  # Konwersja na milisekundy
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
        value="Pokazuje listę wszystkich czempionów i ich czasy respów",
        inline=False
    )
    
    embed.add_field(
        name="🏓 !ping",
        value="Wyświetla opóźnienie bota do Discord",
        inline=False
    )
    
    embed.add_field(
        name="➕ !set_resp [nazwa]",
        value="Dodaje czempiona i ustawia jego czas respu na teraz\nPrzykłady: `!set_resp kowal`, `!set_resp straz`, `!set_resp Smok Lodowy`",
        inline=False
    )
    
    embed.add_field(
        name="🗑️ !del_resp [nazwa]",
        value="Usuwa czempiona z listy respów\nPrzykład: `!del_resp Smok Lodowy`",
        inline=False
    )
    
    embed.add_field(
        name="🔄 Specjalne skróty Lugusa:",
        value="• `kowal` → Kowal Lugusa\n• `straz` → Straż Lugusa\n• Po Kowalu automatycznie respi Straż\n• Po Straży automatycznie respi Kowal",
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
        logger.error(f"Błąd komendy: {error}")
        await ctx.send("❌ Wystąpił błąd podczas wykonywania komendy.")

# ------------------- WORKFLOW RUNNER -------------------
class DiscordBotWorkflow:
    def __init__(self):
        self.running = False
        self.restart_count = 0
        
    async def run_with_restart(self):
        """Uruchom bota z automatycznym restartem"""
        while True:
            try:
                if not TOKEN:
                    logger.error("❌ Brak tokenu Discord!")
                    break
                logger.info("🚀 Uruchamianie Discord bota w workflow...")
                self.running = True
                await bot.start(TOKEN)
            except discord.LoginFailure:
                logger.error("❌ BŁĄD: Nieprawidłowy token Discord bota!")
                break
            except KeyboardInterrupt:
                logger.info("🔄 Bot zatrzymany przez użytkownika")
                break
            except Exception as e:
                self.restart_count += 1
                logger.error(f"❌ BŁĄD ({self.restart_count}): {e}")
                
                if self.restart_count > 10:
                    logger.error("🛑 Zbyt wiele restartów - zatrzymuję bota")
                    break
                
                logger.info(f"🔄 Restart za 5 sekund... (próba {self.restart_count})")
                await asyncio.sleep(5)
                
                # Reset bota dla kolejnej próby
                if not bot.is_closed():
                    await bot.close()
    
    def stop(self):
        """Zatrzymaj workflow"""
        self.running = False
        logger.info("🛑 Zatrzymywanie Discord bota workflow...")

# ------------------- MAIN -------------------
async def main():
    if not TOKEN:
        logger.error("❌ BŁĄD: Nie znaleziono tokenu Discord bota!")
        logger.error("📝 Ustaw zmienną środowiskową DISCORD_BOT_TOKEN")
        return
    
    workflow = DiscordBotWorkflow()
    
    # Obsługa sygnałów dla graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"🔄 Otrzymano sygnał {signum}")
        workflow.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await workflow.run_with_restart()
    except KeyboardInterrupt:
        logger.info("🔄 Bot zatrzymany")
    finally:
        if not bot.is_closed():
            await bot.close()
        logger.info("👋 Discord bot workflow zakończony")

if __name__ == "__main__":
    asyncio.run(main())