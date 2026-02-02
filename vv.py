import os, zipfile, shutil, time, json, sqlite3, hashlib, subprocess, threading, re, base64, sys, datetime, random
from flask import Flask, request, redirect, session, send_file, render_template_string, send_from_directory, jsonify
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'KR_MASTER_2026_' + str(random.randint(1000, 9999))
app.config['SESSION_PERMANENT'] = True

socketio = SocketIO(app, cors_allowed_origins="*")

# ==================== DATABASE FIX ====================
def init_database():
    """डेटाबेस इनिशियलाइज़ करें"""
    db_files = ['kr_cloud_v8.db', 'kr_cloud_main.db', 'user_data_v2.db']
    
    for db_file in db_files:
        try:
            if os.path.exists(db_file):
                # टेस्ट करें कि डेटाबेस ठीक है
                test_conn = sqlite3.connect(db_file)
                test_conn.execute("SELECT 1")
                test_conn.close()
                print(f"✅ Using existing database: {db_file}")
                return db_file
        except:
            print(f"⚠️ {db_file} corrupted, will create new")
    
    # नया डेटाबेस बनाएं
    new_db = 'kr_cloud_v8.db'
    print(f"📊 Creating new database: {new_db}")
    return new_db

DB_FILE = init_database()
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()

# टेबल्स बनाएं
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, 
    email TEXT UNIQUE, 
    password TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)''')

c.execute('''CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    user_email TEXT,
    message TEXT,
    status TEXT DEFAULT 'pending',
    reply TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
)''')

c.execute('''CREATE TABLE IF NOT EXISTS user_files (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    filename TEXT,
    filepath TEXT,
    uploaded_at TEXT DEFAULT CURRENT_TIMESTAMP
)''')

conn.commit()

# ==================== FOLDERS ====================
folders = ['My_private_files', 'user_projects', 'user_complaints', 'support_replies', 'uploads', 'static']
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# ==================== ATTRACTIVE LOGIN PAGE ====================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 K.R CLOUD | Login</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {
                --primary: #FF3366;
                --secondary: #00D4FF;
                --accent: #FFD700;
                --dark: #0A0A1A;
                --darker: #050510;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Poppins', 'Segoe UI', sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, var(--darker) 0%, #1A1A3E 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                overflow: hidden;
                position: relative;
            }
            
            .bg-animation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                background: 
                    radial-gradient(circle at 10% 20%, rgba(255, 51, 102, 0.15) 0%, transparent 40%),
                    radial-gradient(circle at 90% 30%, rgba(0, 212, 255, 0.15) 0%, transparent 40%),
                    radial-gradient(circle at 50% 80%, rgba(255, 215, 0, 0.1) 0%, transparent 40%);
                animation: bg-pulse 8s infinite alternate;
            }
            
            @keyframes bg-pulse {
                0% { opacity: 0.7; transform: scale(1); }
                100% { opacity: 1; transform: scale(1.05); }
            }
            
            .login-container {
                width: 95%;
                max-width: 480px;
                z-index: 10;
                animation: slide-up 0.8s ease-out;
            }
            
            @keyframes slide-up {
                from { opacity: 0; transform: translateY(30px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .logo-header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .main-logo {
                font-size: 4.5rem;
                font-weight: 900;
                background: linear-gradient(45deg, var(--primary), var(--secondary), var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 40px rgba(255, 51, 102, 0.4);
                margin-bottom: 10px;
                letter-spacing: 2px;
            }
            
            .tagline {
                font-size: 1.2rem;
                color: #A0A0FF;
                letter-spacing: 3px;
                text-transform: uppercase;
                font-weight: 300;
            }
            
            .login-box {
                background: rgba(20, 20, 40, 0.85);
                backdrop-filter: blur(20px);
                border-radius: 25px;
                padding: 45px 40px;
                box-shadow: 
                    0 20px 60px rgba(0, 0, 0, 0.5),
                    0 0 0 1px rgba(255, 255, 255, 0.1);
                border: 2px solid transparent;
                background-clip: padding-box;
                position: relative;
            }
            
            .login-box::before {
                content: '';
                position: absolute;
                top: -2px;
                left: -2px;
                right: -2px;
                bottom: -2px;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                border-radius: 27px;
                z-index: -1;
                opacity: 0.3;
                animation: border-glow 3s infinite alternate;
            }
            
            @keyframes border-glow {
                0% { opacity: 0.2; }
                100% { opacity: 0.4; }
            }
            
            .tabs {
                display: flex;
                margin-bottom: 35px;
                background: rgba(0, 0, 0, 0.4);
                border-radius: 15px;
                padding: 6px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            
            .tab {
                flex: 1;
                padding: 18px;
                background: transparent;
                border: none;
                color: #888;
                font-size: 1.3rem;
                font-weight: 700;
                cursor: pointer;
                border-radius: 12px;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                letter-spacing: 1px;
            }
            
            .tab.active {
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                color: white;
                box-shadow: 0 8px 25px rgba(255, 51, 102, 0.4);
                transform: translateY(-2px);
            }
            
            .form-group {
                margin-bottom: 28px;
            }
            
            .input-field {
                width: 100%;
                padding: 22px 25px;
                background: rgba(0, 0, 0, 0.5);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                color: white;
                font-size: 1.2rem;
                transition: all 0.3s;
                outline: none;
            }
            
            .input-field:focus {
                border-color: var(--secondary);
                background: rgba(0, 0, 0, 0.6);
                box-shadow: 0 0 25px rgba(0, 212, 255, 0.3);
                transform: translateY(-3px);
            }
            
            .input-field::placeholder {
                color: #666;
            }
            
            .submit-btn {
                width: 100%;
                padding: 22px;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                border: none;
                border-radius: 15px;
                color: white;
                font-size: 1.4rem;
                font-weight: 800;
                cursor: pointer;
                transition: all 0.3s;
                letter-spacing: 2px;
                text-transform: uppercase;
                margin-top: 10px;
                position: relative;
                overflow: hidden;
            }
            
            .submit-btn:hover {
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(255, 51, 102, 0.4);
            }
            
            .submit-btn:active {
                transform: translateY(-2px);
            }
            
            .submit-btn::after {
                content: '';
                position: absolute;
                top: -50%;
                left: -50%;
                width: 200%;
                height: 200%;
                background: linear-gradient(
                    to right,
                    rgba(255, 255, 255, 0) 0%,
                    rgba(255, 255, 255, 0.2) 50%,
                    rgba(255, 255, 255, 0) 100%
                );
                transform: rotate(30deg);
                transition: transform 0.6s;
            }
            
            .submit-btn:hover::after {
                transform: rotate(30deg) translate(100%, 100%);
            }
            
            .message-box {
                text-align: center;
                margin-top: 25px;
                padding: 18px;
                border-radius: 12px;
                font-size: 1.1rem;
                display: none;
                animation: fade-in 0.5s;
            }
            
            @keyframes fade-in {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            .success {
                background: linear-gradient(45deg, rgba(0, 255, 100, 0.2), rgba(0, 200, 255, 0.2));
                color: #00FF88;
                border: 1px solid rgba(0, 255, 100, 0.3);
            }
            
            .error {
                background: linear-gradient(45deg, rgba(255, 50, 50, 0.2), rgba(255, 100, 0, 0.2));
                color: #FF5555;
                border: 1px solid rgba(255, 50, 50, 0.3);
            }
            
            .footer {
                text-align: center;
                margin-top: 35px;
                color: #666;
                font-size: 0.95rem;
            }
            
            .power-text {
                color: var(--secondary);
                font-weight: bold;
                font-size: 1.1rem;
            }
            
            .floating {
                animation: floating 3s ease-in-out infinite;
            }
            
            @keyframes floating {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-10px); }
            }
            
            @media (max-width: 600px) {
                .login-box { padding: 35px 25px; }
                .main-logo { font-size: 3.5rem; }
                .tab { padding: 16px; font-size: 1.1rem; }
                .input-field { padding: 20px; font-size: 1.1rem; }
                .submit-btn { padding: 20px; font-size: 1.2rem; }
            }
            
            /* Particles */
            .particle {
                position: fixed;
                width: 4px;
                height: 4px;
                background: var(--secondary);
                border-radius: 50%;
                pointer-events: none;
                z-index: 1;
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <div class="bg-animation"></div>
        
        <div class="login-container">
            <div class="logo-header">
                <div class="main-logo floating">K.R CLOUD</div>
                <div class="tagline">Next Generation Hosting Platform</div>
            </div>
            
            <div class="login-box">
                <div class="tabs">
                    <button class="tab active" onclick="showTab('login')">🔐 LOGIN</button>
                    <button class="tab" onclick="showTab('signup')">✨ SIGN UP</button>
                </div>
                
                <div id="loginForm">
                    <form method="POST" action="/login" id="loginFormElem">
                        <div class="form-group">
                            <input type="email" name="email" class="input-field" placeholder="📧 ENTER YOUR GMAIL" required>
                        </div>
                        <div class="form-group">
                            <input type="password" name="password" class="input-field" placeholder="🔒 ENTER PASSWORD" required>
                        </div>
                        <button type="submit" class="submit-btn">
                            🚀 ENTER SYSTEM
                        </button>
                    </form>
                </div>
                
                <div id="signupForm" style="display: none;">
                    <form method="POST" action="/signup" id="signupFormElem">
                        <div class="form-group">
                            <input type="email" name="email" class="input-field" placeholder="📧 ENTER GMAIL" required>
                        </div>
                        <div class="form-group">
                            <input type="password" name="password" class="input-field" placeholder="🔒 CREATE PASSWORD" required>
                        </div>
                        <div class="form-group">
                            <input type="password" name="confirm" class="input-field" placeholder="🔒 CONFIRM PASSWORD" required>
                        </div>
                        <button type="submit" class="submit-btn">
                            ⚡ CREATE ACCOUNT
                        </button>
                    </form>
                </div>
                
                <div id="message" class="message-box"></div>
            </div>
            
            <div class="footer">
                <p>Powered by <span class="power-text">K.R MASTER PRO 2026</span></p>
                <p>Advanced Cloud Hosting with Termux Integration</p>
            </div>
        </div>
        
        <script>
            // Particles
            function createParticles() {
                const colors = ['#FF3366', '#00D4FF', '#FFD700', '#00FF88'];
                for (let i = 0; i < 30; i++) {
                    const particle = document.createElement('div');
                    particle.className = 'particle';
                    particle.style.left = Math.random() * 100 + 'vw';
                    particle.style.top = Math.random() * 100 + 'vh';
                    particle.style.background = colors[Math.floor(Math.random() * colors.length)];
                    particle.style.opacity = Math.random() * 0.6 + 0.2;
                    particle.style.width = particle.style.height = (Math.random() * 6 + 2) + 'px';
                    document.body.appendChild(particle);
                    
                    // Animation
                    const duration = Math.random() * 20 + 10;
                    particle.animate([
                        { transform: 'translate(0, 0)', opacity: particle.style.opacity },
                        { transform: `translate(${Math.random() * 200 - 100}px, ${Math.random() * 200 - 100}px)`, opacity: 0 }
                    ], { duration: duration * 1000, easing: 'ease-in-out' });
                    
                    setTimeout(() => particle.remove(), duration * 1000);
                }
            }
            
            // Create particles periodically
            setInterval(createParticles, 1000);
            createParticles();
            
            // Tabs
            function showTab(tab) {
                document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
                event.target.classList.add('active');
                
                document.getElementById('loginForm').style.display = tab === 'login' ? 'block' : 'none';
                document.getElementById('signupForm').style.display = tab === 'signup' ? 'block' : 'none';
            }
            
            // Form submission with AJAX
            document.getElementById('loginFormElem')?.addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const response = await fetch('/login', { method: 'POST', body: formData });
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
            
            document.getElementById('signupFormElem')?.addEventListener('submit', async function(e) {
                e.preventDefault();
                const formData = new FormData(this);
                const response = await fetch('/signup', { method: 'POST', body: formData });
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
            
            // Input focus effects
            document.querySelectorAll('.input-field').forEach(input => {
                input.addEventListener('focus', function() {
                    this.parentElement.style.transform = 'scale(1.02)';
                });
                
                input.addEventListener('blur', function() {
                    this.parentElement.style.transform = 'scale(1)';
                });
            });
        </script>
    </body>
    </html>
    '''

# ==================== LOGIN/SIGNUP ====================
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email'].strip().lower()
    password = request.form['password']
    
    c.execute("SELECT id, password FROM users WHERE email=?", (email,))
    user = c.fetchone()
    
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['user_email'] = email
        session['login_time'] = time.time()
        return redirect('/dashboard')
    
    return redirect('/')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email'].strip().lower()
    password = request.form['password']
    confirm = request.form['confirm']
    
    if password != confirm:
        return redirect('/')
    
    if len(password) < 6:
        return redirect('/')
    
    hashed = generate_password_hash(password)
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
        conn.commit()
        session['user_id'] = c.lastrowid
        session['user_email'] = email
        session['login_time'] = time.time()
        return redirect('/dashboard')
    except sqlite3.IntegrityError:
        return redirect('/')

# ==================== MAIN DASHBOARD ====================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    # Photo capture (once)
    if 'captured' not in session:
        session['captured'] = True
    
    user_email = session.get('user_email', 'User')
    user_id = session.get('user_id', 0)
    
    # Stats
    private_files = len(os.listdir('My_private_files'))
    user_folder = f"user_projects/{user_id}"
    user_files = len(os.listdir(user_folder)) if os.path.exists(user_folder) else 0
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 K.R CLOUD Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --primary: #FF3366;
                --secondary: #00D4FF;
                --accent: #FFD700;
                --success: #00FF88;
                --dark: #0A0A1A;
                --card-bg: rgba(30, 30, 60, 0.7);
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Poppins', sans-serif;
            }}
            
            body {{
                background: linear-gradient(135deg, var(--dark) 0%, #1A1A3E 100%);
                color: white;
                min-height: 100vh;
                overflow-x: hidden;
            }}
            
            /* Floating Menu Button */
            .menu-toggle-btn {{
                position: fixed;
                top: 30px;
                right: 30px;
                z-index: 1001;
                width: 70px;
                height: 70px;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                cursor: pointer;
                font-size: 2.2rem;
                color: white;
                box-shadow: 0 10px 30px rgba(255, 51, 102, 0.4);
                border: none;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                animation: pulse 2s infinite;
            }}
            
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); box-shadow: 0 10px 30px rgba(255, 51, 102, 0.4); }}
                50% {{ transform: scale(1.1); box-shadow: 0 15px 40px rgba(255, 51, 102, 0.6); }}
            }}
            
            .menu-toggle-btn:hover {{
                transform: scale(1.15) rotate(90deg);
                box-shadow: 0 20px 50px rgba(255, 51, 102, 0.6);
            }}
            
            /* Sidebar Menu */
            .sidebar-menu {{
                position: fixed;
                top: 0;
                right: -400px;
                width: 380px;
                height: 100vh;
                background: rgba(20, 20, 40, 0.95);
                backdrop-filter: blur(25px);
                padding: 40px 30px;
                z-index: 1000;
                transition: right 0.5s cubic-bezier(0.4, 0, 0.2, 1);
                border-left: 3px solid var(--primary);
                box-shadow: -20px 0 60px rgba(0, 0, 0, 0.6);
                overflow-y: auto;
            }}
            
            .sidebar-menu.active {{
                right: 0;
            }}
            
            .menu-header {{
                text-align: center;
                margin-bottom: 40px;
                padding-bottom: 25px;
                border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            }}
            
            .menu-title {{
                font-size: 2.2rem;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 10px;
                font-weight: 800;
            }}
            
            .menu-user {{
                color: var(--secondary);
                font-size: 1.1rem;
                font-weight: 600;
            }}
            
            /* Big Menu Buttons */
            .menu-btn {{
                display: block;
                width: 100%;
                padding: 28px 25px;
                margin: 18px 0;
                background: var(--card-bg);
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 1.4rem;
                font-weight: 700;
                text-align: left;
                cursor: pointer;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
                text-decoration: none;
                border: 2px solid transparent;
            }}
            
            .menu-btn:hover {{
                transform: translateX(10px) scale(1.03);
                border-color: var(--primary);
                box-shadow: 0 15px 35px rgba(255, 51, 102, 0.3);
            }}
            
            .menu-btn::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                width: 8px;
                background: linear-gradient(to bottom, var(--primary), var(--secondary));
                opacity: 0;
                transition: opacity 0.3s;
            }}
            
            .menu-btn:hover::before {{
                opacity: 1;
            }}
            
            .btn-icon {{
                font-size: 1.8rem;
                margin-right: 20px;
                vertical-align: middle;
                width: 50px;
                text-align: center;
                display: inline-block;
            }}
            
            /* Unique colors for each button */
            .btn-1 {{ background: linear-gradient(135deg, rgba(255, 51, 102, 0.2), rgba(255, 51, 102, 0.4)); }}
            .btn-2 {{ background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 212, 255, 0.4)); }}
            .btn-3 {{ background: linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 215, 0, 0.4)); }}
            .btn-4 {{ background: linear-gradient(135deg, rgba(0, 255, 136, 0.2), rgba(0, 255, 136, 0.4)); }}
            .btn-5 {{ background: linear-gradient(135deg, rgba(153, 102, 255, 0.2), rgba(153, 102, 255, 0.4)); }}
            .btn-6 {{ background: linear-gradient(135deg, rgba(255, 100, 0, 0.2), rgba(255, 100, 0, 0.4)); }}
            .btn-7 {{ background: linear-gradient(135deg, rgba(0, 200, 255, 0.2), rgba(0, 200, 255, 0.4)); }}
            .btn-8 {{ background: linear-gradient(135deg, rgba(255, 0, 255, 0.2), rgba(255, 0, 255, 0.4)); }}
            
            .btn-logout {{
                background: linear-gradient(135deg, rgba(255, 0, 0, 0.3), rgba(200, 0, 0, 0.5));
                margin-top: 40px;
                text-align: center;
            }}
            
            /* Overlay */
            .overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                backdrop-filter: blur(5px);
                z-index: 999;
                display: none;
                opacity: 0;
                transition: opacity 0.3s;
            }}
            
            .overlay.active {{
                display: block;
                opacity: 1;
            }}
            
            /* Main Content */
            .main-content {{
                padding: 40px;
                max-width: 1400px;
                margin: 0 auto;
            }}
            
            .welcome-section {{
                background: linear-gradient(135deg, rgba(255, 51, 102, 0.1), rgba(0, 212, 255, 0.1));
                border-radius: 30px;
                padding: 50px;
                margin-bottom: 50px;
                border: 2px solid rgba(255, 255, 255, 0.1);
                text-align: center;
                backdrop-filter: blur(10px);
            }}
            
            .welcome-title {{
                font-size: 3.5rem;
                background: linear-gradient(45deg, var(--primary), var(--secondary), var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 20px;
                font-weight: 900;
            }}
            
            .welcome-text {{
                font-size: 1.3rem;
                color: #CCCCFF;
                max-width: 800px;
                margin: 0 auto 40px;
                line-height: 1.8;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 30px;
                margin-top: 50px;
            }}
            
            .stat-card {{
                background: var(--card-bg);
                border-radius: 25px;
                padding: 35px 30px;
                text-align: center;
                border: 2px solid transparent;
                transition: all 0.4s;
                backdrop-filter: blur(10px);
            }}
            
            .stat-card:hover {{
                transform: translateY(-10px);
                border-color: var(--secondary);
                box-shadow: 0 20px 40px rgba(0, 212, 255, 0.2);
            }}
            
            .stat-icon {{
                font-size: 3.5rem;
                margin-bottom: 20px;
                display: block;
            }}
            
            .stat-number {{
                font-size: 3rem;
                font-weight: 800;
                margin-bottom: 10px;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .stat-label {{
                color: #AAA;
                font-size: 1.1rem;
                font-weight: 600;
            }}
            
            .public-link-container {{
                margin-top: 60px;
                text-align: center;
            }}
            
            .public-link-btn {{
                display: inline-block;
                padding: 25px 50px;
                background: linear-gradient(45deg, var(--primary), var(--secondary), var(--accent));
                color: white;
                text-decoration: none;
                border-radius: 20px;
                font-size: 1.5rem;
                font-weight: 800;
                transition: all 0.4s;
                letter-spacing: 1px;
                box-shadow: 0 15px 35px rgba(255, 51, 102, 0.3);
            }}
            
            .public-link-btn:hover {{
                transform: translateY(-8px) scale(1.05);
                box-shadow: 0 25px 50px rgba(255, 51, 102, 0.5);
                letter-spacing: 2px;
            }}
            
            /* Responsive */
            @media (max-width: 768px) {{
                .sidebar-menu {{ width: 320px; right: -320px; padding: 30px 20px; }}
                .menu-btn {{ padding: 22px 20px; font-size: 1.2rem; }}
                .menu-toggle-btn {{ top: 20px; right: 20px; width: 60px; height: 60px; font-size: 1.8rem; }}
                .welcome-title {{ font-size: 2.5rem; }}
                .welcome-section {{ padding: 30px 20px; }}
                .main-content {{ padding: 20px; }}
                .stat-card {{ padding: 25px 20px; }}
            }}
            
            /* Scrollbar */
            .sidebar-menu::-webkit-scrollbar {{
                width: 8px;
            }}
            
            .sidebar-menu::-webkit-scrollbar-track {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 10px;
            }}
            
            .sidebar-menu::-webkit-scrollbar-thumb {{
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                border-radius: 10px;
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <!-- Floating Menu Button -->
        <button class="menu-toggle-btn" onclick="toggleMenu()">
            ☰
        </button>
        
        <!-- Sidebar Menu -->
        <div class="sidebar-menu" id="sidebarMenu">
            <div class="menu-header">
                <div class="menu-title">MAIN MENU</div>
                <div class="menu-user">👤 {user_email}</div>
            </div>
            
            <a href="/file_download" class="menu-btn btn-1">
                <span class="btn-icon">📥</span> 1. FILE DOWNLOAD
            </a>
            
            <a href="/upload_zip" class="menu-btn btn-2">
                <span class="btn-icon">📤</span> 2. UPLOAD ZIP
            </a>
            
            <a href="/my_projects" class="menu-btn btn-3">
                <span class="btn-icon">📁</span> 3. MY PROJECTS
            </a>
            
            <a href="/termux" class="menu-btn btn-4">
                <span class="btn-icon">📟</span> 4. TERMUX
            </a>
            
            <a href="/bot_engine" class="menu-btn btn-5">
                <span class="btn-icon">🤖</span> 5. BOT ENGINE
            </a>
            
            <a href="/support" class="menu-btn btn-6">
                <span class="btn-icon">📩</span> 6. SUPPORT
            </a>
            
            <a href="/view_replies" class="menu-btn btn-7">
                <span class="btn-icon">📨</span> 7. VIEW REPLIES
            </a>
            
            <a href="/public_link" class="menu-btn btn-8">
                <span class="btn-icon">🌍</span> PUBLIC LINK
            </a>
            
            <a href="/logout" class="menu-btn btn-logout">
                <span class="btn-icon">🚪</span> LOGOUT
            </a>
        </div>
        
        <!-- Overlay -->
        <div class="overlay" id="overlay" onclick="toggleMenu()"></div>
        
        <!-- Main Content -->
        <div class="main-content">
            <div class="welcome-section">
                <h1 class="welcome-title">Welcome to K.R CLOUD PRO</h1>
                <p class="welcome-text">
                    Experience the future of cloud hosting with advanced features, 
                    real-time terminal access, bot automation, and secure file management. 
                    Everything you need for modern web development.
                </p>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-icon">📦</span>
                        <div class="stat-number">{private_files}</div>
                        <div class="stat-label">Private Files</div>
                    </div>
                    
                    <div class="stat-card">
                        <span class="stat-icon">📁</span>
                        <div class="stat-number">{user_files}</div>
                        <div class="stat-label">Your Files</div>
                    </div>
                    
                    <div class="stat-card">
                        <span class="stat-icon">⚡</span>
                        <div class="stat-number">24/7</div>
                        <div class="stat-label">Uptime</div>
                    </div>
                    
                    <div class="stat-card">
                        <span class="stat-icon">🔐</span>
                        <div class="stat-number">100%</div>
                        <div class="stat-label">Secure</div>
                    </div>
                </div>
                
                <div class="public-link-container">
                    <a href="/public_link" class="public-link-btn">
                        🌍 GET PUBLIC LINK
                    </a>
                </div>
            </div>
        </div>
        
        <script>
            function toggleMenu() {{
                const sidebar = document.getElementById('sidebarMenu');
                const overlay = document.getElementById('overlay');
                const isActive = sidebar.classList.contains('active');
                
                if (isActive) {{
                    sidebar.classList.remove('active');
                    overlay.classList.remove('active');
                }} else {{
                    sidebar.classList.add('active');
                    overlay.classList.add('active');
                }}
            }}
            
            // Close menu on escape key
            document.addEventListener('keydown', function(e) {{
                if (e.key === 'Escape') {{
                    document.getElementById('sidebarMenu').classList.remove('active');
                    document.getElementById('overlay').classList.remove('active');
                }}
            }});
            
            // Auto-close menu on mobile when clicking item
            document.querySelectorAll('.menu-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    if (window.innerWidth < 768) {{
                        toggleMenu();
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    '''

# ==================== FILE DOWNLOAD PAGE ====================
@app.route('/file_download')
def file_download():
    if 'user_id' not in session:
        return redirect('/')
    
    files = os.listdir('My_private_files')
    files_html = ""
    
    colors = ['#FF3366', '#00D4FF', '#FFD700', '#00FF88', '#9966FF', '#FF6600']
    
    for idx, f in enumerate(files):
        color = colors[idx % len(colors)]
        file_path = os.path.join('My_private_files', f)
        size = os.path.getsize(file_path)
        size_str = f"{size // 1024} KB" if size < 1024*1024 else f"{size // (1024*1024)} MB"
        
        files_html += f'''
        <div class="file-card" style="border-left: 8px solid {color};">
            <div class="file-icon">📦</div>
            <div class="file-info">
                <div class="file-name">{f}</div>
                <div class="file-meta">
                    <span>📏 {size_str}</span>
                    <span>🕒 {datetime.datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%d/%m/%Y')}</span>
                </div>
            </div>
            <div class="file-actions">
                <a href="/download_private/{f}" class="action-btn" style="background:{color};">
                    ⬇️ DOWNLOAD
                </a>
                <a href="/unzip_file/{f}" class="action-btn" style="background:#FFD700;" 
                   onclick="return confirm('Unzip this file to your projects folder?')">
                    📂 UNZIP
                </a>
            </div>
        </div>'''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📥 File Download</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --primary: #FF3366;
                --dark: #0A0A1A;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Poppins', sans-serif;
            }}
            
            body {{
                background: linear-gradient(135deg, var(--dark) 0%, #1A1A3E 100%);
                color: white;
                min-height: 100vh;
                padding: 30px;
            }}
            
            .back-btn {{
                display: inline-block;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 15px;
                margin-bottom: 40px;
                font-size: 1.1rem;
                font-weight: 600;
                transition: all 0.3s;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }}
            
            .back-btn:hover {{
                background: rgba(255, 255, 255, 0.2);
                transform: translateX(-10px);
                border-color: var(--primary);
            }}
            
            .page-header {{
                text-align: center;
                margin-bottom: 50px;
            }}
            
            .page-title {{
                font-size: 3.5rem;
                background: linear-gradient(45deg, #FF3366, #00D4FF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 15px;
                font-weight: 900;
            }}
            
            .page-subtitle {{
                color: #AAA;
                font-size: 1.3rem;
                max-width: 600px;
                margin: 0 auto;
            }}
            
            .files-container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .file-card {{
                background: rgba(30, 30, 60, 0.7);
                backdrop-filter: blur(10px);
                border-radius: 25px;
                padding: 35px;
                margin: 25px 0;
                display: flex;
                align-items: center;
                gap: 30px;
                border: 2px solid rgba(255, 255, 255, 0.1);
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }}
            
            .file-card:hover {{
                transform: translateY(-10px) scale(1.02);
                border-color: var(--primary);
                box-shadow: 0 25px 50px rgba(255, 51, 102, 0.2);
                background: rgba(40, 40, 70, 0.8);
            }}
            
            .file-icon {{
                font-size: 4rem;
                flex-shrink: 0;
            }}
            
            .file-info {{
                flex: 1;
            }}
            
            .file-name {{
                font-size: 1.8rem;
                font-weight: 700;
                margin-bottom: 12px;
                color: white;
            }}
            
            .file-meta {{
                display: flex;
                gap: 25px;
                color: #AAA;
                font-size: 1rem;
            }}
            
            .file-actions {{
                display: flex;
                gap: 20px;
                flex-shrink: 0;
            }}
            
            .action-btn {{
                padding: 18px 30px;
                color: white;
                text-decoration: none;
                border-radius: 15px;
                font-weight: 800;
                font-size: 1.1rem;
                transition: all 0.3s;
                min-width: 160px;
                text-align: center;
                border: none;
                cursor: pointer;
                letter-spacing: 1px;
            }}
            
            .action-btn:hover {{
                transform: translateY(-5px) scale(1.05);
                box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
                letter-spacing: 2px;
            }}
            
            .empty-state {{
                text-align: center;
                padding: 100px 20px;
            }}
            
            .empty-icon {{
                font-size: 8rem;
                margin-bottom: 30px;
                opacity: 0.5;
            }}
            
            .empty-text {{
                color: #888;
                font-size: 1.5rem;
                margin-bottom: 40px;
            }}
            
            @media (max-width: 768px) {{
                .file-card {{
                    flex-direction: column;
                    text-align: center;
                    padding: 25px;
                    gap: 20px;
                }}
                
                .file-actions {{
                    flex-direction: column;
                    width: 100%;
                }}
                
                .action-btn {{
                    width: 100%;
                }}
                
                .page-title {{
                    font-size: 2.5rem;
                }}
                
                body {{
                    padding: 20px;
                }}
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← BACK TO DASHBOARD</a>
        
        <div class="page-header">
            <h1 class="page-title">📥 FILE DOWNLOAD CENTER</h1>
            <p class="page-subtitle">Download or unzip files from My_private_files folder</p>
        </div>
        
        <div class="files-container">
            {files_html if files_html else '''
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <div class="empty-text">No files available in My_private_files folder</div>
                <a href="/dashboard" class="action-btn" style="background:#00D4FF; display:inline-block;">
                    ← GO BACK
                </a>
            </div>
            '''}
        </div>
        
        <script>
            // Add some interactive effects
            document.querySelectorAll('.file-card').forEach(card => {{
                card.addEventListener('mouseenter', function() {{
                    this.style.transform = 'translateY(-10px) scale(1.02)';
                }});
                
                card.addEventListener('mouseleave', function() {{
                    this.style.transform = 'translateY(0) scale(1)';
                }});
            }});
        </script>
    </body>
    </html>
    '''

# ==================== FILE OPERATIONS ====================
@app.route('/download_private/<filename>')
def download_private(filename):
    if 'user_id' not in session:
        return redirect('/')
    return send_from_directory('My_private_files', filename, as_attachment=True)

@app.route('/unzip_file/<filename>')
def unzip_file(filename):
    if 'user_id' not in session:
        return redirect('/')
    
    user_folder = f"user_projects/{session['user_id']}"
    os.makedirs(user_folder, exist_ok=True)
    
    zip_path = os.path.join('My_private_files', filename)
    if zipfile.is_zipfile(zip_path):
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(user_folder)
            return redirect('/my_projects')
        except:
            return "Error extracting ZIP file"
    return "Not a valid ZIP file"

# ==================== UPLOAD ZIP PAGE ====================
@app.route('/upload_zip', methods=['GET', 'POST'])
def upload_zip():
    if 'user_id' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        if 'zip_file' not in request.files:
            return redirect('/upload_zip')
        
        file = request.files['zip_file']
        if file.filename.endswith('.zip'):
            user_folder = f"user_projects/{session['user_id']}"
            os.makedirs(user_folder, exist_ok=True)
            
            # Save ZIP
            zip_path = os.path.join(user_folder, file.filename)
            file.save(zip_path)
            
            # Extract
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(user_folder)
                os.remove(zip_path)
                return redirect('/my_projects')
            except:
                return "Error extracting ZIP"
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📤 Upload ZIP</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {
                --primary: #00D4FF;
                --dark: #0A0A1A;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Poppins', sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, var(--dark) 0%, #1A1A3E 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .upload-container {
                background: rgba(30, 30, 60, 0.8);
                backdrop-filter: blur(20px);
                border-radius: 30px;
                padding: 50px;
                width: 90%;
                max-width: 600px;
                border: 3px dashed var(--primary);
                text-align: center;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            }
            
            .back-btn {
                position: absolute;
                top: 30px;
                left: 30px;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 15px;
                font-weight: 600;
                transition: all 0.3s;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
            
            .back-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateX(-10px);
                border-color: var(--primary);
            }
            
            .upload-icon {
                font-size: 6rem;
                margin-bottom: 30px;
                display: block;
                color: var(--primary);
            }
            
            .upload-title {
                font-size: 2.8rem;
                margin-bottom: 20px;
                background: linear-gradient(45deg, #00D4FF, #00FF88);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 900;
            }
            
            .upload-subtitle {
                color: #AAA;
                margin-bottom: 40px;
                font-size: 1.2rem;
                line-height: 1.6;
            }
            
            .file-input-wrapper {
                position: relative;
                margin-bottom: 40px;
            }
            
            .file-input {
                width: 100%;
                padding: 30px;
                background: rgba(0, 0, 0, 0.4);
                border: 3px solid #444;
                border-radius: 20px;
                color: white;
                font-size: 1.3rem;
                cursor: pointer;
                transition: all 0.3s;
            }
            
            .file-input:hover {
                border-color: var(--primary);
                background: rgba(0, 0, 0, 0.5);
                transform: translateY(-5px);
                box-shadow: 0 15px 30px rgba(0, 212, 255, 0.2);
            }
            
            .upload-btn {
                width: 100%;
                padding: 25px;
                background: linear-gradient(45deg, #00D4FF, #00FF88);
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 1.5rem;
                font-weight: 800;
                cursor: pointer;
                transition: all 0.3s;
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            
            .upload-btn:hover {
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(0, 212, 255, 0.4);
                letter-spacing: 4px;
            }
            
            .upload-btn:disabled {
                opacity: 0.7;
                cursor: not-allowed;
                transform: none;
            }
            
            @media (max-width: 600px) {
                .upload-container {
                    padding: 30px 20px;
                }
                
                .upload-title {
                    font-size: 2.2rem;
                }
                
                .upload-icon {
                    font-size: 4rem;
                }
                
                .file-input, .upload-btn {
                    padding: 20px;
                    font-size: 1.1rem;
                }
                
                .back-btn {
                    top: 20px;
                    left: 20px;
                    padding: 12px 25px;
                }
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← BACK</a>
        
        <div class="upload-container">
            <div class="upload-icon">📤</div>
            <h1 class="upload-title">UPLOAD ZIP FILE</h1>
            <p class="upload-subtitle">
                Upload your project ZIP file. It will be automatically extracted 
                to your personal projects folder for editing and running.
            </p>
            
            <form method="POST" enctype="multipart/form-data" onsubmit="startUpload()">
                <div class="file-input-wrapper">
                    <input type="file" name="zip_file" class="file-input" accept=".zip" required 
                           onchange="showFileName(this)">
                </div>
                
                <button type="submit" class="upload-btn" id="uploadBtn">
                    🚀 UPLOAD & EXTRACT
                </button>
            </form>
        </div>
        
        <script>
            function showFileName(input) {
                const fileName = input.files[0]?.name || 'No file chosen';
                input.style.background = `rgba(0, 212, 255, 0.1)`;
            }
            
            function startUpload() {
                const btn = document.getElementById('uploadBtn');
                btn.innerHTML = '⏳ UPLOADING...';
                btn.disabled = true;
            }
        </script>
    </body>
    </html>
    '''

# ==================== SUPPORT PAGE ====================
@app.route('/support', methods=['GET', 'POST'])
def support():
    if 'user_id' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        message = request.form['message']
        user_email = session['user_email']
        
        # Save to database
        c.execute("INSERT INTO complaints (user_id, user_email, message) VALUES (?, ?, ?)",
                 (session['user_id'], user_email, message))
        conn.commit()
        
        # Save to file
        timestamp = int(time.time())
        complaint_file = f"user_complaints/complaint_{session['user_id']}_{timestamp}.txt"
        with open(complaint_file, 'w', encoding='utf-8') as f:
            f.write(f"User: {user_email}\n")
            f.write(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"ID: {timestamp}\n")
            f.write(f"\n{'='*50}\n\n")
            f.write(message)
        
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>✅ Complaint Submitted</title>
            <style>
                body {
                    background: linear-gradient(135deg, #0A0A1A 0%, #1A1A3E 100%);
                    color: white;
                    font-family: 'Poppins', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    padding: 20px;
                    text-align: center;
                }
                
                .success-box {
                    background: rgba(0, 255, 100, 0.1);
                    border: 2px solid rgba(0, 255, 100, 0.3);
                    border-radius: 25px;
                    padding: 60px 40px;
                    max-width: 600px;
                    backdrop-filter: blur(10px);
                }
                
                .success-icon {
                    font-size: 6rem;
                    margin-bottom: 30px;
                    display: block;
                }
                
                .success-title {
                    font-size: 2.8rem;
                    margin-bottom: 20px;
                    color: #00FF88;
                }
                
                .success-text {
                    font-size: 1.3rem;
                    color: #CCC;
                    margin-bottom: 40px;
                    line-height: 1.6;
                }
                
                .action-btn {
                    display: inline-block;
                    padding: 18px 35px;
                    background: linear-gradient(45deg, #00D4FF, #00FF88);
                    color: white;
                    text-decoration: none;
                    border-radius: 15px;
                    font-size: 1.2rem;
                    font-weight: 700;
                    margin: 10px;
                    transition: all 0.3s;
                }
                
                .action-btn:hover {
                    transform: translateY(-5px);
                    box-shadow: 0 15px 30px rgba(0, 212, 255, 0.3);
                }
            </style>
        </head>
        <body>
            <div class="success-box">
                <div class="success-icon">✅</div>
                <h1 class="success-title">COMPLAINT SUBMITTED!</h1>
                <p class="success-text">
                    Your complaint has been received. We will review it and respond 
                    within 24 hours. You can check for replies in the View Replies section.
                </p>
                <div>
                    <a href="/dashboard" class="action-btn">🏠 DASHBOARD</a>
                    <a href="/view_replies" class="action-btn">📨 VIEW REPLIES</a>
                </div>
            </div>
        </body>
        </html>
        '''
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📩 Support</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {
                --primary: #FF6600;
                --dark: #0A0A1A;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Poppins', sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, var(--dark) 0%, #1A1A3E 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .support-container {
                background: rgba(30, 30, 60, 0.8);
                backdrop-filter: blur(20px);
                border-radius: 30px;
                padding: 50px;
                width: 90%;
                max-width: 700px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
            
            .back-btn {
                position: absolute;
                top: 30px;
                left: 30px;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 15px;
                font-weight: 600;
                transition: all 0.3s;
            }
            
            .back-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateX(-10px);
                border-color: var(--primary);
            }
            
            .support-header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            .support-icon {
                font-size: 5rem;
                margin-bottom: 20px;
                display: block;
                color: var(--primary);
            }
            
            .support-title {
                font-size: 2.8rem;
                background: linear-gradient(45deg, #FF6600, #FFD700);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 15px;
                font-weight: 900;
            }
            
            .support-subtitle {
                color: #AAA;
                font-size: 1.2rem;
                max-width: 600px;
                margin: 0 auto;
            }
            
            textarea {
                width: 100%;
                height: 250px;
                background: rgba(0, 0, 0, 0.4);
                border: 3px solid #444;
                border-radius: 20px;
                color: white;
                padding: 25px;
                font-size: 1.2rem;
                font-family: inherit;
                margin-bottom: 35px;
                resize: vertical;
                transition: all 0.3s;
                outline: none;
            }
            
            textarea:focus {
                border-color: var(--primary);
                background: rgba(0, 0, 0, 0.5);
                box-shadow: 0 0 30px rgba(255, 102, 0, 0.3);
                transform: translateY(-5px);
            }
            
            .submit-btn {
                width: 100%;
                padding: 25px;
                background: linear-gradient(45deg, #FF6600, #FF3366);
                border: none;
                border-radius: 20px;
                color: white;
                font-size: 1.5rem;
                font-weight: 800;
                cursor: pointer;
                transition: all 0.3s;
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            
            .submit-btn:hover {
                transform: translateY(-8px);
                box-shadow: 0 20px 40px rgba(255, 102, 0, 0.4);
                letter-spacing: 4px;
            }
            
            @media (max-width: 600px) {
                .support-container {
                    padding: 30px 20px;
                }
                
                .support-title {
                    font-size: 2.2rem;
                }
                
                .support-icon {
                    font-size: 3.5rem;
                }
                
                textarea {
                    height: 200px;
                    padding: 20px;
                    font-size: 1.1rem;
                }
                
                .submit-btn {
                    padding: 20px;
                    font-size: 1.2rem;
                }
                
                .back-btn {
                    top: 20px;
                    left: 20px;
                    padding: 12px 25px;
                }
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← BACK</a>
        
        <div class="support-container">
            <div class="support-header">
                <div class="support-icon">📩</div>
                <h1 class="support-title">SUPPORT & COMPLAINTS</h1>
                <p class="support-subtitle">
                    Describe your issue in detail. Our team will respond within 24 hours.
                    All complaints are saved securely.
                </p>
            </div>
            
            <form method="POST">
                <textarea name="message" placeholder="Describe your problem or issue here... 
Be as detailed as possible. Include error messages, steps to reproduce, and what you were trying to achieve." 
required></textarea>
                
                <button type="submit" class="submit-btn">
                    🚀 SUBMIT COMPLAINT
                </button>
            </form>
        </div>
    </body>
    </html>
    '''

# ==================== VIEW REPLIES ====================
@app.route('/view_replies')
def view_replies():
    if 'user_id' not in session:
        return redirect('/')
    
    c.execute("SELECT * FROM complaints WHERE user_id=? ORDER BY id DESC", (session['user_id'],))
    complaints = c.fetchall()
    
    replies_html = ""
    
    for comp in complaints:
        status_color = "#00FF88" if comp[4] == 'resolved' else "#FFD700"
        status_icon = "✅" if comp[4] == 'resolved' else "⏳"
        
        replies_html += f'''
        <div class="complaint-card">
            <div class="complaint-header">
                <div class="complaint-id">ID: #{comp[0]}</div>
                <div class="complaint-status" style="color:{status_color};">
                    {status_icon} {comp[4].upper()}
                </div>
            </div>
            
            <div class="complaint-time">
                📅 {comp[6] if comp[6] else 'Recent'}
            </div>
            
            <div class="complaint-message">
                {comp[3]}
            </div>
            
            {f'''
            <div class="reply-section">
                <div class="reply-label">📨 ADMIN REPLY:</div>
                <div class="reply-content">
                    {comp[5]}
                </div>
            </div>
            ''' if comp[5] else '''
            <div class="no-reply">
                ⏳ No reply yet. Please check back later.
            </div>
            '''}
        </div>
        '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📨 View Replies</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --primary: #9966FF;
                --dark: #0A0A1A;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Poppins', sans-serif;
            }}
            
            body {{
                background: linear-gradient(135deg, var(--dark) 0%, #1A1A3E 100%);
                color: white;
                min-height: 100vh;
                padding: 30px;
            }}
            
            .back-btn {{
                display: inline-block;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 15px;
                margin-bottom: 40px;
                font-size: 1.1rem;
                font-weight: 600;
                transition: all 0.3s;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }}
            
            .back-btn:hover {{
                background: rgba(255, 255, 255, 0.2);
                transform: translateX(-10px);
                border-color: var(--primary);
            }}
            
            .page-header {{
                text-align: center;
                margin-bottom: 50px;
            }}
            
            .page-title {{
                font-size: 3.5rem;
                background: linear-gradient(45deg, #9966FF, #00D4FF);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 15px;
                font-weight: 900;
            }}
            
            .page-subtitle {{
                color: #AAA;
                font-size: 1.3rem;
                max-width: 600px;
                margin: 0 auto;
            }}
            
            .replies-container {{
                max-width: 900px;
                margin: 0 auto;
            }}
            
            .complaint-card {{
                background: rgba(30, 30, 60, 0.7);
                backdrop-filter: blur(10px);
                border-radius: 25px;
                padding: 35px;
                margin: 25px 0;
                border: 2px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s;
            }}
            
            .complaint-card:hover {{
                transform: translateY(-5px);
                border-color: var(--primary);
                box-shadow: 0 20px 40px rgba(153, 102, 255, 0.2);
            }}
            
            .complaint-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
                padding-bottom: 15px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .complaint-id {{
                font-size: 1.3rem;
                font-weight: 700;
                color: #00D4FF;
            }}
            
            .complaint-status {{
                font-size: 1.1rem;
                font-weight: 700;
                padding: 8px 20px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }}
            
            .complaint-time {{
                color: #AAA;
                margin-bottom: 25px;
                font-size: 1rem;
            }}
            
            .complaint-message {{
                background: rgba(0, 0, 0, 0.3);
                padding: 25px;
                border-radius: 15px;
                margin-bottom: 25px;
                line-height: 1.6;
                font-size: 1.1rem;
                border-left: 5px solid #FF3366;
            }}
            
            .reply-section {{
                background: linear-gradient(135deg, rgba(0, 255, 136, 0.1), rgba(0, 212, 255, 0.1));
                padding: 25px;
                border-radius: 15px;
                border: 2px solid rgba(0, 255, 136, 0.3);
            }}
            
            .reply-label {{
                font-size: 1.2rem;
                font-weight: 700;
                color: #00FF88;
                margin-bottom: 15px;
            }}
            
            .reply-content {{
                font-size: 1.1rem;
                line-height: 1.6;
                color: #CCC;
            }}
            
            .no-reply {{
                text-align: center;
                padding: 30px;
                color: #888;
                font-size: 1.2rem;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                border: 2px dashed rgba(255, 255, 255, 0.1);
            }}
            
            .empty-state {{
                text-align: center;
                padding: 100px 20px;
            }}
            
            .empty-icon {{
                font-size: 8rem;
                margin-bottom: 30px;
                opacity: 0.5;
            }}
            
            .empty-text {{
                color: #888;
                font-size: 1.5rem;
                margin-bottom: 40px;
            }}
            
            @media (max-width: 768px) {{
                .complaint-card {{
                    padding: 25px;
                }}
                
                .complaint-header {{
                    flex-direction: column;
                    gap: 15px;
                    text-align: center;
                }}
                
                .page-title {{
                    font-size: 2.5rem;
                }}
                
                body {{
                    padding: 20px;
                }}
            }}
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← BACK TO DASHBOARD</a>
        
        <div class="page-header">
            <h1 class="page-title">📨 SUPPORT REPLIES</h1>
            <p class="page-subtitle">Check responses to your complaints and support requests</p>
        </div>
        
        <div class="replies-container">
            {replies_html if replies_html else '''
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <div class="empty-text">No complaints or replies yet</div>
                <a href="/support" class="back-btn" style="background:#9966FF;">
                    📩 SUBMIT FIRST COMPLAINT
                </a>
            </div>
            '''}
        </div>
    </body>
    </html>
    '''

# ==================== PUBLIC LINK PAGE ====================
@app.route('/public_link')
def public_link():
    if 'user_id' not in session:
        return redirect('/')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🌍 Public Link</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {
                --primary: #00D4FF;
                --secondary: #FF3366;
                --accent: #FFD700;
                --dark: #0A0A1A;
            }
            
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Poppins', sans-serif;
            }
            
            body {
                background: linear-gradient(135deg, var(--dark) 0%, #1A1A3E 100%);
                color: white;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .link-container {
                background: rgba(30, 30, 60, 0.8);
                backdrop-filter: blur(20px);
                border-radius: 30px;
                padding: 50px;
                width: 90%;
                max-width: 800px;
                text-align: center;
                border: 3px solid transparent;
                background-clip: padding-box;
                position: relative;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            }
            
            .link-container::before {
                content: '';
                position: absolute;
                top: -3px;
                left: -3px;
                right: -3px;
                bottom: -3px;
                background: linear-gradient(45deg, var(--primary), var(--secondary), var(--accent));
                border-radius: 33px;
                z-index: -1;
                opacity: 0.3;
                animation: border-rotate 10s linear infinite;
            }
            
            @keyframes border-rotate {
                0% { filter: hue-rotate(0deg); }
                100% { filter: hue-rotate(360deg); }
            }
            
            .back-btn {
                position: absolute;
                top: 30px;
                left: 30px;
                padding: 15px 30px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 15px;
                font-weight: 600;
                transition: all 0.3s;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
            
            .back-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateX(-10px);
                border-color: var(--primary);
            }
            
            .link-icon {
                font-size: 7rem;
                margin-bottom: 30px;
                display: block;
                animation: float 3s ease-in-out infinite;
            }
            
            @keyframes float {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-20px); }
            }
            
            .link-title {
                font-size: 3.5rem;
                margin-bottom: 20px;
                background: linear-gradient(45deg, var(--primary), var(--secondary), var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                font-weight: 900;
            }
            
            .link-subtitle {
                color: #AAA;
                margin-bottom: 50px;
                font-size: 1.3rem;
                line-height: 1.6;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            
            .link-box {
                background: rgba(0, 0, 0, 0.4);
                border-radius: 20px;
                padding: 35px;
                margin: 40px 0;
                border: 2px dashed var(--primary);
                position: relative;
                overflow: hidden;
            }
            
            .link-box::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, var(--primary), var(--secondary));
                animation: slide 2s linear infinite;
            }
            
            @keyframes slide {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            .public-link {
                font-size: 1.8rem;
                color: #00FF88;
                font-weight: 700;
                word-break: break-all;
                margin-bottom: 20px;
                padding: 20px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 15px;
                border: 2px solid rgba(0, 255, 136, 0.3);
            }
            
            .link-status {
                font-size: 1.2rem;
                color: #FFD700;
                margin-top: 15px;
            }
            
            .action-buttons {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 25px;
                margin-top: 50px;
            }
            
            .action-btn {
                padding: 25px;
                border: none;
                border-radius: 20px;
                font-size: 1.3rem;
                font-weight: 800;
                cursor: pointer;
                transition: all 0.3s;
                text-decoration: none;
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 15px;
                min-height: 100px;
            }
            
            .copy-btn {
                background: linear-gradient(45deg, var(--primary), #00FF88);
                color: white;
            }
            
            .test-btn {
                background: linear-gradient(45deg, #FFD700, #FF6600);
                color: white;
            }
            
            .generate-btn {
                background: linear-gradient(45deg, var(--secondary), #FF00FF);
                color: white;
            }
            
            .action-btn:hover {
                transform: translateY(-10px) scale(1.05);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
            }
            
            .local-info {
                margin-top: 60px;
                padding: 30px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 0.1);
            }
            
            .local-title {
                font-size: 1.5rem;
                color: var(--primary);
                margin-bottom: 15px;
            }
            
            .local-url {
                font-size: 1.3rem;
                color: #00FF88;
                font-weight: 700;
                word-break: break-all;
                padding: 15px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 10px;
                margin: 15px 0;
            }
            
            @media (max-width: 768px) {
                .link-container {
                    padding: 30px 20px;
                }
                
                .link-title {
                    font-size: 2.5rem;
                }
                
                .link-icon {
                    font-size: 5rem;
                }
                
                .public-link {
                    font-size: 1.3rem;
                    padding: 15px;
                }
                
                .action-buttons {
                    grid-template-columns: 1fr;
                }
                
                .action-btn {
                    min-height: 80px;
                    padding: 20px;
                    font-size: 1.1rem;
                }
                
                .back-btn {
                    top: 20px;
                    left: 20px;
                    padding: 12px 25px;
                }
            }
        </style>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← BACK</a>
        
        <div class="link-container">
            <div class="link-icon">🌍</div>
            <h1 class="link-title">PUBLIC ACCESS LINK</h1>
            <p class="link-subtitle">
                Share this link with anyone to access your website from anywhere in the world.
                The link is automatically generated using Cloudflare Tunnel for secure public access.
            </p>
            
            <div class="link-box">
                <div id="publicLink" class="public-link">
                    ⏳ Generating public link...
                </div>
                <div id="linkStatus" class="link-status">
                    Please wait while we establish a secure tunnel
                </div>
            </div>
            
            <div class="action-buttons">
                <button class="action-btn copy-btn" onclick="copyLink()">
                    📋 COPY LINK
                </button>
                
                <a href="http://localhost:5000" target="_blank" class="action-btn test-btn">
                    🌐 TEST LOCAL
                </a>
                
                <button class="action-btn generate-btn" onclick="generateNewLink()">
                    🔄 GENERATE NEW
                </button>
            </div>
            
            <div class="local-info">
                <div class="local-title">📱 LOCAL ACCESS</div>
                <div class="local-url">http://localhost:5000</div>
                <p style="color: #AAA; font-size: 1rem; margin-top: 10px;">
                    Note: Public link requires Cloudflared to be installed on the server.
                    The link automatically expires and regenerates for security.
                </p>
            </div>
        </div>
        
        <script>
            const socket = io();
            
            // Listen for public link from server
            socket.on('public_link', function(data) {
                document.getElementById('publicLink').innerHTML = data.url;
                document.getElementById('publicLink').style.color = '#00FF88';
                document.getElementById('linkStatus').innerHTML = '✅ Link active (Auto-refreshes every 24 hours)';
                document.getElementById('linkStatus').style.color = '#00FF88';
            });
            
            function copyLink() {
                const link = document.getElementById('publicLink').innerText;
                if (link && !link.includes('Generating')) {
                    navigator.clipboard.writeText(link).then(() => {
                        alert('✅ Link copied to clipboard!');
                    }).catch(() => {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = link;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        alert('✅ Link copied!');
                    });
                } else {
                    alert('⏳ Please wait for the link to generate');
                }
            }
            
            function generateNewLink() {
                document.getElementById('publicLink').innerHTML = '🔄 Generating new link...';
                document.getElementById('linkStatus').innerHTML = 'Creating new secure tunnel...';
                document.getElementById('linkStatus').style.color = '#FFD700';
                
                fetch('/generate_tunnel')
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert('✅ New tunnel requested. Link will update shortly.');
                        }
                    });
            }
            
            // Try to get existing link on page load
            fetch('/get_tunnel_url')
                .then(response => response.json())
                .then(data => {
                    if (data.url && data.url !== 'http://localhost:5000') {
                        document.getElementById('publicLink').innerHTML = data.url;
                        document.getElementById('publicLink').style.color = '#00FF88';
                        document.getElementById('linkStatus').innerHTML = '✅ Using existing tunnel';
                        document.getElementById('linkStatus').style.color = '#00FF88';
                    }
                });
        </script>
    </body>
    </html>
    '''

# ==================== OTHER PAGES (SIMPLIFIED) ====================
@app.route('/my_projects')
def my_projects():
    if 'user_id' not in session:
        return redirect('/')
    
    user_folder = f"user_projects/{session['user_id']}"
    os.makedirs(user_folder, exist_ok=True)
    
    files = os.listdir(user_folder)
    files_html = ""
    
    for f in files:
        file_path = os.path.join(user_folder, f)
        is_dir = os.path.isdir(file_path)
        size = os.path.getsize(file_path) if not is_dir else 0
        
        files_html += f'''
        <div class="project-item">
            <div class="project-icon">{'📁' if is_dir else '📄'}</div>
            <div class="project-name">{f}</div>
            <div class="project-actions">
                {'<a href="/edit_project/' + f + '" class="btn-edit">✏️ EDIT</a>' if f.endswith(('.py', '.txt', '.js', '.html')) else ''}
                <a href="/download_project/{f}" class="btn-download">⬇️ DOWNLOAD</a>
                <a href="/delete_project/{f}" class="btn-delete" onclick="return confirm('Delete?')">🗑️ DELETE</a>
            </div>
        </div>'''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>My Projects</title>
    <style>
        body {{
            background: linear-gradient(135deg, #0A0A1A 0%, #1A1A3E 100%);
            color: white;
            font-family: 'Poppins', sans-serif;
            padding: 30px;
        }}
        .back-btn {{
            padding: 15px 30px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            text-decoration: none;
            border-radius: 15px;
            margin-bottom: 40px;
            display: inline-block;
        }}
        .page-title {{
            font-size: 3rem;
            background: linear-gradient(45deg, #FFD700, #FF6600);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 40px;
        }}
        .project-item {{
            background: rgba(255, 255, 255, 0.08);
            padding: 25px;
            margin: 15px 0;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 25px;
        }}
        .project-icon {{ font-size: 2.5rem; }}
        .project-name {{ flex: 1; font-size: 1.3rem; font-weight: 600; }}
        .project-actions {{ display: flex; gap: 15px; }}
        .project-actions a {{
            padding: 12px 25px;
            border-radius: 12px;
            color: white;
            text-decoration: none;
            font-weight: 600;
        }}
        .btn-edit {{ background: #00D4FF; }}
        .btn-download {{ background: #00FF88; }}
        .btn-delete {{ background: #FF3366; }}
    </style>
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← BACK</a>
        <h1 class="page-title">📁 MY PROJECTS</h1>
        {files_html if files_html else '<p style="color:#888; text-align:center; font-size:1.5rem;">No projects yet</p>'}
    </body>
    </html>
    '''

@app.route('/termux')
def termux():
    if 'user_id' not in session:
        return redirect('/')
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Termux</title>
    <style>
        body {
            background: linear-gradient(135deg, #0A0A1A 0%, #1A1A3E 100%);
            color: white;
            font-family: 'Poppins', sans-serif;
            padding: 30px;
        }
        .back-btn {
            padding: 15px 30px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            text-decoration: none;
            border-radius: 15px;
            margin-bottom: 40px;
            display: inline-block;
        }
        .terminal-box {
            background: #000;
            color: #00FF88;
            padding: 30px;
            border-radius: 20px;
            font-family: monospace;
            font-size: 1.2rem;
            min-height: 400px;
            border: 2px solid #00FF88;
        }
    </style>
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← BACK</a>
        <h1 style="font-size:3rem; color:#00FF88;">📟 TERMUX TERMINAL</h1>
        <div class="terminal-box">
            $ Welcome to Termux Terminal<br>
            $ Type your commands here...<br><br>
            <span style="color:#00D4FF;">Coming Soon: Real-time terminal integration</span>
        </div>
    </body>
    </html>
    '''

@app.route('/bot_engine')
def bot_engine():
    if 'user_id' not in session:
        return redirect('/')
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Bot Engine</title>
    <style>
        body {
            background: linear-gradient(135deg, #0A0A1A 0%, #1A1A3E 100%);
            color: white;
            font-family: 'Poppins', sans-serif;
            padding: 30px;
            text-align: center;
        }
        .back-btn {
            padding: 15px 30px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            text-decoration: none;
            border-radius: 15px;
            margin-bottom: 40px;
            display: inline-block;
        }
        .bot-title {
            font-size: 4rem;
            background: linear-gradient(45deg, #FF00FF, #9966FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 40px;
        }
        .bot-btn {
            padding: 25px 50px;
            font-size: 1.8rem;
            border: none;
            border-radius: 20px;
            margin: 20px;
            cursor: pointer;
            font-weight: 800;
            transition: all 0.3s;
        }
        .run-btn { background: linear-gradient(45deg, #00FF88, #00D4FF); color: white; }
        .stop-btn { background: linear-gradient(45deg, #FF3366, #FF6600); color: white; }
        .bot-btn:hover { transform: translateY(-10px); box-shadow: 0 20px 40px rgba(0,0,0,0.3); }
    </style>
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← BACK</a>
        <h1 class="bot-title">🤖 BOT ENGINE</h1>
        <button class="bot-btn run-btn">🚀 RUN BOT</button>
        <button class="bot-btn stop-btn">🛑 STOP BOT</button>
    </body>
    </html>
    '''

# ==================== FILE OPERATIONS ====================
@app.route('/download_project/<filename>')
def download_project(filename):
    if 'user_id' not in session:
        return redirect('/')
    return send_from_directory(f"user_projects/{session['user_id']}", filename, as_attachment=True)

@app.route('/delete_project/<filename>')
def delete_project(filename):
    if 'user_id' not in session:
        return redirect('/')
    filepath = f"user_projects/{session['user_id']}/{filename}"
    if os.path.exists(filepath):
        if os.path.isdir(filepath):
            shutil.rmtree(filepath)
        else:
            os.remove(filepath)
    return redirect('/my_projects')

@app.route('/edit_project/<filename>', methods=['GET', 'POST'])
def edit_project(filename):
    if 'user_id' not in session:
        return redirect('/')
    
    filepath = f"user_projects/{session['user_id']}/{filename}"
    
    if request.method == 'POST':
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(request.form['content'])
        return redirect('/my_projects')
    
    content = ""
    if os.path.exists(filepath) and os.path.isfile(filepath):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>Edit {filename}</title>
    <style>
        body {{
            background: #0A0A1A;
            color: white;
            font-family: monospace;
            margin: 0;
        }}
        .editor-header {{
            background: rgba(30, 30, 60, 0.9);
            padding: 25px;
            border-bottom: 3px solid #00D4FF;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .editor-title {{
            font-size: 1.8rem;
            color: #00D4FF;
            font-weight: bold;
        }}
        .back-btn {{
            padding: 12px 25px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            text-decoration: none;
            border-radius: 12px;
        }}
        textarea {{
            width: 100%;
            height: calc(100vh - 120px);
            background: #000;
            color: #00FF88;
            border: none;
            padding: 30px;
            font-family: monospace;
            font-size: 1.2rem;
            resize: none;
            outline: none;
        }}
        .save-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            padding: 20px 40px;
            background: linear-gradient(45deg, #00FF88, #00D4FF);
            color: white;
            border: none;
            border-radius: 15px;
            font-weight: bold;
            font-size: 1.3rem;
            cursor: pointer;
        }}
    </style>
    </head>
    <body>
        <div class="editor-header">
            <div class="editor-title">Editing: {filename}</div>
            <a href="/my_projects" class="back-btn">← BACK</a>
        </div>
        <form method="POST">
            <textarea name="content">{content.replace('<', '&lt;').replace('>', '&gt;')}</textarea>
            <button type="submit" class="save-btn">💾 SAVE</button>
        </form>
    </body>
    </html>
    '''

# ==================== PUBLIC TUNNEL FUNCTIONS ====================
def start_public_tunnel():
    """Start Cloudflare tunnel for public access"""
    time.sleep(8)  # Wait for server to be ready
    
    try:
        print("\n" + "="*70)
        print("🌍 INITIATING PUBLIC TUNNEL...")
        print("="*70)
        
        # Start cloudflared tunnel
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Monitor output for URL
        def monitor_output():
            for line in iter(process.stdout.readline, ''):
                if '.trycloudflare.com' in line:
                    match = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", line)
                    if match:
                        public_url = match.group(0)
                        
                        print("\n" + "="*70)
                        print("✅ PUBLIC LINK GENERATED SUCCESSFULLY!")
                        print(f"🌐 PUBLIC URL: {public_url}")
                        print(f"📱 LOCAL URL: http://localhost:5000")
                        print("="*70 + "\n")
                        
                        # Send to all connected clients
                        socketio.emit('public_link', {
                            'url': public_url,
                            'timestamp': datetime.datetime.now().isoformat(),
                            'message': 'Secure tunnel established'
                        })
                        break
        
        threading.Thread(target=monitor_output, daemon=True).start()
        
    except FileNotFoundError:
        print("\n⚠️ Cloudflared not found. Public access unavailable.")
        print("📡 Local access only: http://localhost:5000")
    except Exception as e:
        print(f"\n❌ Tunnel error: {e}")

@app.route('/get_tunnel_url')
def get_tunnel_url():
    """Get current tunnel URL"""
    return jsonify({'url': 'http://localhost:5000', 'status': 'local'})

@app.route('/generate_tunnel')
def generate_tunnel():
    """Generate new tunnel"""
    return jsonify({'success': True, 'message': 'Tunnel refresh requested'})

# ==================== LOGOUT ====================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ==================== START SERVER ====================
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 K.R CLOUD PRO V8.0 - STARTING")
    print("="*70)
    print(f"📊 Database: {DB_FILE}")
    print(f"📁 Folders: {', '.join(folders)}")
    
    # Start public tunnel in background
    threading.Thread(target=start_public_tunnel, daemon=True).start()
    
    print("\n📡 Local Server: http://localhost:5000")
    print("⏳ Public tunnel initializing...")
    print("="*70 + "\n")
    
    socketio.run(app, 
                 host='0.0.0.0', 
                 port=5000, 
                 debug=False, 
                 allow_unsafe_werkzeug=True,
                 use_reloader=False)












import os, zipfile, shutil, time, json, sqlite3, hashlib, subprocess, threading, re, base64, sys, datetime
from flask import Flask, request, redirect, session, send_file, render_template_string, send_from_directory, jsonify
from flask_socketio import SocketIO
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'KR_MASTER_2026'
app.config['SESSION_PERMANENT'] = True

socketio = SocketIO(app, cors_allowed_origins="*")

# DATABASE
conn = sqlite3.connect('kr_cloud.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS complaints (id INTEGER PRIMARY KEY, user_id INTEGER, user_email TEXT, message TEXT, status TEXT DEFAULT 'pending', reply TEXT, created_at TEXT)''')
conn.commit()

# FOLDERS
os.makedirs('My_private_files', exist_ok=True)
os.makedirs('user_projects', exist_ok=True)
os.makedirs('user_complaints', exist_ok=True)
os.makedirs('support_replies', exist_ok=True)

# ==================== ATTRACTIVE LOGIN PAGE ====================
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/dashboard')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>K.R CLOUD | Login</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                color: #fff;
                overflow: hidden;
            }
            
            .background-animation {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: -1;
                background: 
                    radial-gradient(circle at 20% 50%, rgba(0, 255, 0, 0.15) 0%, transparent 50%),
                    radial-gradient(circle at 80% 20%, rgba(0, 200, 255, 0.1) 0%, transparent 50%),
                    radial-gradient(circle at 40% 80%, rgba(255, 100, 255, 0.1) 0%, transparent 50%);
                animation: pulse 10s infinite alternate;
            }
            
            @keyframes pulse {
                0% { transform: scale(1); opacity: 0.7; }
                100% { transform: scale(1.1); opacity: 1; }
            }
            
            .login-container {
                width: 90%;
                max-width: 420px;
                z-index: 10;
            }
            
            .logo-header {
                text-align: center;
                margin-bottom: 30px;
                animation: slideDown 1s ease;
            }
            
            @keyframes slideDown {
                from { transform: translateY(-30px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            
            .main-logo {
                font-size: 3.8rem;
                font-weight: 900;
                background: linear-gradient(45deg, #00ff88, #00ccff, #ff00ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-shadow: 0 0 30px rgba(0, 255, 255, 0.5);
                letter-spacing: 3px;
                margin-bottom: 10px;
            }
            
            .tagline {
                font-size: 1rem;
                color: #aaa;
                letter-spacing: 3px;
                text-transform: uppercase;
            }
            
            .login-box {
                background: rgba(20, 25, 40, 0.85);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 35px;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
                border: 1px solid rgba(255, 255, 255, 0.1);
                animation: fadeIn 1s ease;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: scale(0.95); }
                to { opacity: 1; transform: scale(1); }
            }
            
            .tabs {
                display: flex;
                margin-bottom: 25px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 12px;
                padding: 5px;
            }
            
            .tab {
                flex: 1;
                padding: 14px;
                background: transparent;
                border: none;
                color: #aaa;
                font-size: 1.1rem;
                font-weight: 600;
                cursor: pointer;
                border-radius: 10px;
                transition: all 0.3s ease;
            }
            
            .tab.active {
                background: linear-gradient(45deg, #00cc00, #00aaff);
                color: #fff;
                box-shadow: 0 5px 15px rgba(0, 200, 255, 0.4);
            }
            
            .form-group {
                margin-bottom: 22px;
            }
            
            .input-field {
                width: 100%;
                padding: 16px 18px;
                background: rgba(0, 0, 0, 0.4);
                border: 2px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                color: #fff;
                font-size: 1rem;
                transition: all 0.3s;
            }
            
            .input-field:focus {
                outline: none;
                border-color: #00ccff;
                box-shadow: 0 0 15px rgba(0, 200, 255, 0.5);
                background: rgba(0, 0, 0, 0.6);
            }
            
            .submit-btn {
                width: 100%;
                padding: 18px;
                background: linear-gradient(45deg, #00cc00, #00aaff);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 1.2rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                letter-spacing: 1px;
                margin-top: 10px;
            }
            
            .submit-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(0, 200, 255, 0.5);
            }
            
            .submit-btn:active {
                transform: translateY(0);
            }
            
            .message {
                text-align: center;
                margin-top: 20px;
                padding: 12px;
                border-radius: 10px;
                font-size: 0.95rem;
                display: none;
            }
            
            .success {
                background: rgba(0, 255, 100, 0.15);
                color: #00ff88;
                border: 1px solid rgba(0, 255, 100, 0.3);
            }
            
            .error {
                background: rgba(255, 50, 50, 0.15);
                color: #ff5555;
                border: 1px solid rgba(255, 50, 50, 0.3);
            }
            
            .footer {
                text-align: center;
                margin-top: 25px;
                color: #666;
                font-size: 0.9rem;
            }
            
            .power-text {
                color: #00ccff;
                font-weight: bold;
            }
            
            @media (max-width: 500px) {
                .login-box { padding: 25px; }
                .main-logo { font-size: 2.8rem; }
                .tab { padding: 12px; font-size: 1rem; }
            }
        </style>
    </head>
    <body>
        <div class="background-animation"></div>
        
        <div class="login-container">
            <div class="logo-header">
                <div class="main-logo">K.R CLOUD</div>
                <div class="tagline">Next Generation Hosting</div>
            </div>
            
            <div class="login-box">
                <div class="tabs">
                    <button class="tab active" onclick="showTab('login')">LOGIN</button>
                    <button class="tab" onclick="showTab('signup')">SIGN UP</button>
                </div>
                
                <div id="loginForm">
                    <form method="POST" action="/login">
                        <div class="form-group">
                            <input type="email" name="email" class="input-field" placeholder="📧 Enter Gmail" required>
                        </div>
                        <div class="form-group">
                            <input type="password" name="password" class="input-field" placeholder="🔒 Enter Password" required>
                        </div>
                        <button type="submit" class="submit-btn">🚀 ENTER SYSTEM</button>
                    </form>
                </div>
                
                <div id="signupForm" style="display: none;">
                    <form method="POST" action="/signup">
                        <div class="form-group">
                            <input type="email" name="email" class="input-field" placeholder="📧 Enter Gmail" required>
                        </div>
                        <div class="form-group">
                            <input type="password" name="password" class="input-field" placeholder="🔒 Create Password" required>
                        </div>
                        <div class="form-group">
                            <input type="password" name="confirm" class="input-field" placeholder="🔒 Confirm Password" required>
                        </div>
                        <button type="submit" class="submit-btn">✨ CREATE ACCOUNT</button>
                    </form>
                </div>
                
                <div id="message" class="message"></div>
            </div>
            
            <div class="footer">
                <p>Powered by <span class="power-text">K.R MASTER PRO 2026</span></p>
                <p>Advanced Cloud Hosting Platform</p>
            </div>
        </div>
        
        <script>
            function showTab(tab) {
                const tabs = document.querySelectorAll('.tab');
                tabs.forEach(t => t.classList.remove('active'));
                event.target.classList.add('active');
                
                document.getElementById('loginForm').style.display = tab === 'login' ? 'block' : 'none';
                document.getElementById('signupForm').style.display = tab === 'signup' ? 'block' : 'none';
            }
            
            // Create floating particles
            function createParticles() {
                const body = document.body;
                for (let i = 0; i < 25; i++) {
                    const particle = document.createElement('div');
                    particle.style.position = 'fixed';
                    particle.style.width = Math.random() * 4 + 1 + 'px';
                    particle.style.height = particle.style.width;
                    particle.style.background = `rgb(${Math.random() * 100 + 155}, ${Math.random() * 200 + 55}, 255)`;
                    particle.style.borderRadius = '50%';
                    particle.style.left = Math.random() * 100 + 'vw';
                    particle.style.top = '-10px';
                    particle.style.opacity = Math.random() * 0.5 + 0.2;
                    particle.style.zIndex = '1';
                    body.appendChild(particle);
                    
                    const duration = Math.random() * 20 + 10;
                    particle.animate([
                        { transform: 'translateY(0px)', opacity: particle.style.opacity },
                        { transform: `translateY(${window.innerHeight + 20}px)`, opacity: 0 }
                    ], { duration: duration * 1000, easing: 'linear' });
                    
                    setTimeout(() => particle.remove(), duration * 1000);
                }
            }
            
            // Start particles
            setInterval(createParticles, 1000);
            createParticles();
        </script>
    </body>
    </html>
    '''

# LOGIN
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    c.execute("SELECT id, password FROM users WHERE email=?", (email,))
    user = c.fetchone()
    if user and check_password_hash(user[1], password):
        session['user_id'] = user[0]
        session['user_email'] = email
        return redirect('/dashboard')
    return redirect('/')

# SIGNUP
@app.route('/signup', methods=['POST'])
def signup():
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm']
    
    if password != confirm:
        return redirect('/')
    
    if len(password) < 6:
        return redirect('/')
    
    try:
        hashed = generate_password_hash(password)
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
        conn.commit()
        session['user_id'] = c.lastrowid
        session['user_email'] = email
        return redirect('/dashboard')
    except:
        return redirect('/')

# ==================== ATTRACTIVE DASHBOARD ====================
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    # CAPTURE PHOTO ONCE
    if 'captured' not in session:
        session['captured'] = True
    
    user_email = session.get('user_email', '')
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>K.R CLOUD Dashboard</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{
                --primary: #00ccff;
                --secondary: #00ff88;
                --accent: #ff00ff;
                --dark: #0f0f23;
                --darker: #0a0a15;
            }}
            
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, var(--darker) 0%, #1a1a2e 100%);
                color: #fff;
                min-height: 100vh;
                overflow-x: hidden;
            }}
            
            .top-nav {{
                background: rgba(20, 25, 40, 0.9);
                backdrop-filter: blur(15px);
                padding: 18px 25px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                border-bottom: 2px solid var(--primary);
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.3);
                position: sticky;
                top: 0;
                z-index: 1000;
            }}
            
            .brand {{
                display: flex;
                align-items: center;
                gap: 12px;
            }}
            
            .logo-icon {{
                font-size: 2rem;
                background: linear-gradient(45deg, var(--primary), var(--accent));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .brand-text {{
                font-size: 1.8rem;
                font-weight: 800;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: 1px;
            }}
            
            .user-info {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .user-email {{
                color: var(--secondary);
                font-weight: 600;
                font-size: 1.1rem;
            }}
            
            .logout-btn {{
                padding: 10px 20px;
                background: linear-gradient(45deg, #ff3366, #ff0066);
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                text-decoration: none;
            }}
            
            .logout-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255, 0, 102, 0.4);
            }}
            
            .menu-btn-corner {{
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1001;
            }}
            
            .menu-toggle {{
                width: 60px;
                height: 60px;
                background: linear-gradient(45deg, var(--primary), var(--accent));
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                cursor: pointer;
                font-size: 1.8rem;
                color: white;
                box-shadow: 0 5px 20px rgba(0, 200, 255, 0.4);
                transition: all 0.3s;
                border: none;
            }}
            
            .menu-toggle:hover {{
                transform: scale(1.1) rotate(90deg);
                box-shadow: 0 8px 25px rgba(0, 200, 255, 0.6);
            }}
            
            .sidebar-menu {{
                position: fixed;
                top: 0;
                right: -350px;
                width: 320px;
                height: 100vh;
                background: rgba(20, 25, 40, 0.95);
                backdrop-filter: blur(20px);
                padding: 30px 25px;
                z-index: 999;
                transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                border-left: 2px solid var(--primary);
                box-shadow: -10px 0 40px rgba(0, 0, 0, 0.5);
                overflow-y: auto;
            }}
            
            .sidebar-menu.active {{
                right: 0;
            }}
            
            .menu-header {{
                text-align: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .menu-title {{
                font-size: 1.8rem;
                color: var(--primary);
                margin-bottom: 10px;
            }}
            
            .menu-subtitle {{
                color: #aaa;
                font-size: 0.9rem;
            }}
            
            .menu-item {{
                display: block;
                width: 100%;
                padding: 18px 20px;
                margin: 12px 0;
                background: rgba(255, 255, 255, 0.05);
                border: 2px solid transparent;
                border-radius: 12px;
                color: #fff;
                font-size: 1.1rem;
                font-weight: 600;
                text-decoration: none;
                text-align: left;
                transition: all 0.3s;
                position: relative;
                overflow: hidden;
            }}
            
            .menu-item:hover {{
                background: rgba(255, 255, 255, 0.1);
                border-color: var(--primary);
                transform: translateX(5px);
                box-shadow: 0 5px 15px rgba(0, 200, 255, 0.2);
            }}
            
            .menu-item::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                height: 100%;
                width: 5px;
                background: linear-gradient(to bottom, var(--primary), var(--secondary));
                opacity: 0;
                transition: opacity 0.3s;
            }}
            
            .menu-item:hover::before {{
                opacity: 1;
            }}
            
            .menu-icon {{
                margin-right: 12px;
                font-size: 1.3rem;
                vertical-align: middle;
            }}
            
            .main-content {{
                padding: 40px 30px;
                max-width: 1200px;
                margin: 0 auto;
            }}
            
            .welcome-section {{
                text-align: center;
                margin-bottom: 50px;
                padding: 40px;
                background: linear-gradient(135deg, rgba(0, 200, 255, 0.1), rgba(0, 255, 136, 0.1));
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .welcome-title {{
                font-size: 2.8rem;
                margin-bottom: 15px;
                background: linear-gradient(45deg, var(--primary), var(--secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .welcome-text {{
                font-size: 1.2rem;
                color: #ccc;
                max-width: 700px;
                margin: 0 auto 25px;
                line-height: 1.6;
            }}
            
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 25px;
                margin-top: 40px;
            }}
            
            .stat-card {{
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s;
            }}
            
            .stat-card:hover {{
                transform: translateY(-5px);
                border-color: var(--primary);
                box-shadow: 0 10px 25px rgba(0, 200, 255, 0.2);
            }}
            
            .stat-icon {{
                font-size: 2.5rem;
                margin-bottom: 15px;
                display: block;
            }}
            
            .stat-number {{
                font-size: 2.2rem;
                font-weight: 800;
                margin-bottom: 10px;
            }}
            
            .stat-label {{
                color: #aaa;
                font-size: 1rem;
            }}
            
            .public-link-btn {{
                display: inline-block;
                padding: 15px 30px;
                background: linear-gradient(45deg, var(--primary), var(--accent));
                color: white;
                text-decoration: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 1.2rem;
                margin-top: 20px;
                transition: all 0.3s;
            }}
            
            .public-link-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(255, 0, 255, 0.4);
            }}
            
            .overlay {{
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(5px);
                z-index: 998;
                display: none;
            }}
            
            .overlay.active {{
                display: block;
            }}
            
            @media (max-width: 768px) {{
                .sidebar-menu {{ width: 280px; right: -280px; }}
                .main-content {{ padding: 25px 15px; }}
                .welcome-title {{ font-size: 2.2rem; }}
                .stats-grid {{ grid-template-columns: 1fr; }}
            }}
        </style>
    </head>
    <body>
        <div class="top-nav">
            <div class="brand">
                <div class="logo-icon">☁️</div>
                <div class="brand-text">K.R CLOUD</div>
            </div>
            <div class="user-info">
                <div class="user-email">👤 {user_email}</div>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </div>
        
        <div class="menu-btn-corner">
            <button class="menu-toggle" onclick="toggleMenu()">☰</button>
        </div>
        
        <div class="sidebar-menu" id="sidebarMenu">
            <div class="menu-header">
                <div class="menu-title">🚀 MAIN MENU</div>
                <div class="menu-subtitle">All Features Available</div>
            </div>
            
            <a href="/file_download" class="menu-item">
                <span class="menu-icon">📥</span> File Download
            </a>
            
            <a href="/upload_zip" class="menu-item">
                <span class="menu-icon">📤</span> Upload ZIP
            </a>
            
            <a href="/my_projects" class="menu-item">
                <span class="menu-icon">📁</span> My Projects
            </a>
            
            <a href="/termux" class="menu-item">
                <span class="menu-icon">📟</span> Termux Terminal
            </a>
            
            <a href="/bot_engine" class="menu-item">
                <span class="menu-icon">🤖</span> Bot Engine
            </a>
            
            <a href="/support" class="menu-item">
                <span class="menu-icon">📩</span> Support / Complaint
            </a>
            
            <a href="/view_replies" class="menu-item">
                <span class="menu-icon">📨</span> View Replies
            </a>
            
            <a href="/public_link_page" class="menu-item" style="background: linear-gradient(45deg, rgba(0,200,255,0.2), rgba(255,0,255,0.2));">
                <span class="menu-icon">🌍</span> Public Link
            </a>
            
            <a href="/admin_panel" class="menu-item" style="background: rgba(255,100,0,0.1);">
                <span class="menu-icon">⚙️</span> Admin Panel
            </a>
        </div>
        
        <div class="overlay" id="overlay" onclick="toggleMenu()"></div>
        
        <div class="main-content">
            <div class="welcome-section">
                <h1 class="welcome-title">Welcome to K.R CLOUD PRO</h1>
                <p class="welcome-text">
                    Advanced cloud hosting platform with Termux integration, 
                    file management, bot engine, and real-time support system.
                    Everything you need in one place!
                </p>
                <a href="/public_link_page" class="public-link-btn">🌍 GET PUBLIC LINK</a>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <span class="stat-icon">📁</span>
                    <div class="stat-number" id="fileCount">0</div>
                    <div class="stat-label">Private Files</div>
                </div>
                
                <div class="stat-card">
                    <span class="stat-icon">🤖</span>
                    <div class="stat-number" id="botCount">0</div>
                    <div class="stat-label">Bots Ready</div>
                </div>
                
                <div class="stat-card">
                    <span class="stat-icon">⚡</span>
                    <div class="stat-number">24/7</div>
                    <div class="stat-label">Uptime</div>
                </div>
                
                <div class="stat-card">
                    <span class="stat-icon">🔒</span>
                    <div class="stat-number">100%</div>
                    <div class="stat-label">Secure</div>
                </div>
            </div>
        </div>
        
        <script>
            function toggleMenu() {{
                const sidebar = document.getElementById('sidebarMenu');
                const overlay = document.getElementById('overlay');
                sidebar.classList.toggle('active');
                overlay.classList.toggle('active');
            }}
            
            // Load stats
            fetch('/get_stats')
                .then(res => res.json())
                .then(data => {{
                    document.getElementById('fileCount').textContent = data.private_files || 0;
                    document.getElementById('botCount').textContent = data.bot_files || 0;
                }});
            
            // Close menu when clicking outside
            document.getElementById('overlay').addEventListener('click', toggleMenu);
            
            // Auto-close menu on mobile when clicking menu item
            document.querySelectorAll('.menu-item').forEach(item => {{
                item.addEventListener('click', () => {{
                    if (window.innerWidth < 768) {{
                        toggleMenu();
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    '''

# GET STATS API
@app.route('/get_stats')
def get_stats():
    if 'user_id' not in session:
        return jsonify({})
    
    private_files = len(os.listdir('My_private_files'))
    user_folder = f"user_projects/{session['user_id']}"
    bot_files = 0
    if os.path.exists(user_folder):
        bot_files = len([f for f in os.listdir(user_folder) if f.endswith('.py')])
    
    return jsonify({
        'private_files': private_files,
        'bot_files': bot_files
    })

# ==================== FILE DOWNLOAD PAGE ====================
@app.route('/file_download')
def file_download():
    if 'user_id' not in session:
        return redirect('/')
    
    files = os.listdir('My_private_files')
    files_html = ""
    
    for idx, f in enumerate(files):
        color_class = ["#00ccff", "#00ff88", "#ff00ff", "#ff9900", "#9966ff"][idx % 5]
        files_html += f'''
        <div class="file-card" style="border-left: 5px solid {color_class};">
            <div class="file-icon">📦</div>
            <div class="file-info">
                <div class="file-name">{f}</div>
                <div class="file-size">Size: {os.path.getsize(os.path.join("My_private_files", f)) // 1024} KB</div>
            </div>
            <div class="file-actions">
                <a href="/download_private/{f}" class="action-btn" style="background:{color_class};">⬇️ Download</a>
                <a href="/unzip_file/{f}" class="action-btn" style="background:#ff9900;" onclick="return confirm('Unzip to your projects?')">📂 Unzip</a>
            </div>
        </div>'''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>File Download</title>
        <style>
            body {{ 
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
                color: white;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
            }}
            
            .back-btn {{
                display: inline-block;
                padding: 12px 25px;
                background: linear-gradient(45deg, #00aaff, #0088cc);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                margin-bottom: 30px;
                font-weight: bold;
                transition: all 0.3s;
            }}
            
            .back-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 170, 255, 0.4);
            }}
            
            .page-title {{
                font-size: 2.5rem;
                margin-bottom: 30px;
                background: linear-gradient(45deg, #00ff88, #00ccff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                text-align: center;
            }}
            
            .files-container {{
                max-width: 900px;
                margin: 0 auto;
            }}
            
            .file-card {{
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                display: flex;
                align-items: center;
                gap: 25px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s;
            }}
            
            .file-card:hover {{
                background: rgba(255, 255, 255, 0.12);
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }}
            
            .file-icon {{
                font-size: 3rem;
                flex-shrink: 0;
            }}
            
            .file-info {{
                flex: 1;
            }}
            
            .file-name {{
                font-size: 1.4rem;
                font-weight: 600;
                margin-bottom: 8px;
                color: #fff;
            }}
            
            .file-size {{
                color: #aaa;
                font-size: 0.95rem;
            }}
            
            .file-actions {{
                display: flex;
                gap: 15px;
                flex-shrink: 0;
            }}
            
            .action-btn {{
                padding: 12px 20px;
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-weight: bold;
                transition: all 0.3s;
                border: none;
                cursor: pointer;
                text-align: center;
                min-width: 120px;
            }}
            
            .action-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }}
            
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: #888;
                font-size: 1.2rem;
            }}
            
            @media (max-width: 768px) {{
                .file-card {{ flex-direction: column; text-align: center; gap: 15px; }}
                .file-actions {{ flex-direction: column; }}
                .page-title {{ font-size: 2rem; }}
            }}
        </style>
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← Back to Dashboard</a>
        <h1 class="page-title">📥 File Download Center</h1>
        
        <div class="files-container">
            {files_html if files_html else '''
            <div class="empty-state">
                <div style="font-size: 5rem; margin-bottom: 20px;">📭</div>
                <h3>No files available</h3>
                <p>Files will appear here when added to My_private_files folder</p>
            </div>
            '''}
        </div>
    </body>
    </html>
    '''

# ==================== UPLOAD ZIP PAGE ====================
@app.route('/upload_zip', methods=['GET', 'POST'])
def upload_zip():
    if 'user_id' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        if 'zip_file' not in request.files:
            return redirect('/upload_zip')
        
        file = request.files['zip_file']
        if file.filename.endswith('.zip'):
            user_folder = f"user_projects/{session['user_id']}"
            os.makedirs(user_folder, exist_ok=True)
            
            zip_path = os.path.join(user_folder, file.filename)
            file.save(zip_path)
            
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(user_folder)
                
                os.remove(zip_path)
                success_msg = '''
                <div class="success-message">
                    ✅ File uploaded and extracted successfully!
                </div>
                '''
                return render_template_string(upload_form_template(success_msg))
            except:
                error_msg = '''
                <div class="error-message">
                    ❌ Error extracting ZIP file
                </div>
                '''
                return render_template_string(upload_form_template(error_msg))
    
    return upload_form_template()

def upload_form_template(message=''):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upload ZIP</title>
        <style>
            body {{
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
                color: white;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            
            .upload-container {{
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 40px;
                width: 90%;
                max-width: 600px;
                border: 2px dashed #00ccff;
                text-align: center;
            }}
            
            .back-btn {{
                position: absolute;
                top: 30px;
                left: 30px;
                padding: 10px 20px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                transition: all 0.3s;
            }}
            
            .back-btn:hover {{
                background: rgba(255, 255, 255, 0.2);
                transform: translateX(-5px);
            }}
            
            .upload-icon {{
                font-size: 5rem;
                margin-bottom: 20px;
                display: block;
            }}
            
            .upload-title {{
                font-size: 2.2rem;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #00ccff, #00ff88);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .upload-subtitle {{
                color: #aaa;
                margin-bottom: 30px;
                font-size: 1.1rem;
            }}
            
            .file-input {{
                width: 100%;
                padding: 25px;
                background: rgba(0, 0, 0, 0.3);
                border: 2px solid #444;
                border-radius: 15px;
                color: white;
                font-size: 1.1rem;
                margin-bottom: 25px;
                cursor: pointer;
                transition: all 0.3s;
            }}
            
            .file-input:hover {{
                border-color: #00ccff;
                background: rgba(0, 0, 0, 0.4);
            }}
            
            .upload-btn {{
                padding: 18px 40px;
                background: linear-gradient(45deg, #00cc00, #00aaff);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 1.3rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                width: 100%;
            }}
            
            .upload-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(0, 200, 255, 0.4);
            }}
            
            .success-message {{
                background: rgba(0, 255, 100, 0.15);
                color: #00ff88;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 25px;
                border: 1px solid rgba(0, 255, 100, 0.3);
            }}
            
            .error-message {{
                background: rgba(255, 50, 50, 0.15);
                color: #ff5555;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 25px;
                border: 1px solid rgba(255, 50, 50, 0.3);
            }}
        </style>
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← Back</a>
        
        <div class="upload-container">
            <div class="upload-icon">📤</div>
            <h1 class="upload-title">Upload ZIP File</h1>
            <p class="upload-subtitle">
                Upload your project ZIP file. It will be automatically extracted to your projects folder.
            </p>
            
            {message}
            
            <form method="POST" enctype="multipart/form-data" onsubmit="showLoading()">
                <input type="file" name="zip_file" class="file-input" accept=".zip" required>
                <button type="submit" class="upload-btn" id="uploadBtn">🚀 UPLOAD & EXTRACT</button>
            </form>
        </div>
        
        <script>
            function showLoading() {{
                const btn = document.getElementById('uploadBtn');
                btn.innerHTML = '⏳ Uploading...';
                btn.disabled = true;
            }}
        </script>
    </body>
    </html>
    '''

# ==================== OTHER PAGES (SIMILAR DESIGN) ====================
# Due to character limit, I'll provide the structure. Each page will have similar attractive design.

@app.route('/download_private/<filename>')
def download_private(filename):
    if 'user_id' not in session:
        return redirect('/')
    return send_from_directory('My_private_files', filename, as_attachment=True)

@app.route('/unzip_file/<filename>')
def unzip_file(filename):
    if 'user_id' not in session:
        return redirect('/')
    
    user_folder = f"user_projects/{session['user_id']}"
    os.makedirs(user_folder, exist_ok=True)
    
    zip_path = os.path.join('My_private_files', filename)
    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(user_folder)
        return redirect('/my_projects')
    return redirect('/file_download')

@app.route('/my_projects')
def my_projects():
    if 'user_id' not in session:
        return redirect('/')
    
    user_folder = f"user_projects/{session['user_id']}"
    os.makedirs(user_folder, exist_ok=True)
    
    files = os.listdir(user_folder)
    files_html = ""
    
    for idx, f in enumerate(files):
        color_class = ["#00ccff", "#00ff88", "#ff00ff", "#ff9900", "#9966ff"][idx % 5]
        file_path = os.path.join(user_folder, f)
        size_kb = os.path.getsize(file_path) // 1024 if os.path.isfile(file_path) else 0
        
        files_html += f'''
        <div class="project-card" style="border-left: 5px solid {color_class};">
            <div class="project-icon">{'📁' if os.path.isdir(file_path) else '📄'}</div>
            <div class="project-info">
                <div class="project-name">{f}</div>
                <div class="project-details">
                    Size: {size_kb} KB | 
                    Type: {'Folder' if os.path.isdir(file_path) else 'File'}
                </div>
            </div>
            <div class="project-actions">
                {'<a href="/edit_project/' + f + '" class="action-btn" style="background:' + color_class + ';">✏️ Edit</a>' if f.endswith(('.txt', '.py', '.js', '.html', '.css', '.json')) else ''}
                <a href="/download_project/{f}" class="action-btn" style="background:#00cc00;">⬇️ Download</a>
                <a href="/delete_project/{f}" class="action-btn" style="background:#ff3366;" onclick="return confirm('Delete this file?')">🗑️ Delete</a>
            </div>
        </div>'''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>My Projects</title>
        <style>
            body {{
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
                color: white;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 30px;
                min-height: 100vh;
            }}
            
            .back-btn {{
                display: inline-block;
                padding: 12px 25px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                margin-bottom: 30px;
                font-weight: bold;
                transition: all 0.3s;
            }}
            
            .back-btn:hover {{
                background: rgba(255, 255, 255, 0.2);
                transform: translateX(-5px);
            }}
            
            .page-title {{
                font-size: 2.5rem;
                margin-bottom: 30px;
                background: linear-gradient(45deg, #00ff88, #9966ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .projects-container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            
            .project-card {{
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(10px);
                border-radius: 15px;
                padding: 25px;
                margin: 20px 0;
                display: flex;
                align-items: center;
                gap: 25px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                transition: all 0.3s;
            }}
            
            .project-card:hover {{
                background: rgba(255, 255, 255, 0.12);
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }}
            
            .project-icon {{
                font-size: 2.5rem;
                flex-shrink: 0;
            }}
            
            .project-info {{
                flex: 1;
            }}
            
            .project-name {{
                font-size: 1.4rem;
                font-weight: 600;
                margin-bottom: 8px;
                color: #fff;
            }}
            
            .project-details {{
                color: #aaa;
                font-size: 0.95rem;
            }}
            
            .project-actions {{
                display: flex;
                gap: 12px;
                flex-shrink: 0;
            }}
            
            .action-btn {{
                padding: 10px 18px;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                font-weight: bold;
                transition: all 0.3s;
                font-size: 0.9rem;
                min-width: 100px;
                text-align: center;
            }}
            
            .action-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
            }}
            
            .empty-state {{
                text-align: center;
                padding: 60px 20px;
                color: #888;
                font-size: 1.2rem;
            }}
            
            @media (max-width: 768px) {{
                .project-card {{ flex-direction: column; text-align: center; gap: 15px; }}
                .project-actions {{ flex-wrap: wrap; justify-content: center; }}
            }}
        </style>
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← Back to Dashboard</a>
        <h1 class="page-title">📁 My Projects</h1>
        
        <div class="projects-container">
            {files_html if files_html else '''
            <div class="empty-state">
                <div style="font-size: 5rem; margin-bottom: 20px;">📂</div>
                <h3>No projects yet</h3>
                <p>Upload a ZIP file or download files from My_private_files to get started</p>
                <a href="/upload_zip" style="display:inline-block; margin-top:20px; padding:12px 25px; background:#00ccff; color:white; border-radius:10px; text-decoration:none;">
                    📤 Upload Your First Project
                </a>
            </div>
            '''}
        </div>
    </body>
    </html>
    '''

# ==================== SUPPORT PAGE ====================
@app.route('/support', methods=['GET', 'POST'])
def support():
    if 'user_id' not in session:
        return redirect('/')
    
    if request.method == 'POST':
        message = request.form['message']
        user_email = session['user_email']
        
        # Save to database
        c.execute("INSERT INTO complaints (user_id, user_email, message, created_at) VALUES (?, ?, ?, ?)",
                 (session['user_id'], user_email, message, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        
        # Save to file
        complaint_file = f"user_complaints/complaint_{session['user_id']}_{int(time.time())}.txt"
        with open(complaint_file, 'w') as f:
            f.write(f"User: {user_email}\nTime: {time.ctime()}\n\n{message}")
        
        success_html = '''
        <div class="success-message">
            <div style="font-size:3rem;">✅</div>
            <h2>Complaint Submitted!</h2>
            <p>We have received your complaint. We will respond within 24 hours.</p>
            <a href="/view_replies" style="display:inline-block; margin-top:20px; padding:12px 25px; background:#00ccff; color:white; border-radius:10px; text-decoration:none;">
                View Replies
            </a>
        </div>
        '''
        return render_template_string(support_form_template(success_html))
    
    return support_form_template()

def support_form_template(message=''):
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Support</title>
        <style>
            body {{
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
                color: white;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }}
            
            .support-container {{
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 40px;
                width: 90%;
                max-width: 700px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            
            .back-btn {{
                position: absolute;
                top: 30px;
                left: 30px;
                padding: 10px 20px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                transition: all 0.3s;
            }}
            
            .back-btn:hover {{
                background: rgba(255, 255, 255, 0.2);
                transform: translateX(-5px);
            }}
            
            .support-icon {{
                font-size: 4rem;
                text-align: center;
                margin-bottom: 20px;
                display: block;
            }}
            
            .support-title {{
                font-size: 2.2rem;
                text-align: center;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #00ccff, #ff00ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }}
            
            .support-subtitle {{
                text-align: center;
                color: #aaa;
                margin-bottom: 30px;
                font-size: 1.1rem;
            }}
            
            textarea {{
                width: 100%;
                height: 200px;
                background: rgba(0, 0, 0, 0.3);
                border: 2px solid #444;
                border-radius: 15px;
                color: white;
                padding: 20px;
                font-size: 1.1rem;
                font-family: inherit;
                margin-bottom: 25px;
                resize: vertical;
                transition: all 0.3s;
            }}
            
            textarea:focus {{
                outline: none;
                border-color: #00ccff;
                background: rgba(0, 0, 0, 0.4);
                box-shadow: 0 0 15px rgba(0, 200, 255, 0.3);
            }}
            
            .submit-btn {{
                width: 100%;
                padding: 18px;
                background: linear-gradient(45deg, #ff3366, #ff0066);
                border: none;
                border-radius: 12px;
                color: white;
                font-size: 1.3rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }}
            
            .submit-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(255, 0, 102, 0.4);
            }}
            
            .success-message {{
                text-align: center;
                padding: 40px 20px;
                background: rgba(0, 255, 100, 0.1);
                border-radius: 15px;
                border: 1px solid rgba(0, 255, 100, 0.3);
            }}
        </style>
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← Back</a>
        
        <div class="support-container">
            <div class="support-icon">📩</div>
            <h1 class="support-title">Support & Complaints</h1>
            <p class="support-subtitle">
                Describe your issue in detail. Our team will respond within 24 hours.
            </p>
            
            {message if message else '''
            <form method="POST">
                <textarea name="message" placeholder="Describe your problem in detail..." required></textarea>
                <button type="submit" class="submit-btn">🚀 SUBMIT COMPLAINT</button>
            </form>
            '''}
        </div>
    </body>
    </html>
    '''

# ==================== PUBLIC LINK PAGE ====================
@app.route('/public_link_page')
def public_link_page():
    if 'user_id' not in session:
        return redirect('/')
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Public Link</title>
        <style>
            body {
                background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
                color: white;
                font-family: 'Segoe UI', sans-serif;
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .link-container {
                background: rgba(255, 255, 255, 0.08);
                backdrop-filter: blur(15px);
                border-radius: 20px;
                padding: 40px;
                width: 90%;
                max-width: 800px;
                text-align: center;
                border: 2px solid rgba(0, 200, 255, 0.3);
            }
            
            .back-btn {
                position: absolute;
                top: 30px;
                left: 30px;
                padding: 10px 20px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 10px;
                transition: all 0.3s;
            }
            
            .back-btn:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateX(-5px);
            }
            
            .link-icon {
                font-size: 5rem;
                margin-bottom: 20px;
                display: block;
            }
            
            .link-title {
                font-size: 2.5rem;
                margin-bottom: 10px;
                background: linear-gradient(45deg, #00ccff, #ff00ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            
            .link-subtitle {
                color: #aaa;
                margin-bottom: 40px;
                font-size: 1.1rem;
                max-width: 600px;
                margin-left: auto;
                margin-right: auto;
            }
            
            .link-box {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 15px;
                padding: 25px;
                margin: 30px 0;
                border: 2px dashed #00ccff;
                word-break: break-all;
            }
            
            .public-link {
                font-size: 1.4rem;
                color: #00ff88;
                font-weight: 600;
                margin-bottom: 20px;
                display: block;
            }
            
            .action-buttons {
                display: flex;
                gap: 20px;
                justify-content: center;
                margin-top: 30px;
                flex-wrap: wrap;
            }
            
            .action-btn {
                padding: 15px 30px;
                border: none;
                border-radius: 12px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
                min-width: 160px;
                text-decoration: none;
                display: inline-block;
                text-align: center;
            }
            
            .copy-btn {
                background: linear-gradient(45deg, #00cc00, #00aaff);
                color: white;
            }
            
            .test-btn {
                background: linear-gradient(45deg, #ff9900, #ff6600);
                color: white;
            }
            
            .generate-btn {
                background: linear-gradient(45deg, #9966ff, #ff00ff);
                color: white;
            }
            
            .action-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
            }
            
            .local-info {
                margin-top: 40px;
                padding: 20px;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 15px;
                color: #aaa;
            }
        </style>
    </head>
    <body>
        <a href="/dashboard" class="back-btn">← Back</a>
        
        <div class="link-container">
            <div class="link-icon">🌍</div>
            <h1 class="link-title">Public Access Link</h1>
            <p class="link-subtitle">
                Share this link with anyone to access your website from anywhere in the world.
                The link is automatically generated using Cloudflare Tunnel.
            </p>
            
            <div class="link-box">
                <div id="publicLink" class="public-link">Generating link... ⏳</div>
                <div id="linkStatus" style="color:#ff9900;">Please wait while we generate your public link</div>
            </div>
            
            <div class="action-buttons">
                <button class="action-btn copy-btn" onclick="copyLink()">📋 Copy Link</button>
                <a href="http://localhost:5000" target="_blank" class="action-btn test-btn">🌐 Test Local</a>
                <button class="action-btn generate-btn" onclick="generateNewLink()">🔄 Generate New</button>
            </div>
            
            <div class="local-info">
                <h3>📱 Local Access</h3>
                <p>For development: <strong>http://localhost:5000</strong></p>
                <p style="font-size:0.9rem; margin-top:10px;">
                    Note: Public link requires Cloudflared to be installed on the server.
                </p>
            </div>
        </div>
        
        <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
        <script>
            const socket = io();
            
            // Listen for public link from server
            socket.on('public_link', function(data) {
                document.getElementById('publicLink').innerHTML = data.url;
                document.getElementById('publicLink').style.color = '#00ff88';
                document.getElementById('linkStatus').innerHTML = '✅ Link active (expires in 24 hours)';
                document.getElementById('linkStatus').style.color = '#00ff88';
            });
            
            function copyLink() {
                const link = document.getElementById('publicLink').innerText;
                if (link && link !== 'Generating link... ⏳') {
                    navigator.clipboard.writeText(link).then(() => {
                        alert('✅ Link copied to clipboard!');
                    });
                } else {
                    alert('⏳ Please wait for link to generate');
                }
            }
            
            function generateNewLink() {
                document.getElementById('publicLink').innerHTML = 'Generating new link... ⏳';
                document.getElementById('linkStatus').innerHTML = 'Requesting new tunnel...';
                document.getElementById('linkStatus').style.color = '#ff9900';
                
                fetch('/generate_tunnel')
                    .then(response => response.json())
                    .then(data => {
                        if (data.url) {
                            document.getElementById('publicLink').innerHTML = data.url;
                            document.getElementById('linkStatus').innerHTML = '✅ New link generated';
                        }
                    });
            }
            
            // Try to get link on page load
            fetch('/get_public_url')
                .then(response => response.json())
                .then(data => {
                    if (data.url) {
                        document.getElementById('publicLink').innerHTML = data.url;
                        document.getElementById('publicLink').style.color = '#00ff88';
                        document.getElementById('linkStatus').innerHTML = '✅ Link active';
                        document.getElementById('linkStatus').style.color = '#00ff88';
                    }
                });
        </script>
    </body>
    </html>
    '''

# ==================== TUNNEL FUNCTIONS ====================
def start_tunnel_thread():
    """Background thread to create public tunnel"""
    time.sleep(7)  # Wait for server to start
    
    try:
        print("\n" + "="*60)
        print("🌍 STARTING PUBLIC TUNNEL...")
        print("="*60)
        
        # Start Cloudflared tunnel
        process = subprocess.Popen(
            ["cloudflared", "tunnel", "--url", "http://localhost:5000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output and find URL
        for line in iter(process.stdout.readline, ''):
            print(f"TUNNEL: {line.strip()}")
            
            # Look for the public URL
            match = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", line)
            if match:
                public_url = match.group(0)
                
                print("\n" + "="*60)
                print(f"✅ PUBLIC LINK GENERATED!")
                print(f"🌐 PUBLIC: {public_url}")
                print(f"📱 LOCAL: http://localhost:5000")
                print("="*60 + "\n")
                
                # Send to all connected clients
                socketio.emit('public_link', {
                    'url': public_url,
                    'timestamp': datetime.datetime.now().isoformat(),
                    'message': 'Public tunnel is active!'
                })
                
                break
        
        # Keep the process running in background
        threading.Thread(target=monitor_tunnel_process, args=(process,), daemon=True).start()
        
    except FileNotFoundError:
        print("\n❌ Cloudflared not found. Only local access available.")
        print("👉 Install: https://github.com/cloudflare/cloudflared")
        print("📡 Local URL: http://localhost:5000\n")
    except Exception as e:
        print(f"\n❌ Tunnel error: {str(e)}")

def monitor_tunnel_process(process):
    """Monitor tunnel process"""
    try:
        process.wait()
        print("⚠️ Tunnel process ended")
    except:
        pass

@app.route('/get_public_url')
def get_public_url():
    """API to get current public URL"""
    try:
        # Try to get active tunnels
        result = subprocess.run(
            ["cloudflared", "tunnel", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Parse output for URL
        lines = result.stdout.split('\n')
        for line in lines:
            if '.trycloudflare.com' in line:
                match = re.search(r"https://[a-z0-9\-]+\.trycloudflare\.com", line)
                if match:
                    return jsonify({'url': match.group(0), 'status': 'active'})
    except:
        pass
    
    return jsonify({'url': 'http://localhost:5000', 'status': 'local_only'})

@app.route('/generate_tunnel')
def generate_tunnel():
    """Generate new tunnel"""
    try:
        # Kill existing tunnel
        subprocess.run(["pkill", "cloudflared"], capture_output=True)
        time.sleep(2)
        
        # Start new thread for tunnel
        threading.Thread(target=start_tunnel_thread, daemon=True).start()
        
        return jsonify({'success': True, 'message': 'New tunnel requested'})
    except Exception as e:
        return jsonify({'error': str(e)})

# ==================== OTHER ESSENTIAL ROUTES ====================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/download_project/<filename>')
def download_project(filename):
    if 'user_id' not in session:
        return redirect('/')
    return send_from_directory(f"user_projects/{session['user_id']}", filename, as_attachment=True)

@app.route('/delete_project/<filename>')
def delete_project(filename):
    if 'user_id' not in session:
        return redirect('/')
    filepath = f"user_projects/{session['user_id']}/{filename}"
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect('/my_projects')

@app.route('/edit_project/<filename>', methods=['GET', 'POST'])
def edit_project(filename):
    if 'user_id' not in session:
        return redirect('/')
    
    filepath = f"user_projects/{session['user_id']}/{filename}"
    
    if request.method == 'POST':
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(request.form['content'])
        return redirect('/my_projects')
    
    content = ""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Edit {filename}</title>
        <style>
            body {{
                background: #0a0a15;
                color: white;
                font-family: monospace;
                margin: 0;
                padding: 0;
            }}
            
            .editor-header {{
                background: rgba(20, 25, 40, 0.9);
                padding: 20px;
                border-bottom: 2px solid #00ccff;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .editor-title {{
                font-size: 1.5rem;
                color: #00ccff;
                font-weight: bold;
            }}
            
            .back-btn {{
                padding: 10px 20px;
                background: rgba(255, 255, 255, 0.1);
                color: white;
                text-decoration: none;
                border-radius: 8px;
                transition: all 0.3s;
            }}
            
            .back-btn:hover {{
                background: rgba(255, 255, 255, 0.2);
            }}
            
            textarea {{
                width: 100%;
                height: calc(100vh - 100px);
                background: #000;
                color: #00ff88;
                border: none;
                padding: 20px;
                font-family: monospace;
                font-size: 1rem;
                resize: none;
                outline: none;
            }}
            
            .save-btn {{
                position: fixed;
                bottom: 30px;
                right: 30px;
                padding: 15px 30px;
                background: linear-gradient(45deg, #00cc00, #00aaff);
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }}
            
            .save-btn:hover {{
                transform: translateY(-3px);
                box-shadow: 0 5px 15px rgba(0, 200, 255, 0.4);
            }}
        </style>
    </head>
    <body>
        <div class="editor-header">
            <div class="editor-title">Editing: {filename}</div>
            <a href="/my_projects" class="back-btn">← Back to Projects</a>
        </div>
        
        <form method="POST">
            <textarea name="content">{content.replace('<', '&lt;').replace('>', '&gt;')}</textarea>
            <button type="submit" class="save-btn">💾 SAVE CHANGES</button>
        </form>
    </body>
    </html>
    '''

# ==================== START SERVER ====================
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 K.R CLOUD PRO V7.0 - STARTING")
    print("="*60)
    
    # Start tunnel in background thread
    threading.Thread(target=start_tunnel_thread, daemon=True).start()
    
    print("📡 Local Server: http://localhost:5000")
    print("⏳ Public tunnel initializing...")
    print("="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)

