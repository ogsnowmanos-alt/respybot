# Import Flask aplikacji dla Gunicorn
from flask_app import app

# Ten plik jest używany przez Gunicorn do uruchomienia Flask server
# Discord bot uruchamiany jest osobno przez discord_bot.py

if __name__ == "__main__":
    print("Uruchamianie Flask aplikacji...")
    app.run(host="0.0.0.0", port=5000, debug=False)
