import os
from typing import Final

# Bot Configuration
BOT_TOKEN: Final[str] = os.getenv("DISCORD_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
COMMAND_PREFIX: Final[str] = "/"

# Game Configuration
MAX_PLAYERS: Final[int] = 20
TURN_TIMEOUT: Final[int] = 300  # 5 minutes in seconds

# Emoji Configuration
EMOJIS = {
    "truth": "🧠",
    "dare": "🎯", 
    "punishment": "⚠️",
    "success": "✅",
    "error": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "game": "🎮",
    "queue": "📥",
    "next": "🔁",
    "refuse": "❌",
    "ping": "📡",
    "stop": "🛑",
    "random": "🎲"
}

# Colors for embeds
COLORS = {
    "success": 0x00ff00,
    "error": 0xff0000,
    "warning": 0xffff00,
    "info": 0x0099ff,
    "game": 0x9932cc
}
