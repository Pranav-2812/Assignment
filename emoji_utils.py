
import emoji
import re
from textblob import TextBlob

def get_emoji_codepoints(text):
    """
    Extracts Unicode emoji codepoints from a given string.
    Handles multi-codepoint emojis.
    """
    emojis_in_text = []
    for char in text:
        if emoji.is_emoji(char):
            emojis_in_text.append(char)
    
    codepoints = []
    for e_char in emojis_in_text:
        cp_list = []
        # Handle multi-codepoint emojis (e.g., skin tones, gender variants)
        for char_part in e_char:
            cp_list.append(f"{ord(char_part):x}")
        codepoints.append('-'.join(cp_list))
    return codepoints

def get_relevant_emojis(text):
    """
    Selects relevant emojis from a given text based on keyword mapping and sentiment.
    Returns a list of emoji characters.
    """
    selected_emojis = []

    # Extensive Keyword to Emoji Mapping
    # This dictionary can be further expanded for better relevance.
    word_to_emoji_map = {
        "happy": "😊", "joy": "😁", "sad": "😔", "love": "❤️", "heart": "❤️",
        "food": "🍔", "eat": "🍕", "drink": "☕", "sun": "☀️", "rain": "🌧️",
        "weather": "☁️", "book": "📚", "read": "📖", "music": "🎶", "travel": "✈️",
        "car": "🚗", "tech": "💻", "computer": "💻", "phone": "📱", "idea": "💡",
        "money": "💰", "work": "💼", "time": "⏰", "party": "🎉", "celebrate": "🥳",
        "star": "⭐", "thumbs up": "👍", "ok": "👌", "good": "👍", "bad": "👎",
        "exciting": "🤩", "sleep": "😴", "question": "❓", "answer": "✅", "warning": "⚠️",
        "danger": "🚨", "home": "🏠", "building": "🏢", "flower": "🌸", "tree": "🌳",
        "animal": "🐾", "dog": "🐶", "cat": "🐱", "fish": "🐠", "game": "🎮",
        "sport": "⚽", "run": "🏃", "walk": "🚶", "study": "📚", "write": "✍️",
        "art": "🎨", "movie": "🎬", "film": "🎞️", "camera": "📸", "picture": "🖼️",
        "fire": "🔥", "water": "💧", "earth": "🌍", "world": "🌎", "space": "🚀",
        "rocket": "🚀", "science": "🔬", "chemistry": "🧪", "math": "➕", "school": "🏫",
        "hospital": "🏥", "doctor": "👩‍⚕️", "nurse": "👨‍⚕️", "police": "👮", "firefighter": "🧑‍🚒",
        "business": "📈", "chart": "📊", "growth": "📈", "decline": "📉", "delivery": "📦",
        "gift": "🎁", "present": "🎁", "email": "📧", "message": "✉️", "chat": "💬",
        "call": "📞", "phone": "📱", "idea": "💡", "light": "💡", "bulb": "💡",
        "success": "✅", "failure": "❌", "check": "✔️", "cross": "❌", "up": "⬆️",
        "down": "⬇️", "left": "⬅️", "right": "➡️", "new": "🆕", "old": "👴",
        "vintage": "🕰️", "modern": "📱", "fast": "💨", "slow": "🐌", "high": "⬆️",
        "low": "⬇️", "big": "🐘", "small": "🐜", "hot": "♨️", "cold": "🧊",
        "clean": "🧼", "dirty": "💩", "strong": "💪", "weak": " দুর্বল", "beautiful": "💖",
        "ugly": "🧌", "funny": "😂", "serious": "😐", "cool": "😎", "surprise": "😮",
        "anger": "😡", "fear": "😨", "brave": "🦸", "shy": "腼腆", "crazy": "🤪",
        "smart": "🧠", "stupid": "🤡", "kind": "😇", "mean": "😈", "honest": "🤥",
        "lie": "🤥", "truth": "🧐", "justice": "⚖️", "law": "⚖️", "peace": "☮️",
        "war": "💣", "fight": "🥊", "win": "🏆", "lose": "💀", "gain": "⬆️",
        "loss": "⬇️", "growth": "🌱", "decay": "🍂", "health": "⚕️", "sick": "🤢",
        "doctor": "🩺", "medicine": "💊", "hospital": "🏥", "family": "👨‍👩‍👧‍👦",
        "friend": "🤝", "team": "👥", "group": "👨‍👩‍👧‍👦", "person": "🧍", "man": "👨",
        "woman": "👩", "child": "👶", "boy": "👦", "girl": "👧", "baby": "👶",
        "education": "🎓", "learn": "📖", "teach": "🧑‍🏫", "student": "🧑‍🎓", "teacher": "🧑‍🏫",
        "university": "🎓", "college": "🏛️", "school": "🏫", "class": "🧑‍🤝‍🧑",
        "lesson": "✏️", "homework": "📝", "exam": "💯", "test": "📝", "grade": "💯",
        "certificate": "📜", "diploma": "📜", "award": "🏆", "prize": "🏅", "medal": "🎖️",
        "trophy": "🏆", "gift": "🎁", "present": "🎁", "birthday": "🎂", "anniversary": "🎉",
        "wedding": "💒", "marriage": "💍", "divorce": "💔", "death": "💀", "funeral": "⚰️",
        "ghost": "👻", "monster": "👹", "vampire": "🧛", "zombie": "🧟", "alien": "👽",
        "robot": "🤖", "computer": "🖥️", "laptop": "💻", "desktop": "🖥️", "tablet": " tablet",
        "phone": "📱", "mobile": "📱", "camera": "📸", "video": "📹", "audio": "🎧",
        "microphone": "🎤", "speaker": "🔊", "headphones": "🎧", "tv": "📺", "radio": "📻",
        "internet": "🌐", "wifi": "📶", "bluetooth": "蓝牙", "battery": "🔋", "charge": "🔌",
        "power": "⚡", "electricity": "💡", "solar": "☀️", "wind": "🌬️", "hydro": "🌊",
        "nuclear": "☢️", "recycle": "♻️", "trash": "🗑️", "bin": "🚮", "clean": "🧹",
        "wash": "🧺", "shower": "🚿", "bath": "🛁", "toilet": "🚽", "soap": "🧼",
        "towel": "🧴", "brush": "🖌️", "comb": "💇", "mirror": "🪞", "nail": "💅",
        "hair": "💇‍♀️", "face": "🙂", "body": "🧍", "hand": "🖐️", "foot": "🦶",
        "finger": "👆", "leg": "🦵", "arm": "💪", "head": "🗣️", "eye": "👁️",
        "nose": "👃", "mouth": "👄", "ear": "👂", "brain": "🧠", "bone": "🦴",
        "tooth": "🦷", "blood": "🩸", "pill": "💊", "syring": "💉", "bandage": "🩹",
        "crutch": "🩼", "wheelchair": "♿", "hospital": "🏥", "ambulance": "🚑",
        "fire_engine": "🚒", "police_car": "🚓", "taxi": "🚕", "bus": "🚌",
        "train": "🚆", "airplane": "✈️", "ship": "🚢", "boat": "⛵", "submarine": "🚢",
        "bicycle": "🚲", "motorcycle": "🏍️", "scooter": "🛵", "truck": " ट्रक",
        "tractor": "🚜", "construction": "🚧", "road": "🛣️", "bridge": "🌉",
        "tunnel": "🚇", "city": "🏙️", "town": "🏘️", "village": "🛖", "house": "🏠",
        "apartment": "🏢", "hotel": "🏨", "office": "🏢", "bank": "🏦", "atm": "🏧",
        "store": "🏪", "shop": "🛍️", "restaurant": "🍽️", "cafe": "☕", "bar": "🍺",
        "pizza": "🍕", "burger": "🍔", "fries": "🍟", "sushi": "🍣", "ice_cream": "🍦",
        "cookie": "🍪", "cake": "🎂", "bread": "    🍞", "fruit": "🍎", "vegetable": "🥦",
        "meat": "🥩", "egg": "🥚", "milk": "🥛", "cheese": "🧀", "water": "💧",
        "juice": "🍹", "soda": "🥤", "wine": "🍷", "beer": "🍺", "coffee": "☕",
        "tea": "🍵", "breakfast": "🍳", "lunch": "🥪", "dinner": "🍝", "dessert": "🍰",
        "fork": "🍴", "knife": "🔪", "spoon": "🥄", "plate": "🍽️", "cup": "カップ",
        "glass": "🥛", "bottle": "🍾", "can": "🥫", "bag": "👜", "backpack": "🎒",
        "suitcase": "🧳", "wallet": "👛", "purse": "👜", "money": "💰", "coin": "🪙",
        "bill": "💵", "credit_card": "💳", "receipt": "🧾", "atm": "🏧", "bank": "🏦",
        "safe": "🔒", "key": "🔑", "lock": "🔒", "door": "🚪",
        "window": "🪟", "bed": "🛏️", "chair": "🪑", "table": " テーブル", "desk": " المكتب",
        "lamp": "💡", "clock": "⏰", "watch": "⌚", "ring": "💍", "necklace": "💎",
        "earring": "👂", "bracelet": "📿", "diamond": "💎", "gem": "💎", "crown": "👑",
        "hat": "🎩", "cap": "🧢", "shirt": "👕", "tshirt": "👕", "pants": "👖",
        "jeans": "👖", "shorts": "🩳", "dress": "👗", "skirt": " skirt", "jacket": "🧥",
        "coat": "🧥", "sweater": " स्वेटर", "sock": "🧦", "shoe": "👟", "boot": "🥾",
        "sandal": "👡", "slipper": " slippers", "tie": "👔", "scarf": "🧣", "glove": "🧤",
        "umbrella": "☔", "glasses": "👓", "sunglasses": "🕶️", "mask": "😷", "wig": " wig",
        "razor": "🪒", "scissors": "✂️", "needle": "🪡", "thread": "🧵", "sewing": "🧵",
        "button": " 버튼", "zip": " zipper", "pin": "📌", "glue": "🧴", "tape": " tape"
    }

    normalized_text = text.lower()
    words = re.findall(r'\b\w+\b', normalized_text)  # Extract words

    # Prioritize direct keyword matches
    for word in words:
        if word in word_to_emoji_map:
            selected_emojis.append(word_to_emoji_map[word])
            if len(selected_emojis) >= 4: # Limit to 4 emojis for clarity on small canvas
                break
    
    # Fallback to sentiment analysis if no keyword matches
    if not selected_emojis:
        analysis = TextBlob(text)
        if analysis.sentiment.polarity > 0.2: # Positive sentiment
            selected_emojis.append("😊")
            selected_emojis.append("👍")
        elif analysis.sentiment.polarity < -0.2: # Negative sentiment
            selected_emojis.append("😔")
            selected_emojis.append("👎")
        else: # Neutral or ambiguous sentiment
            selected_emojis.append("💬") # Speech bubble
            selected_emojis.append("🤔") # Thinking face

    # Ensure at least one emoji, if all else fails
    if not selected_emojis:
        selected_emojis = ["✨"] # Sparkles

    # Cap the number of emojis for the icon
    return selected_emojis[:4]