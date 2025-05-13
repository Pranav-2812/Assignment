
import io
import os
import requests
from PIL import Image, ImageDraw, ImageFont

from config import TWEMOJI_BASE_URL, DEBUG_DIR_DOWNLOADS, DEBUG_DIR_RESIZED
from emoji_utils import get_emoji_codepoints

def download_twemoji_png(codepoint):
    """
    Downloads a Twemoji PNG image for a given codepoint.
    Returns a PIL Image object in RGBA mode.
    """
    url = TWEMOJI_BASE_URL + codepoint + ".png"
    print(f"Attempting to download Twemoji from: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        img = Image.open(io.BytesIO(response.content)).convert("RGBA")
        print(f"Successfully downloaded Twemoji {codepoint}. Image mode: {img.mode}, size: {img.size}")
        
        # Debug: Save downloaded emoji for inspection
        try:
            img.save(os.path.join(DEBUG_DIR_DOWNLOADS, f"{codepoint}_downloaded.png"))
            print(f"DEBUG: Saved downloaded emoji {codepoint}_downloaded.png for inspection.")
        except Exception as e:
            print(f"ERROR: Could not save downloaded emoji debug image: {e}")
            
        return img
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to download Twemoji {codepoint} from {url}: {e}")
        return None

def generate_icon_from_emojis(selected_emojis, canvas_size=(64, 64), background_color=(255, 255, 255, 0)):
    """
    Generates an icon from a list of emoji characters by downloading their Twemoji assets
    and composing them onto a canvas.
    """
    emoji_string = "".join(selected_emojis)
    codepoints = get_emoji_codepoints(emoji_string)
    
    # Create the canvas with a transparent background
    canvas = Image.new("RGBA", canvas_size, background_color)
    print(f"DEBUG: Initial canvas created. Mode: {canvas.mode}, Size: {canvas.size}, Background: {background_color}")

    # Fallback if no valid emoji codepoints are derived
    if not codepoints:
        draw = ImageDraw.Draw(canvas)
        try:
            font = ImageFont.truetype("arial.ttf", 20) # Try Arial font
        except IOError:
            font = ImageFont.load_default() # Fallback to default Pillow font
        draw.text((5, 5), "No icon", fill=(0, 0, 0), font=font)
        print("DEBUG: No codepoints found, drawing 'No icon' text.")
        return canvas

    num_emojis = len(codepoints)
    
    # Calculate emoji size and positions based on number of emojis
    # Ensuring integer values for positioning
    if num_emojis == 1:
        emoji_size = int(canvas_size[0] * 0.7)
        positions = [(int((canvas_size[0] - emoji_size) / 2), int((canvas_size[1] - emoji_size) / 2))]
    elif num_emojis == 2:
        emoji_size = int(canvas_size[0] * 0.45)
        x_offset = int((canvas_size[0] - emoji_size * 2) / 3)
        y_offset = int((canvas_size[1] - emoji_size) / 2)
        positions = [
            (x_offset, y_offset),
            (2 * x_offset + emoji_size, y_offset)
        ]
    elif num_emojis == 3:
        emoji_size = int(canvas_size[0] * 0.35)
        x_offset = int((canvas_size[0] - emoji_size * 3) / 4)
        y_offset = int((canvas_size[1] - emoji_size) / 2)
        positions = [
            (x_offset, y_offset),
            (2 * x_offset + emoji_size, y_offset),
            (3 * x_offset + 2 * emoji_size, y_offset)
        ]
    elif num_emojis == 4:
        emoji_size = int(canvas_size[0] * 0.4)
        positions = [
            (int(canvas_size[0]/2 - emoji_size), int(canvas_size[1]/2 - emoji_size)), # Top-left
            (int(canvas_size[0]/2), int(canvas_size[1]/2 - emoji_size)),           # Top-right
            (int(canvas_size[0]/2 - emoji_size), int(canvas_size[1]/2)),           # Bottom-left
            (int(canvas_size[0]/2), int(canvas_size[1]/2))                            # Bottom-right
        ]
    else: # Should not be reached due to [:4] limit, but as a fallback
        emoji_size = int(canvas_size[0] * 0.3)
        positions = []
        for r in range(2):
            for c in range(2):
                positions.append((c * emoji_size + 5, r * emoji_size + 5))

    # Place emojis on the canvas
    for i, cp in enumerate(codepoints[:num_emojis]):
        emoji_img = download_twemoji_png(cp)
        if emoji_img and i < len(positions):
            emoji_img = emoji_img.resize((emoji_size, emoji_size), Image.Resampling.LANCZOS)
            
            # Debug: Save resized emoji for inspection
            try:
                emoji_img.save(os.path.join(DEBUG_DIR_RESIZED, f"{cp}_resized_to_{emoji_img.width}x{emoji_img.height}.png"))
                print(f"DEBUG: Saved resized emoji {cp}_resized_to_{emoji_img.width}x{emoji_img.height}.png.")
            except Exception as e:
                print(f"ERROR: Could not save resized emoji debug image: {e}")

            paste_x, paste_y = positions[i]
            
            # Verify paste will be within bounds
            if paste_x >= 0 and paste_y >= 0 and \
               paste_x + emoji_img.width <= canvas_size[0] and \
               paste_y + emoji_img.height <= canvas_size[1]:
                canvas.paste(emoji_img, positions[i], emoji_img) # Use emoji_img as mask for transparency
                print(f"DEBUG: Pasted emoji {cp} at position {positions[i]}")
            else:
                print(f"WARNING: Position {positions[i]} out of bounds for emoji {cp} (resized to {emoji_img.size}). Skipping paste.")
        elif not emoji_img:
            print(f"WARNING: Emoji image for {cp} was None (download failed). Skipping paste.")
        else: # i >= len(positions) - should ideally not happen if num_emojis cap is correct
            print(f"WARNING: No defined position for emoji {cp} at index {i}. Skipping paste.")
    
    # Debug: Save final RGBA canvas before returning
    try:
        canvas.save("debug_final_rgba_canvas.png")
        print("DEBUG: Saved debug_final_rgba_canvas.png (final RGBA canvas). Check this file.")
    except Exception as e:
        print(f"ERROR: Could not save debug_final_rgba_canvas.png: {e}")

    return canvas.copy()