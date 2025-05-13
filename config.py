
import os

# Base URL for Twemoji assets (72x72 PNGs)
TWEMOJI_BASE_URL = "https://cdn.jsdelivr.net/gh/twitter/twemoji/assets/72x72/"

# Debug directories
DEBUG_DIR_DOWNLOADS = "debug_emoji_downloads"
DEBUG_DIR_RESIZED = "debug_resized_emojis"

# Ensure debug directories exist (can be moved to a setup function in app.py if preferred)
os.makedirs(DEBUG_DIR_DOWNLOADS, exist_ok=True)
os.makedirs(DEBUG_DIR_RESIZED, exist_ok=True)

# Image generation settings
CANVAS_SIZE = (64, 64)
BACKGROUND_COLOR = (255, 255, 255, 0) # Transparent background