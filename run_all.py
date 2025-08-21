import asyncio
import threading
from flask_app import app  # Twój Flask z main.py
from discord_bot import run_bot  # Funkcja run_bot z discord_bot.py


# ----------------------- FLASK -----------------------
def start_flask():
    print("🌐 Uruchamianie Flask...")
    # Flask nasłuchuje na porcie 5000 dla UptimeRobot
    app.run(host="0.0.0.0", port=5000, debug=False)


# ----------------------- DISCORD BOT -----------------------
def start_discord_bot():
    print("🤖 Uruchamianie Discord bota...")
    asyncio.run(run_bot())


# ----------------------- URUCHAMIANIE -----------------------
if __name__ == "__main__":
    # Flask w osobnym wątku (daemon, aby zakończył się razem z głównym wątkiem)
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()

    # Discord bota uruchamiamy w głównym wątku
    start_discord_bot()
