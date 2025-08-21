#!/usr/bin/env python3
"""
Monitor Discord Bot Workflow
Monitoruje i restartuje Discord bota w przypadku problemów
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def is_bot_running():
    """Sprawdź czy Discord bot działa"""
    try:
        result = subprocess.run(['pgrep', '-f', 'discord_bot'], capture_output=True, text=True)
        return result.returncode == 0 and result.stdout.strip()
    except:
        return False

def start_bot():
    """Uruchom Discord bota"""
    try:
        print(f"[{datetime.now()}] 🚀 Uruchamianie Discord bota...")
        process = subprocess.Popen(['python', 'start_discord_bot.py'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        return process.pid
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Błąd podczas uruchamiania: {e}")
        return None

def monitor_bot():
    """Monitoruj Discord bota i restartuj w razie potrzeby"""
    restart_count = 0
    max_restarts = 5
    
    print(f"[{datetime.now()}] 📊 Uruchamianie monitora Discord bota...")
    
    while restart_count < max_restarts:
        if not is_bot_running():
            print(f"[{datetime.now()}] ❌ Discord bot nie działa")
            
            # Uruchom ponownie
            pid = start_bot()
            if pid:
                restart_count += 1
                print(f"[{datetime.now()}] ✅ Bot uruchomiony (PID: {pid}, restart #{restart_count})")
            else:
                print(f"[{datetime.now()}] 🛑 Nie udało się uruchomić bota")
                break
        else:
            print(f"[{datetime.now()}] ✅ Discord bot działa")
        
        # Czekaj 30 sekund przed następnym sprawdzeniem
        time.sleep(30)
    
    print(f"[{datetime.now()}] 🛑 Monitor zakończony - osiągnięto limit restartów")

if __name__ == "__main__":
    try:
        monitor_bot()
    except KeyboardInterrupt:
        print(f"[{datetime.now()}] 🔄 Monitor zatrzymany przez użytkownika")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Błąd monitora: {e}")