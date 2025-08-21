import discord
from discord.ext import commands, tasks
from flask import Flask
import asyncio
from datetime import datetime, timedelta
import threading
import os

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot działa!"

@bot.event
async def on_ready():
    print(f'{bot.user} jest online!')

@bot.command(name='ping')
async def ping(ctx):
    """Sprawdza ping bota"""
    latency = round(bot.latency * 1000)
    await ctx.send(f'Pong! {latency}ms')

@bot.command(name='czas')
async def czas(ctx):
    """Pokazuje aktualny czas"""
    teraz = datetime.now()
    await ctx.send(f'Aktualny czas: {teraz.strftime("%H:%M:%S %d.%m.%Y")}')

@bot.command(name='info')
async def info(ctx):
    """Informacje o bocie"""
    embed = discord.Embed(
        title="Informacje o bocie",
        description="Discord bot z Flask backend",
        color=0x00ff00
    )
    embed.add_field(name="Serwery", value=len(bot.guilds), inline=True)
    embed.add_field(name="Użytkownicy", value=len(bot.users), inline=True)
    embed.add_field(name="Ping", value=f"{round(bot.latency * 1000)}ms", inline=True)
    await ctx.send(embed=embed)

# Przykład timera
@tasks.loop(minutes=30)
async def okresowa_wiadomosc():
    """Wysyła wiadomość co 30 minut"""
    print("Timer działa - bot jest aktywny")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    # Odpowiedz na "cześć"
    if message.content.lower() in ['cześć', 'czesc', 'hej', 'witaj']:
        await message.channel.send(f'Cześć {message.author.mention}!')
    
    await bot.process_commands(message)

# Uruchom bota
async def main():
    if not TOKEN:
        print("BŁĄD: Nie znaleziono tokenu Discord bota!")
        print("Ustaw zmienną środowiskową DISCORD_BOT_TOKEN")
        return
    
    async with bot:
        # Uruchom timer
        okresowa_wiadomosc.start()
        await bot.start(TOKEN)

# Flask uruchamia się w osobnym wątku
if __name__ == "__main__":
    # Uruchom Flask w osobnym wątku
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=False))
    flask_thread.daemon = True
    flask_thread.start()
    
    print("Flask server uruchomiony na porcie 5000")
    print("Uruchamianie Discord bota...")
    
    # Uruchom Discord bota
    asyncio.run(main())
