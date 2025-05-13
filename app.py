
from flask import Flask, request, jsonify, send_file
import base64
from io import BytesIO
from PIL import Image # Import Image for type hinting, if desired

from config import CANVAS_SIZE, BACKGROUND_COLOR # Import configuration
from emoji_utils import get_relevant_emojis # Import emoji-related utility
from image_processor import generate_icon_from_emojis # Import image processing utility
from flask_cors import CORS

app = Flask(__name__)
# CORS(app, resources={r"/generate-icon":{"origins":"http://localhost:3000"}})
CORS(app)
# Global variable to store the last generated icon for direct viewing endpoint
last_generated_icon = None

@app.route("/view-last-icon")
def view_last_icon():
    """
    Endpoint to view the last generated icon as a PNG image directly in the browser.
    Useful for visual debugging of transparency.
    """
    global last_generated_icon
    if last_generated_icon is None:
        return "No icon has been generated yet. Please call /generate-icon first.", 404
    
    buffered = BytesIO()
    last_generated_icon.save(buffered, format="PNG")
    buffered.seek(0)
    return send_file(buffered, mimetype='image/png')

@app.route("/generate-icon", methods=["POST"])
def generate_icon_from_words_endpoint():
    """
    Main API endpoint to generate a 64x64 icon from input text.
    Returns a JSON object with pixel data (RGBA) and a base64-encoded PNG.
    """
    global last_generated_icon
    data = request.json
    text = data.get("text", "")
    
    if not text:
        return jsonify({"error": "Please provide 'text' in the request body."}), 400

    # Get relevant emojis based on the text
    selected_emojis = get_relevant_emojis(text)

    # Generate the RGBA icon (with transparency)
    icon_rgba = generate_icon_from_emojis(selected_emojis, canvas_size=CANVAS_SIZE, background_color=BACKGROUND_COLOR)
    print(f"DEBUG: (generate_icon_from_words_endpoint) Received icon_rgba object ID: {id(icon_rgba)}")
    if not icon_rgba:
        return jsonify({"error": "Could not generate icon from text."}), 500

    # Central pixel Check (for debugging)
    center_x = icon_rgba.width // 2
    center_y = icon_rgba.height // 2
    center_pixel = icon_rgba.getpixel((center_x, center_y))
    print(f"DEBUG: Pixel at center ({center_x}, {center_y}) from icon_rgba: {center_pixel}")

    # Prepare pixel data for JSON output (RGBA values)
    pixels = []
    for y in range(icon_rgba.height):
        row = []
        for x in range(icon_rgba.width):
            # Get all four RGBA values for each pixel
            r, g, b, a = icon_rgba.getpixel((x, y))
            row.append([r, g, b, a]) # Append RGBA tuple as a list
        pixels.append(row)

    # Prepare base64-encoded PNG for easy client-side display
    buffered = BytesIO()
    icon_rgba.save(buffered, format="PNG") # Save as PNG, preserving transparency
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    # Store the last generated icon for the /view-last-icon debug endpoint
    last_generated_icon = icon_rgba

    return jsonify({
        "icon_array": pixels, # This will now contain RGBA values for each pixel
        "width": icon_rgba.width,
        "height": icon_rgba.height,
        # "base64_image": img_str # This base64 string represents the transparent PNG
    })

if __name__ == "__main__":
    # To use TextBlob, you might need to download its corpora once:
    # python -m textblob.download_corpora
    app.run(debug=True, host='0.0.0.0', port=5000) # Listen on all interfaces and port 5000