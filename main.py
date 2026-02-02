import os, zipfile, shutil, time, json, sqlite3, hashlib, subprocess, threading, re, base64, sys, datetime, random
from flask import Flask, request, redirect, session, send_file, render_template_string, send_from_directory, jsonify
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Render पर Secret Key को सुरक्षित रखने के लिए
app.secret_key = os.environ.get('SECRET_KEY', 'KR_MASTER_2026_' + str(random.randint(1000, 9999)))
app.config['SESSION_PERMANENT'] = True

# Render और आधुनिक ब्राउज़र्स के लिए CORS सेटिंग्स
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# ==================== DATABASE FIX ====================
def init_database():
    """डेटाबेस इनिशियलाइज़ करें"""
    # Render पर /opt/render/project/src/ डेटाबेस के लिए सही जगह है अगर Disk इस्तेमाल कर रहे हैं
    db_file = 'kr_cloud_v8.db'
    try:
        conn = sqlite3.connect(db_file)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, 
            email TEXT UNIQUE, 
            password TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY,
            user_id INTEGER, user_email TEXT, message TEXT,
            status TEXT DEFAULT 'pending', reply TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files (
            id INTEGER PRIMARY KEY,
            user_id INTEGER, filename TEXT, filepath TEXT,
            uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
        )''')
        conn.commit()
        conn.close()
        print(f"✅ Database Ready: {db_file}")
    except Exception as e:
        print(f"❌ DB Error: {e}")
    return db_file

DB_FILE = init_database()

# डेटाबेस कनेक्शन के लिए हेल्पर (थ्रेड सेफ)
def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    return conn

# ==================== FOLDERS ====================
folders = ['My_private_files', 'user_projects', 'user_complaints', 'support_replies', 'uploads', 'static']
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# --- यहाँ आपका पुराना Index/Login/Signup वाला HTML कोड वैसा ही रहेगा ---
# (समय बचाने के लिए मैंने उसे यहाँ दोबारा पेस्ट नहीं किया है, लेकिन आप अपना वही कोड रखें)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    # आपका पूरा HTML यहाँ पेस्ट करें (जैसा आपने ऊपर दिया था)
    return render_template_string("आपका_लॉगिन_HTML_यहाँ")

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email'].strip().lower()
    password = request.form['password']
    
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['user_email'] = email
        return redirect('/dashboard')
    return redirect('/')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email'].strip().lower()
    password = request.form['password']
    confirm = request.form['confirm']
    
    if password != confirm or len(password) < 6:
        return redirect('/')
    
    hashed = generate_password_hash(password)
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
        conn.commit()
        session['user_id'] = c.lastrowid
        session['user_email'] = email
        conn.close()
        return redirect('/dashboard')
    except:
        return redirect('/')

# ==================== DASHBOARD (UPDATED) ====================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    user_email = session.get('user_email', 'User')
    return f"""
    <html>
    <body style="background:#0A0A1A; color:white; font-family:sans-serif; text-align:center; padding:50px;">
        <h1 style="color:#00D4FF;">🚀 Welcome to K.R CLOUD Dashboard</h1>
        <p>Logged in as: {user_email}</p>
        <div style="margin-top:20px;">
            <a href="/logout" style="color:#FF3366; text-decoration:none; border:1px solid #FF3366; padding:10px 20px; border-radius:10px;">Logout</a>
        </div>
    </body>
    </html>
    """

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ==================== RENDER RUN FIX ====================
if __name__ == '__main__':
    # Render PORT एनवायरनमेंट वेरिएबल का उपयोग करता है
    port = int(os.environ.get("PORT", 5000))
    # SocketIO के साथ ऐप चलाएं
    socketio.run(app, host='0.0.0.0', port=port)
