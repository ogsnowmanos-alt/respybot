from flask import Flask

# Flask aplikacja dla Gunicorn
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <h1>Bot do trackowania respów czempionów działa!</h1>
    <h2>Dostępne komendy Discord:</h2>
    <ul>
        <li><code>!resp</code> - pokazuje kiedy respią się czempioni</li>
        <li><code>!set_resp [nazwa_czempiona]</code> - ustawia czas respu na teraz</li>
        <li><code>!del_resp [nazwa_czempiona]</code> - usuwa czempiona z listy</li>
        <li><code>!pomoc</code> - pomoc</li>
    </ul>
    <p>Bot automatycznie pinguje @everyone 30 minut przed respem czempiona!</p>
    <p><strong>Status Discord bota:</strong> Sprawdź w konsoli czy bot się połączył</p>
    """

@app.route('/status')
def status():
    return {
        "flask": "running",
        "discord_bot": "check console logs",
        "commands": ["!resp", "!set_resp", "!del_resp", "!pomoc"]
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)