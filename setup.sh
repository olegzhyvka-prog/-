#!/bin/bash
# Setup script — run once on your local machine

echo "=== AI Agent Setup ==="

# 1. Install Python dependencies
pip install anthropic ddgs httpx "beautifulsoup4[lxml]" markdownify playwright

# 2. Install Chromium for browser-use (optional but needed for browser tasks)
python3 -m playwright install chromium

# 3. Install browser-use
pip install browser-use

echo ""
echo "=== Done! ==="
echo ""
echo "Now set your API key:"
echo "  export ANTHROPIC_API_KEY=sk-ant-..."
echo ""
echo "Then run:"
echo "  python3 agent.py \"your task here\""
