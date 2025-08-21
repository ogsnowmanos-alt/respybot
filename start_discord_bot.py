#!/usr/bin/env python3
"""
Starter script for Discord bot - designed to work with Replit workflow
"""
import os
import sys

# Dodaj ścieżkę do PYTHONPATH
sys.path.insert(0, '/home/runner/workspace')

# Uruchom główny Discord bot
if __name__ == "__main__":
    import discord_bot_workflow
    import asyncio
    
    asyncio.run(discord_bot_workflow.main())