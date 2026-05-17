#!/bin/bash
# Запусти це один раз на своєму комп'ютері

echo "=== Встановлення залежностей ==="
pip install playwright anthropic ddgs httpx beautifulsoup4 markdownify lxml

echo ""
echo "=== Встановлення браузера Chromium ==="
python3 -m playwright install chromium

echo ""
echo "=== Готово! ==="
echo ""
echo "Використання:"
echo ""
echo "  # Знайти монітор і відкрити сторінку товару:"
echo "  python3 rozetka_browser_agent.py 'монітор 27 дюймів' --max-price 30000"
echo ""
echo "  # Знайти і ДОДАТИ В КОШИК (потрібен вхід):"
echo "  python3 rozetka_browser_agent.py 'монітор 27 дюймів' --max-price 30000 --add-to-cart"
echo ""
echo "  # Загальний AI-агент з пошуком в інтернеті:"
echo "  export ANTHROPIC_API_KEY=sk-ant-..."
echo "  python3 agent.py 'твоє завдання'"
