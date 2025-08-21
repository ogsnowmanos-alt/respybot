#!/bin/bash

# Skrypt uruchamiający Discord bota w trybie ciągłym
echo "🚀 Uruchamianie Discord bota w trybie ciągłym..."

while true; do
    echo "$(date): Startowanie Discord bota..."
    python discord_bot.py
    echo "$(date): Bot się zatrzymał. Restartowanie za 5 sekund..."
    sleep 5
done