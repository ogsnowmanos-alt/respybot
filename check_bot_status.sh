#!/bin/bash

echo "🔍 Sprawdzanie statusu Discord bota..."
echo "Serwer Discord: 1394086742436614316"
echo "Kanał pingów: 1394086743061299349"
echo ""

# Sprawdź procesy
PROCESSES=$(ps aux | grep -E "(run_discord_bot|discord_bot)" | grep -v grep)

if [ -z "$PROCESSES" ]; then
    echo "❌ Bot nie działa"
    echo ""
    echo "🚀 Uruchamiam bota ponownie..."
    ./run_discord_bot.sh > discord_bot_persistent.log 2>&1 &
    sleep 3
    echo "✅ Bot uruchomiony"
else
    echo "✅ Bot działa:"
    echo "$PROCESSES"
fi

echo ""
echo "📝 Ostatnie logi:"
tail -n 3 discord_bot_persistent.log 2>/dev/null || echo "Brak logów"