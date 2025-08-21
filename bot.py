import os
import logging
import asyncio
import discord
from discord.ext import commands

# Configure logging
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variable to track bot status
bot_status = {
    'connected': False,
    'guilds': 0,
    'latency': 0,
    'user': None
}

@bot.event
async def on_ready():
    """Event triggered when bot is ready"""
    global bot_status
    logger.info(f'{bot.user} has connected to Discord!')
    bot_status['connected'] = True
    bot_status['guilds'] = len(bot.guilds)
    bot_status['user'] = str(bot.user)
    
    try:
        # Sync slash commands
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

@bot.event
async def on_disconnect():
    """Event triggered when bot disconnects"""
    global bot_status
    logger.warning("Bot disconnected from Discord")
    bot_status['connected'] = False

@bot.event
async def on_guild_join(guild):
    """Event triggered when bot joins a guild"""
    global bot_status
    logger.info(f"Joined guild: {guild.name}")
    bot_status['guilds'] = len(bot.guilds)

@bot.event
async def on_guild_remove(guild):
    """Event triggered when bot leaves a guild"""
    global bot_status
    logger.info(f"Left guild: {guild.name}")
    bot_status['guilds'] = len(bot.guilds)

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Ping command to check bot latency"""
    try:
        latency = round(bot.latency * 1000)
        global bot_status
        bot_status['latency'] = latency
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
        logger.info(f"Ping command used by {interaction.user} - Latency: {latency}ms")
    except Exception as e:
        logger.error(f"Error in ping command: {e}")
        await interaction.response.send_message("❌ An error occurred while checking latency.", ephemeral=True)

@bot.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    """Help command to show available commands"""
    try:
        embed = discord.Embed(
            title="🤖 Bot Commands",
            description="Here are the available commands:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="/ping",
            value="Check bot latency",
            inline=False
        )
        
        embed.add_field(
            name="/help",
            value="Show this help message",
            inline=False
        )
        
        embed.set_footer(text="Bot is running alongside Flask web server")
        
        await interaction.response.send_message(embed=embed)
        logger.info(f"Help command used by {interaction.user}")
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await interaction.response.send_message("❌ An error occurred while showing help.", ephemeral=True)

@bot.event
async def on_message(message):
    """Event triggered when a message is sent"""
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Log message for debugging (be careful with privacy in production)
    logger.debug(f"Message from {message.author} in {message.guild}: {message.content[:50]}...")
    
    # Process commands
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands"""
    logger.error(f"Command error: {error}")
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore command not found errors
    
    await ctx.send("❌ An error occurred while processing the command.")

def get_bot_status():
    """Get current bot status for web interface"""
    global bot_status
    if bot.is_ready():
        bot_status['latency'] = round(bot.latency * 1000) if bot.latency else 0
        bot_status['guilds'] = len(bot.guilds)
    return bot_status

def run_discord_bot():
    """Run the Discord bot"""
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set!")
        raise ValueError("Discord bot token is required")
    
    try:
        logger.info("Starting Discord bot...")
        bot.run(token, log_handler=None)  # Disable discord.py's default logging
    except discord.LoginFailure:
        logger.error("Invalid Discord bot token")
        raise
    except Exception as e:
        logger.error(f"Error running Discord bot: {e}")
        raise
