from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image, ImageDraw
import io
import base64
import numpy as np
import sqlite3
import json

app = Flask(__name__)
CORS(app, resources={r"/generate": {"origins": "https://assignment-gamma-mocha.vercel.app/"}})


def init_db():
    conn = sqlite3.connect('patterns.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT NOT NULL,
            theme TEXT NOT NULL,
            option INTEGER NOT NULL,
            matrix TEXT,
            image_base64 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Themes
themes = {
    'rain': 'rain',
    'sun': 'sun',
    'cloud': 'cloud',
    'snow': 'snow',
    'fire': 'fire',
    'hot': 'fire',
    'heart': 'heart',
    'star': 'star',
    'happy': 'happy',
    'sad': 'sad',
    'angry': 'angry',
}

def detect_theme(text):
    t = text.lower()
    for k, v in themes.items():
        if k in t:
            return v
    return 'default'

def generate_pattern(theme, option):
    # Option 1: base64 image
    if option == 1:
        size = (64, 64)
        img = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        if theme == 'rain':
            for _ in range(20):
                x, y = np.random.randint(0, 64, 2)
                draw.ellipse([x, y, x+4, y+8], fill=(0, 120, 255, 200))
        elif theme == 'sun':
            cx, cy = 32, 32
            draw.ellipse([16, 16, 48, 48], fill=(255, 200, 0, 255))
            for a in range(0, 360, 30):
                r = np.deg2rad(a)
                x1, y1 = cx + 20*np.cos(r), cy + 20*np.sin(r)
                x2, y2 = cx + 30*np.cos(r), cy + 30*np.sin(r)
                draw.line([x1, y1, x2, y2], fill=(255,200,0,200), width=2)
        elif theme == 'cloud':
            draw.ellipse([10,30,30,45], fill=(200,200,200,255))
            draw.ellipse([25,25,45,45], fill=(200,200,200,255))
            draw.rectangle([10,36,45,50], fill=(200,200,200,255))
        elif theme == 'snow':
            for _ in range(15):
                x, y = np.random.randint(5,59,2)
                draw.line([x-3,y, x+3,y], fill=(240,240,255,220))
                draw.line([x,y-3, x,y+3], fill=(240,240,255,220))
        elif theme == 'fire':
            for _ in range(10):
                x = np.random.randint(20,44)
                y = np.random.randint(20,60)
                s = np.random.randint(10,20)
                draw.polygon([(x,y),(x+s/2,y-s),(x+s,y)], fill=(255, np.random.randint(80,150), 0,200))
        elif theme == 'heart':
            draw.polygon([[32,50],[12,30],[20,15],[32,25],[44,15],[52,30]], fill=(255,50,80,255))
        elif theme == 'star':
            pts=[]
            cx,cy=32,32
            for i in range(5):
                a1=np.deg2rad(i*72-90)
                pts.append((cx+20*np.cos(a1), cy+20*np.sin(a1)))
                a2=np.deg2rad(i*72-54)
                pts.append((cx+8*np.cos(a2), cy+8*np.sin(a2)))
            draw.polygon(pts, fill=(255,215,0,255))
        elif theme == 'happy':
            draw.ellipse([8,8,56,56], fill=(255,225,0,255))
            draw.ellipse([20,20,28,28], fill=(0,0,0,255))
            draw.ellipse([36,20,44,28], fill=(0,0,0,255))
            draw.arc([20,24,44,48], start=0, end=180, fill=(0,0,0,255), width=3)
        elif theme == 'sad':
            draw.ellipse([8,8,56,56], fill=(255,225,0,255))
            draw.ellipse([20,20,28,28], fill=(0,0,0,255))
            draw.ellipse([36,20,44,28], fill=(0,0,0,255))
            draw.arc([20,32,44,56], start=180, end=360, fill=(0,0,0,255), width=3)
        elif theme == 'angry':
            draw.ellipse([8,8,56,56], fill=(255,180,0,255))
            draw.line([20,28,28,24], fill=(0,0,0,255), width=3)
            draw.line([36,24,44,28], fill=(0,0,0,255), width=3)
            draw.line([20,44,44,44], fill=(0,0,0,255), width=3)
        else:
            arr = np.random.randint(0,256,(64,64,3),dtype=np.uint8)
            img = Image.fromarray(arr,'RGB')
        return img
    # Option 2: matrix
    matrix = np.zeros((64,64),dtype=int)
    if theme == 'rain':
        for _ in range(20): x,y=np.random.randint(0,64,2); matrix[y:y+8,x:x+4]=1
    elif theme=='sun':
        cx,cy=32,32
        for a in range(0,360,30):
            r=np.deg2rad(a)
            for rad in range(20,31):
                x=int(cx+rad*np.cos(r)); y=int(cy+rad*np.sin(r))
                if 0<=x<64 and 0<=y<64: matrix[y,x]=1
        matrix[16:48,16:48]=1
    elif theme=='cloud': matrix[30:45,10:30]=1; matrix[25:45,25:45]=1; matrix[36:50,10:45]=1
    elif theme=='snow':
        for _ in range(15): x,y=np.random.randint(5,59,2)
        for dx in range(-3,4):
            if 0<=x+dx<64: matrix[y,x+dx]=1
            if 0<=y+dx<64: matrix[y+dx,x]=1
    elif theme=='fire':
        for _ in range(10):
            x=np.random.randint(20,44); y=np.random.randint(4,24); s=np.random.randint(10,20)
            for dy in range(s):
                for dx in range(-dy,dy+1):
                    if 0<=y+dy<64 and 0<=x+dx<64: matrix[y+dy,x+dx]=1
    elif theme=='heart':
        for x,y in [[32,50],[12,30],[20,15],[32,25],[44,15],[52,30]]:
            if 0<=x<64 and 0<=y<64: matrix[y-2:y+3,x-2:x+3]=1
    elif theme=='star':
        cx,cy=32,32; pts=[]
        for i in range(5):
            a1=np.deg2rad(i*72-90); pts.append((int(cx+20*np.cos(a1)),int(cy+20*np.sin(a1))))
            a2=np.deg2rad(i*72-54); pts.append((int(cx+8*np.cos(a2)),int(cy+8*np.sin(a2))))
        for x,y in pts:
            if 0<=x<64 and 0<=y<64: matrix[y-1:y+2,x-1:x+2]=1
    elif theme=='happy':
        for r in range(64):
            for c in range(64):
                if (r-32)**2+(c-32)**2 <= 30**2: matrix[r,c]=1
        for e in [(20,20),(20,44),(44,20),(44,44)]: rx,ry=e; matrix[ry-2:ry+3,rx-2:rx+3]=0
        for r in range(44,52): matrix[r,20:45]=0
    elif theme=='sad':
        for r in range(64):
            for c in range(64):
                if (r-32)**2+(c-32)**2 <= 30**2: matrix[r,c]=1
        for e in [(20,20),(20,44),(44,20),(44,44)]: rx,ry=e; matrix[ry-2:ry+3,rx-2:rx+3]=0
        for offset in range(25): matrix[44+offset//15,20+offset:44-offset]=0
    elif theme=='angry':
        for r in range(64):
            for c in range(64):
                if (r-32)**2+(c-32)**2 <= 30**2: matrix[r,c]=1
        for i in range(5): matrix[20+i,20+i:31+i]=0; matrix[20+i,33-i:45-i]=0
        matrix[44,20:45]=0
    else:
        matrix = np.random.randint(0,2,(64,64),dtype=int)
    return matrix.tolist()

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data or 'text' not in data or 'option' not in data:
        return jsonify({'error':'Please provide prompt and option'}),400
    prompt=data['text']; option=int(data['option'])
    theme=detect_theme(prompt)
    result=generate_pattern(theme,option)

    conn=sqlite3.connect('patterns.db'); c=conn.cursor()
    matrix_json=None; image_b64=None
    if option==1:
        buf=io.BytesIO(); result.save(buf,format='PNG'); buf.seek(0)
        image_b64=base64.b64encode(buf.getvalue()).decode('utf-8'); payload={'theme':theme,'image':image_b64}
    else:
        matrix_json=json.dumps(result); payload={'theme':theme,'matrix':result}
    c.execute('INSERT INTO patterns(prompt,theme,option,matrix,image_base64) VALUES (?,?,?,?,?)',
              (prompt,theme,option,matrix_json,image_b64))
    conn.commit(); conn.close()
    return jsonify(payload)

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
