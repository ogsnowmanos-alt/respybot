# Discord Bot - Respy Czempionów

## Konfiguracja Workflow

Bot Discord został skonfigurowany do działania w workflow Replit z automatycznym monitoringiem i restartami.

### Komponenty:
- `discord_bot.py` - Główny kod bota
- `discord_bot_workflow.py` - Wersja workflow z obsługą błędów  
- `start_discord_bot.py` - Starter dla workflow
- `monitor_discord_bot.py` - Monitor i auto-restart
- `check_bot_status.sh` - Sprawdzanie statusu

### Konfiguracja serwera:
- **Serwer Discord:** 1394086742436614316 (Jazda Bez Trzymanki)
- **Kanał respów:** 1394086743061299349 (🕓┃respy-loch)

### Uruchamianie:

**Automatyczne (workflow):**
```bash
./check_bot_status.sh        # Sprawdź status
python monitor_discord_bot.py &  # Monitor z auto-restartem
```

**Ręczne:**
```bash
python discord_bot.py
```

### Komendy bota:
- `!ping` - Sprawdź opóźnienie bota
- `!pomoc` - Lista wszystkich komend
- `!resp` - Pokaż aktywne respy
- `!set_resp kowal` - Ustaw Kowala Lugusa
- `!set_resp straz` - Ustaw Straż Lugusa
- `!del_resp [nazwa]` - Usuń czempiona

### System rotacji Lugusa:
- Po śmierci **Kowala** → automatycznie ustawia **Straż**
- Po śmierci **Straży** → automatycznie ustawia **Kowala**
- Ping @everyone 30 minut przed respem (po 5h od śmierci)

### Status workflow:
- Bot działa w workflow z automatycznym monitoringiem
- System restart przy problemach
- Logi w `discord_workflow.log`