from flask import Flask, request, jsonify
import emoji
from PIL import Image
import numpy as np
import io
import base64

app = Flask(__name__)

def get_emojis_from_text(text):
    """Converts words into emojis using the emoji library."""
    words = text.split()
    emoji_list = []
    for word in words:
        # Convert word into emoji
        emoji_version = emoji.emojize(f":{word}:")
        emoji_list.append(emoji_version)
    return emoji_list

def emoji_to_64x64_array(emoji_char):
    """Converts an emoji character into a 64x64 array"""
    try:
        # Convert emoji to image
        emoji_image = Image.new('RGB', (64, 64), color = (255, 255, 255))  # Placeholder blank image
        # Normally, we would render an emoji image here; for now, using the placeholder
        # This is just a placeholder step; you can use an actual emoji rendering method
        
        # For demonstration, we'll just draw the emoji on the image
        image = Image.new("RGB", (64, 64), (255, 255, 255))  # Placeholder blank white image
        image = image.resize((64, 64))  # Resize to 64x64 pixels
        
        # Convert image to numpy array
        image_array = np.array(image)
        return image_array
    except Exception as e:
        raise RuntimeError(f"Error while converting emoji to image: {str(e)}")

@app.route('/generate-icon', methods=['POST'])
def generate_icon():
    """API endpoint to generate emojis and return a 64x64 array"""
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.get_json()
    input_text = data.get('text', '').strip()

    if not input_text:
        return jsonify({'error': 'Input text is required'}), 400

    # Step 1: Convert words to emojis
    emojis = get_emojis_from_text(input_text)
    
    # Step 2: Convert each emoji to a 64x64 image array
    icon_arrays = []
    for emoji_char in emojis:
        icon_array = emoji_to_64x64_array(emoji_char)
        icon_arrays.append(icon_array.tolist())  # Converting numpy array to list for JSON compatibility

    return jsonify({'icons': icon_arrays})

if __name__ == '__main__':
    app.run(port=5000)
