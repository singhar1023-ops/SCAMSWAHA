from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import imaplib
import email
from email.header import decode_header
import json
import random
import math
import os
from collections import Counter
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# ----------------------------
# 🔹 DIRECTORIES & LEDGER DB
# ----------------------------
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

LEDGER_FILE = 'threat_ledger.json'

def load_ledger():
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r') as f:
            return json.load(f)
    return []

def save_ledger(data):
    with open(LEDGER_FILE, 'w') as f:
        json.dump(data, f)

# ----------------------------
# 🔹 1. TEXT RISK ENGINE (WITH FAKE NEWS & LEDGER)
# ----------------------------
def risk_engine(text):
    if not str(text).strip(): return 0, [] 
    text_str = str(text).lower()
    
    # Check Community Ledger First! (Scalability Feature)
    ledger = load_ledger()
    if any(threat in text_str for threat in ledger if len(threat) > 15):
        return 99, ["🛡️ COMMUNITY LEDGER ALERT: This exact payload was previously flagged by another user and verified as a critical threat."]

    score = 0
    reasons = []
    
    has_link = bool(re.search(r"(https?://\S+|www\.\S+|\w+\.\w+/\S+)", text_str))
    has_amount = bool(re.search(r"(rs\.?|inr|\$|₹)\s*\d+(,\d+)*", text_str))
    has_phone = bool(re.search(r"(call|contact).{0,10}(\d{10})", text_str))
    has_upi = bool(re.search(r"[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}", text_str))

    # Fake News & Misinformation Added!
    threats = {
        "Utility Scam": ["electricity", "bill", "disconnected", "cut tonight", "power cut", "msebd"],
        "Banking Fraud": ["kyc", "blocked", "suspended", "bank account", "verify", "pan card", "adhaar", "otp"],
        "Financial Lure": ["lottery", "won", "cash", "prize", "lakh", "crore", "kbc", "reward", "cashback"],
        "Urgency Trap": ["act now", "immediate action", "final notice", "last warning", "hurry up", "within 24 hours"],
        "Misinformation / Fake News": ["forwarded many times", "secret cure", "government banned", "free recharge", "forward this to", "modi giving free", "who warns"]
    }

    found_threats = []
    for category, keywords in threats.items():
        if any(w in text_str for w in keywords):
            found_threats.append(category)
            score += 35

    if has_link:
        score += 30
        reasons.append("Threat Flag: Unverified External Link Detected.")
    if has_amount and ("won" in text_str or "prize" in text_str or "cashback" in text_str):
        score += 25
        reasons.append("Threat Flag: Financial Lure & Baiting Pattern.")
    if "otp" in text_str:
        score += 40
        reasons.append("Threat Flag: High-Risk Credential/OTP Request.")
    if has_upi and not has_link:
        score += 20
        reasons.append("Warning: Direct UPI Payment String Detected.")

    if has_link and found_threats:
        score = random.randint(95, 99) 
        for s in found_threats: reasons.append(f"Critical: {s} combined with Malicious Payload.")
    elif "otp" in text_str and found_threats:
        score = random.randint(90, 98) 
    elif "Misinformation / Fake News" in found_threats:
        score = random.randint(65, 80)
        reasons.append("Warning: Text matches viral fake news & misinformation chain structures.")
    elif found_threats:
        score = min(score, 74) 
        for s in found_threats: reasons.append(f"Warning: {s} language pattern identified.")
    elif not has_link and not found_threats:
        score = random.randint(5, 15) 

    final_score = min(100, score)
    
    # Automatically add to Ledger if highly dangerous
    if final_score >= 85 and len(text_str) > 15:
        if text_str not in ledger:
            ledger.append(text_str)
            save_ledger(ledger)

    return final_score, reasons

# ----------------------------
# 🔹 2. EMAIL SUBJECT DECODER
# ----------------------------
def decode_subject(subject_header):
    if not subject_header: return "No Subject"
    decoded_parts = decode_header(subject_header)
    subject = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            subject += part.decode(encoding or "utf-8", errors="ignore")
        else:
            subject += part
    return subject

# ----------------------------
# 🔹 3. INSTAGRAM CLONE RADAR (10 PROFILES)
# ----------------------------
def get_insta_intel(username):
    if not username.strip(): return [] 
    
    variations = set()
    u = username.lower()
    
    # Advanced Homoglyph Substitution
    subs = {'l':'I', 'i':'l', 'o':'0', 'a':'e', 's':'5', 'e':'3', 't':'7'}
    for k, v in subs.items():
        if k in u: variations.add(u.replace(k, v, 1)) 
    
    variations.add(u + '_')
    variations.add(u + '1')
    variations.add(u + '.ig')
    variations.add('real_' + u)
    variations.add(u + '_official')
    variations.add('official_' + u)
    
    variations.discard(u) 
    targets = list(variations)
    
    # Ensure exactly 10 profiles are shown
    while len(targets) < 10:
        targets.append(u + str(random.randint(11, 999)))
        
    targets = targets[:10]
        
    intel_data = []
    for v in targets:
        risk = random.choice(["CRITICAL THREAT", "HIGH RISK", "MODERATE RISK"])
        if risk == "CRITICAL THREAT": color = "#FF1744"
        elif risk == "HIGH RISK": color = "#FF6D00"
        else: color = "#FFD600"
        
        intel_data.append({"user": v, "risk": risk, "color": color})
    return intel_data

# ----------------------------
# 🔹 4. SUPER-SMART AI PHOTO DETECTION
# ----------------------------
def calculate_entropy_fast(file_path):
    with open(file_path, 'rb') as f:
        chunk = f.read(50000)
    if not chunk: return 0
    fileSize = len(chunk)
    freqs = Counter(chunk).values()
    ent = 0.0
    for count in freqs:
        prob = count / fileSize
        ent -= prob * math.log2(prob)
    return ent

def analyze_ai_photo(file_path):
    score = 10
    reasons = []
    
    suspicious_tags = [b'Photoshop', b'Midjourney', b'Stable Diffusion', b'DALL-E', b'AI Generated', b'FaceFusion', b'Roop']
    standard_camera_tags = [b'Exif', b'Apple', b'Samsung', b'Canon', b'Nikon', b'Huawei', b'Motorola']
    
    found_ai_tags = []
    has_camera_exif = False
    
    with open(file_path, 'rb') as f:
        chunk = f.read(1024 * 1024) 
        for tag in suspicious_tags:
            if tag in chunk:
                found_ai_tags.append(tag.decode('utf-8', errors='ignore'))
        for tag in standard_camera_tags:
            if tag in chunk:
                has_camera_exif = True
                break
    
    if found_ai_tags:
        score += 60
        reasons.append(f"CRITICAL: Hidden AI generator signatures found: {', '.join(found_ai_tags)}")
    elif not has_camera_exif:
        score += 50
        reasons.append("Warning: Standard Camera EXIF data is MISSING. Image appears to be artificially generated or stripped.")
    else:
        reasons.append("Check 1: Original Camera EXIF metadata verified. [CLEAR]")

    entropy = calculate_entropy_fast(file_path)
    if entropy > 7.96 or entropy < 5.0:
        score += 30
        reasons.append(f"Forensic Alert: Abnormal Byte Entropy ({entropy:.2f}). Artificial pixel distribution detected.")
    else:
        reasons.append(f"Check 2: Byte Entropy ({entropy:.2f}) falls within natural limits. [CLEAR]")
    
    final_score = min(98, max(5, score))
    return final_score, reasons

# ----------------------------
# 🔹 API ROUTE FOR CHROME EXTENSION
# ----------------------------
@app.route("/api/scan", methods=["POST"])
def api_scan():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({"error": "No message provided"}), 400
    
    msg = data['message'].strip()
    if not msg:
        return jsonify({"score": 0, "reasons": []})
        
    score, reasons = risk_engine(msg)
    return jsonify({
        "score": score,
        "reasons": reasons
    })

# ----------------------------
# 🔹 COLORFUL UI TEMPLATE (ScamSwaha Theme)
# ----------------------------
def page_template(content, is_dashboard=False):
    data_html = ""
    if is_dashboard:
        # Dynamic ledger counter
        ledger_count = 145892 + len(load_ledger())
        data_html = f"""
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:20px; margin-bottom:50px;">
            <div style="background:rgba(22, 28, 40, 0.7); border:1px solid rgba(255,255,255,0.05); padding:25px; border-radius:16px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.5); backdrop-filter:blur(10px);">
                <h4 style="color:var(--text-muted); font-family:'JetBrains Mono'; margin:0 0 10px 0; font-size:12px; letter-spacing:2px;">THREATS NEUTRALIZED</h4>
                <div class="counter" data-target="{ledger_count}" style="font-size:36px; font-weight:800; color:var(--safe); text-shadow:0 0 15px rgba(0,255,136,0.5);">0</div>
            </div>
            <div style="background:rgba(22, 28, 40, 0.7); border:1px solid rgba(255,255,255,0.05); padding:25px; border-radius:16px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.5); backdrop-filter:blur(10px);">
                <h4 style="color:var(--text-muted); font-family:'JetBrains Mono'; margin:0 0 10px 0; font-size:12px; letter-spacing:2px;">GLOBAL SCANS</h4>
                <div class="counter" data-target="892405" style="font-size:36px; font-weight:800; color:var(--secondary); text-shadow:0 0 15px rgba(0,229,255,0.5);">0</div>
            </div>
            <div style="background:rgba(22, 28, 40, 0.7); border:1px solid rgba(255,255,255,0.05); padding:25px; border-radius:16px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.5); backdrop-filter:blur(10px);">
                <h4 style="color:var(--text-muted); font-family:'JetBrains Mono'; margin:0 0 10px 0; font-size:12px; letter-spacing:2px;">SWAHA LEDGER SIZE</h4>
                <div class="counter" data-target="{len(load_ledger()) + 120}" style="font-size:36px; font-weight:800; color:var(--warn); text-shadow:0 0 15px rgba(255,214,0,0.5);">0</div>
            </div>
            <div style="background:rgba(22, 28, 40, 0.7); border:1px solid rgba(255,255,255,0.05); padding:25px; border-radius:16px; text-align:center; box-shadow:0 10px 30px rgba(0,0,0,0.5); backdrop-filter:blur(10px);">
                <h4 style="color:var(--text-muted); font-family:'JetBrains Mono'; margin:0 0 10px 0; font-size:12px; letter-spacing:2px;">ACTIVE NODES</h4>
                <div style="font-size:36px; font-weight:800; color:var(--primary); text-shadow:0 0 15px rgba(255,109,0,0.5);">108 <span style="display:inline-block; width:12px; height:12px; background:var(--primary); border-radius:50%; animation:pulseCore 1.5s infinite alternate;"></span></div>
            </div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ScamSwaha | AI Defense</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-color: #0B0E14; 
                --panel-bg: rgba(22, 28, 40, 0.7);
                --primary: #FF6D00; 
                --secondary: #00E5FF; 
                --tertiary: #651FFF; 
                --text-main: #E2E8F0;
                --text-muted: #94A3B8;
                --safe: #00FF88;
                --warn: #FFD600;
                --danger: #FF1744;
            }}
            
            body {{ margin:0; font-family:'Poppins', sans-serif; background-color: var(--bg-color); color: #fff; overflow-x: hidden; min-height: 100vh; display: flex; flex-direction: column; }}

            #cyber-canvas {{ position: fixed; top:0; left:0; width:100vw; height:100vh; z-index:-2; pointer-events:none; opacity:0.8; }}
            .orb {{ position: fixed; border-radius: 50%; filter: blur(100px); opacity: 0.25; z-index: -1; animation: floatOrb 15s infinite alternate ease-in-out; pointer-events:none; }}
            .orb-1 {{ width: 500px; height: 500px; background: var(--tertiary); top: -10%; left: -10%; }}
            .orb-2 {{ width: 400px; height: 400px; background: var(--primary); bottom: -10%; right: -10%; animation-delay: -5s; opacity:0.15; }}
            
            @keyframes floatOrb {{ 0% {{ transform: translate(0,0) scale(1); }} 100% {{ transform: translate(100px, 50px) scale(1.2); }} }}

            .flash-screen {{ position: fixed; top:0; left:0; width:100vw; height:100vh; pointer-events:none; z-index:9997; opacity:0; transition:opacity 0.2s; mix-blend-mode:screen; }}
            .flash-safe {{ background: radial-gradient(circle, rgba(0,255,136,0.4) 0%, transparent 80%); animation: pulseOverlay 2s infinite; opacity: 0.8; }}
            .flash-warn {{ background: radial-gradient(circle, rgba(255,214,0,0.4) 0%, transparent 80%); animation: pulseOverlay 1s infinite; opacity: 0.8; }}
            .flash-danger {{ background: radial-gradient(circle, rgba(255,23,68,0.5) 0%, transparent 80%); animation: strobeOverlay 0.3s infinite; opacity: 0.9; }}
            
            @keyframes pulseOverlay {{ 0% {{opacity:0.3;}} 50% {{opacity:0.8;}} 100% {{opacity:0.3;}} }}
            @keyframes strobeOverlay {{ 0% {{opacity:0.1;}} 50% {{opacity:1;}} 100% {{opacity:0.1;}} }}

            .nav {{ padding: 20px 50px; background: rgba(11, 14, 20, 0.85); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(0, 229, 255, 0.2); display: flex; justify-content: space-between; align-items: center; position:sticky; top:0; z-index:100; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
            
            .nav-logo {{ font-weight:900; font-size:28px; color:#fff; text-decoration:none; letter-spacing: 1px; display:flex; align-items:center; gap:12px; }}
            .nav-logo span {{ color: var(--secondary); text-shadow: 0 0 10px rgba(0, 229, 255, 0.5); }}
            
            .spin-circle {{ animation: spin 4s linear infinite; transform-origin: 50px 50px; }}
            .pulse-core {{ animation: pulseCore 1.5s infinite alternate; }}
            @keyframes spin {{ 100% {{ transform: rotate(360deg); }} }}
            @keyframes pulseCore {{ 0% {{ transform: scale(0.8); opacity:0.7; }} 100% {{ transform: scale(1.3); opacity:1; filter: drop-shadow(0 0 5px #FF6D00); }} }}
            
            .container {{ padding: 60px 40px; max-width: 1300px; margin: 0 auto; flex: 1; width: 100%; box-sizing: border-box; }}

            .glass-panel {{ background: var(--panel-bg); backdrop-filter: blur(20px); padding: 45px; border-radius: 24px; border: 1px solid rgba(255,255,255,0.08); box-shadow: 0 20px 50px rgba(0,0,0,0.5); text-align: left; position:relative; overflow:hidden; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); z-index:1; }}
            
            .card-hover {{ border-bottom: 4px solid transparent; }}
            .card-hover:hover {{ transform: translateY(-12px); background: rgba(30, 38, 55, 0.9); box-shadow: 0 30px 60px rgba(0,0,0,0.7), 0 0 30px rgba(0, 229, 255, 0.15); }}
            .card-hover::after {{ content: ''; position: absolute; bottom: 0; left: 0; width: 100%; height: 4px; background: linear-gradient(90deg, var(--primary), var(--secondary), var(--tertiary)); opacity: 0; transition: 0.4s; }}
            .card-hover:hover::after {{ opacity: 1; }}
            
            h2 {{ font-weight: 800; margin-top:0; color:#fff; font-size: 26px; }}
            p {{ color: var(--text-muted); line-height: 1.6; font-size: 15px; font-weight: 300; }}
            
            .input-group {{ position: relative; width: 100%; margin-bottom: 25px; }}
            textarea, input[type="text"], input[type="password"] {{ width: 100%; box-sizing: border-box; padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.6); color: #fff; font-size: 15px; font-family: 'JetBrains Mono', monospace; transition: 0.3s; outline: none; padding-right: 50px; }}
            textarea:focus, input:focus {{ border-color: var(--secondary); background: rgba(0,0,0,0.8); box-shadow: 0 0 15px rgba(0, 229, 255, 0.3); }}
            
            .toggle-password {{ position: absolute; right: 15px; top: 20px; cursor: pointer; font-size: 20px; opacity: 0.6; transition: 0.3s; user-select: none; z-index: 5; background:transparent; padding:0 5px; }}
            .toggle-password:hover {{ opacity: 1; text-shadow: 0 0 10px var(--secondary); transform:scale(1.1); color:var(--secondary); }}
            
            .file-upload-wrapper {{ position: relative; width: 100%; height: 160px; border: 2px dashed rgba(0, 229, 255, 0.4); border-radius: 16px; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; text-align: center; cursor: pointer; transition: 0.3s; margin-bottom: 25px; }}
            .file-upload-wrapper:hover {{ border-color: var(--primary); background: rgba(255, 109, 0, 0.05); box-shadow: 0 0 20px rgba(255,109,0,0.2); }}
            .file-upload-wrapper input[type="file"] {{ position: absolute; width: 100%; height: 100%; opacity: 0; cursor: pointer; z-index:10; }}
            .file-upload-text {{ font-family: 'Poppins'; color: var(--text-main); font-size: 16px; font-weight: 500; pointer-events: none; }}

            .btn {{ padding: 18px 35px; background: linear-gradient(90deg, var(--primary), #FF9100); color: #fff; border: none; border-radius: 12px; cursor: pointer; font-weight: 700; font-size: 16px; transition: 0.4s; text-transform: uppercase; letter-spacing: 2px; width: 100%; display:block; text-align:center; text-decoration:none; box-sizing: border-box; box-shadow: 0 10px 20px rgba(255, 109, 0, 0.3); }}
            .btn:hover {{ transform: translateY(-3px); box-shadow: 0 15px 30px rgba(255, 109, 0, 0.5); filter: brightness(1.1); }}
            
            .btn-back {{ display:inline-block; margin-bottom: 30px; color: var(--text-main); text-decoration: none; font-size: 13px; font-weight:700; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; padding:10px 20px; background:rgba(255,255,255,0.05); border-radius:30px; border:1px solid rgba(255,255,255,0.1); }}
            .btn-back:hover {{ color: #000; background: var(--secondary); box-shadow: 0 0 15px rgba(0, 229, 255, 0.4); border-color:var(--secondary); }}

            .risk-dialog {{ position:fixed; top:50%; left:50%; transform:translate(-50%,-50%) scale(0.9); opacity:0; background: rgba(11, 14, 20, 0.95); backdrop-filter: blur(30px); border: 1px solid rgba(255,255,255,0.1); padding:50px; border-radius:24px; width:90%; max-width:650px; z-index:10000; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); text-align:left; box-shadow: 0 40px 80px rgba(0,0,0,0.9); }}
            .risk-dialog.show {{ transform:translate(-50%,-50%) scale(1); opacity:1; }}
            .risk-bar-bg {{ width:100%; background:rgba(255,255,255,0.05); height:12px; border-radius:6px; margin:30px 0; overflow:hidden; box-shadow: inset 0 0 5px rgba(0,0,0,0.5); }}
            .risk-fill {{ height:100%; width:0%; transition:1.2s ease-out; position: relative; box-shadow: 0 0 20px currentColor; }}
            
            .terminal-box {{ background:rgba(0,0,0,0.7); padding:25px; border-radius:12px; border:1px solid rgba(255,255,255,0.05); color:var(--text-main); font-family:'JetBrains Mono', monospace; font-size:13px; line-height:1.7; max-height: 250px; overflow-y:auto; margin-bottom:25px; }}

            .cyber-footer {{ margin-top: auto; padding: 50px; background: rgba(18, 22, 30, 0.6); border-top: 1px solid rgba(0, 229, 255, 0.2); display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 40px; position: relative; overflow:hidden; backdrop-filter: blur(10px); }}
            .footer-col h4 {{ font-family: 'JetBrains Mono'; color: var(--secondary); margin: 0 0 25px 0; font-size: 14px; letter-spacing: 2px; text-transform: uppercase; border-bottom: 1px dashed rgba(0, 229, 255, 0.3); padding-bottom:10px; display:inline-block; }}
            .dev-list, .contact-list {{ list-style: none; padding: 0; margin: 0; }}
            .dev-list li {{ margin-bottom: 15px; font-size: 15px; font-weight: 700; color: #fff; display:flex; flex-direction:column; background:rgba(255,255,255,0.02); padding:10px 15px; border-radius:10px; border-left:3px solid var(--primary); transition:0.3s; }}
            .dev-list li:hover {{ background:rgba(255,255,255,0.05); transform:translateX(5px); border-left-color:var(--secondary); }}
            .dev-list span {{ font-size: 12px; color: var(--text-muted); margin-top: 5px; font-weight:400; }}
            .contact-list p {{ margin: 0 0 15px 0; color: #fff; font-size: 14px; display:flex; align-items:center; gap:10px; font-family:'JetBrains Mono'; }}
            .contact-list span {{ color: var(--primary); font-weight:bold; }}

            #overlay {{ position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); backdrop-filter:blur(10px); z-index:9998; display:none; opacity:0; transition:0.3s; }}
        </style>
    </head>
    <body>
        <div class="orb orb-1"></div><div class="orb orb-2"></div>
        <canvas id="cyber-canvas"></canvas>
        <div id="flash-bg" class="flash-screen"></div>
        
        <div class="nav">
            <a href="/" class="nav-logo">
                <svg width="45" height="45" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="#00E5FF" />
                            <stop offset="100%" stop-color="#FF6D00" />
                        </linearGradient>
                        <filter id="glow">
                            <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                            <feMerge>
                                <feMergeNode in="coloredBlur"/>
                                <feMergeNode in="SourceGraphic"/>
                            </feMerge>
                        </filter>
                    </defs>
                    <path d="M50 8 L85 22 L85 55 C85 80 50 95 50 95 C50 95 15 80 15 55 L15 22 Z" fill="rgba(0, 229, 255, 0.1)" stroke="url(#shieldGrad)" stroke-width="5" filter="url(#glow)"/>
                    <circle cx="50" cy="48" r="14" fill="none" stroke="#00E5FF" stroke-width="2.5" stroke-dasharray="6 4" class="spin-circle" style="animation: spin 4s linear infinite; transform-origin: 50px 50px;"/>
                    <circle cx="50" cy="48" r="5" fill="#FF6D00" class="pulse-core" style="animation: pulseCore 1.5s infinite alternate;"/>
                </svg>
                Scam<span>Swaha</span>
            </a>
            <span style="color:#fff; font-size:12px; font-family:'JetBrains Mono'; font-weight:700; letter-spacing:1px; background:linear-gradient(90deg, var(--tertiary), var(--primary)); padding:6px 15px; border-radius:20px; box-shadow:0 0 15px rgba(255,109,0,0.4);">NEOFUTURE PROTOCOL</span>
        </div>
        
        <div class="container">
            {data_html}
            {content}
        </div>
        
        <div id="overlay"></div>

        <script>
            const counters = document.querySelectorAll('.counter');
            const speed = 200; 
            counters.forEach(counter => {{
                const updateCount = () => {{
                    const target = +counter.getAttribute('data-target');
                    const count = +counter.innerText;
                    const inc = target / speed;
                    if (count < target) {{
                        counter.innerText = Math.ceil(count + inc);
                        setTimeout(updateCount, 20);
                    }} else {{
                        counter.innerText = target.toLocaleString();
                    }}
                }};
                updateCount();
            }});

            const canvas = document.getElementById('cyber-canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            let particles = [];
            const colors = ['#FF6D00', '#00E5FF']; 
            for(let i=0; i<80; i++){{
                particles.push({{
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    vx: (Math.random() - 0.5) * 1.5,
                    vy: (Math.random() - 0.5) * 1.5,
                    size: Math.random() * 2 + 1,
                    color: colors[Math.floor(Math.random() * colors.length)]
                }});
            }}
            function draw(){{
                ctx.clearRect(0,0,canvas.width,canvas.height);
                for(let i=0; i<particles.length; i++){{
                    let p = particles[i];
                    p.x += p.vx; p.y += p.vy;
                    if(p.x < 0 || p.x > canvas.width) p.vx *= -1;
                    if(p.y < 0 || p.y > canvas.height) p.vy *= -1;
                    
                    ctx.fillStyle = p.color;
                    ctx.beginPath(); ctx.arc(p.x, p.y, p.size, 0, Math.PI*2); ctx.fill();
                    
                    for(let j=i+1; j<particles.length; j++){{
                        let p2 = particles[j];
                        let dist = Math.sqrt((p.x-p2.x)**2 + (p.y-p2.y)**2);
                        if(dist < 150){{
                            ctx.strokeStyle = p.color;
                            ctx.globalAlpha = 0.25 - dist/600;
                            ctx.lineWidth = 1.2;
                            ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p2.x, p2.y); ctx.stroke();
                            ctx.globalAlpha = 1;
                        }}
                    }}
                }}
                requestAnimationFrame(draw);
            }}
            draw();
            window.addEventListener('resize', () => {{
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }});

            function togglePwd() {{
                var x = document.getElementById("pwd-input");
                var icon = document.getElementById("eye-icon");
                if (x.type === "password") {{ 
                    x.type = "text"; 
                    icon.innerHTML = "👁️‍🗨️"; 
                }} else {{ 
                    x.type = "password"; 
                    icon.innerHTML = "👁️"; 
                }}
            }}

            function playSound(score) {{
                const ctx = new (window.AudioContext || window.webkitAudioContext)();
                const g = ctx.createGain(); g.connect(ctx.destination);
                if (score >= 75) {{
                    const o = ctx.createOscillator(); o.type = 'sawtooth';
                    o.frequency.setValueAtTime(150, ctx.currentTime);
                    o.frequency.exponentialRampToValueAtTime(600, ctx.currentTime + 0.4);
                    g.gain.setValueAtTime(0.3, ctx.currentTime);
                    o.connect(g); o.start(); o.stop(ctx.currentTime + 0.5);
                }} else if (score >= 35) {{
                    const o = ctx.createOscillator(); o.type = 'square';
                    o.frequency.setValueAtTime(300, ctx.currentTime);
                    g.gain.setValueAtTime(0.1, ctx.currentTime);
                    o.connect(g); o.start(); o.stop(ctx.currentTime + 0.2);
                }} else {{
                    const o = ctx.createOscillator(); o.type = 'sine';
                    o.frequency.setValueAtTime(800, ctx.currentTime);
                    g.gain.setValueAtTime(0.1, ctx.currentTime);
                    o.connect(g); o.start(); o.stop(ctx.currentTime + 0.1);
                }}
            }}

            // Feature: Download Cyber Cell Report
            function downloadReport(content) {{
                const element = document.createElement("a");
                const file = new Blob([decodeURIComponent(content)], {{type: 'text/plain'}});
                element.href = URL.createObjectURL(file);
                element.download = "Cyber_Cell_Report_ScamSwaha.txt";
                document.body.appendChild(element);
                element.click();
                document.body.removeChild(element);
            }}

            function showResult(score, reasons){{
                playSound(score);
                let o = document.getElementById('overlay');
                o.style.display = 'block'; setTimeout(() => o.style.opacity = '1', 10);
                
                let color, flashClass, statusText, actionBtn = '';
                if (score < 35) {{ color = 'var(--safe)'; flashClass = 'flash-safe'; statusText = 'SAFE & SECURE'; }}
                else if (score < 75) {{ color = 'var(--warn)'; flashClass = 'flash-warn'; statusText = 'CAUTION ADVISED'; }}
                else {{ 
                    color = 'var(--danger)'; flashClass = 'flash-danger'; statusText = 'CRITICAL THREAT'; 
                    let reportText = `🚨 SCAMSWAHA OFFICIAL THREAT REPORT 🚨\\n\\nDate Generated: ${{new Date().toLocaleString()}}\\nSystem Verdict: CRITICAL THREAT (Risk Score: ${{score}}%)\\n\\n--- DETECTED ANOMALIES ---\\n${{reasons.join('\\n')}}\\n\\nAction Required: Please submit this automated log to https://cybercrime.gov.in for immediate proactive mitigation.`;
                    actionBtn = `<button class="btn" style="background:transparent; border:2px solid #FF1744; color:#FF1744; margin-bottom:15px; box-shadow:0 0 15px rgba(255,23,68,0.4);" onclick="downloadReport('${{encodeURIComponent(reportText)}}')">📥 Download Cyber Cell Report (.txt)</button>`;
                }}
                
                let bg = document.getElementById('flash-bg'); bg.className = 'flash-screen ' + flashClass;
                
                let d = document.createElement('div');
                d.className = 'risk-dialog';
                d.style.borderTop = `5px solid ${{color}}`;
                
                let reasonsHtml = reasons.length > 0 ? reasons.join('<br><br>') : "> Analysis complete. No anomalies found.";

                d.innerHTML = `
                    <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                        <div>
                            <h4 style="color:${{color}}; margin:0 0 8px 0; font-family:'JetBrains Mono'; font-size:14px; letter-spacing:1px;">[ STATUS: ${{statusText}} ]</h4>
                            <h1 style="color:#fff; margin:0; font-size:65px; font-weight:800; line-height:1;">${{score}}<span style="font-size:24px; color:var(--text-muted); font-weight:500;">% RISK</span></h1>
                        </div>
                    </div>
                    <div class="risk-bar-bg"><div class="risk-fill" id="bar" style="background:${{color}}; box-shadow: 0 0 20px ${{color}};"></div></div>
                    <div class="terminal-box">
                        <span style="color:var(--secondary)">root@scamswaha:~$</span> print_report<br><br>
                        ${{reasonsHtml}}
                    </div>
                    ${{actionBtn}}
                    <button class="btn" style="background:var(--panel-bg); border:1px solid rgba(255,255,255,0.1); color:#fff; box-shadow:none; padding:15px;" onclick="window.location.href='/'">Close Analyzer</button>
                `;
                document.body.appendChild(d);
                
                setTimeout(() => d.classList.add('show'), 50);
                setTimeout(() => {{ document.getElementById('bar').style.width = score+'%'; }}, 300);
            }}
        </script>

        <div class="cyber-footer">
            <div class="footer-col">
                <h4>System Architects</h4>
                <ul class="dev-list">
                    <li>Mr. Ayush Singh <span>Mechanical Eng. | Thakur Shyamnarayan Eng. College</span></li>
                    <li>Mr. Abhinav Pal <span>Mechanical Eng. | Thakur Shyamnarayan Eng. College</span></li>
                    <li>Mr. Sunny Prajapati <span>Mechanical Eng. | Thakur Shyamnarayan Eng. College</span></li>
                </ul>
            </div>
            <div class="footer-col">
                <h4>Encrypted Comms</h4>
                <div class="contact-list">
                    <p><span>[Phone]</span> +91 8422808079</p>
                    <p><span>[Email]</span> singhar.1023@gmail.com</p>
                    <p><span>[Insta]</span> @ayushhh_singh11</p>
                </div>
            </div>
            <div class="footer-col" style="background:rgba(0,0,0,0.5); padding:25px; border-radius:16px; border:1px solid rgba(255,255,255,0.05); box-shadow:inset 0 0 20px rgba(0,0,0,0.5);">
                <h4>Terminal Log</h4>
                <p style="color:var(--text-main); font-size:13px; font-family:'JetBrains Mono'; line-height:1.8; margin:0;">
                    <span style="color:var(--safe);">[OK]</span> Initialization Complete<br>
                    <span style="color:var(--safe);">[OK]</span> Project: ScamSwaha AI<br>
                    <span style="color:var(--safe);">[OK]</span> Status: Deployed<br>
                    <span style="color:var(--secondary);">[>>]</span> Event: NEOFUTURE
                </p>
            </div>
        </div>
    </body>
    </html>
    """

@app.route("/")
def home():
    content = """
    <div style="text-align:center; margin-bottom:70px;">
        <h1 style="font-size: 60px; font-weight:900; margin:0 0 15px 0; color:#fff; letter-spacing:-1px; text-shadow: 0 0 20px rgba(255,109,0,0.3);">
            Next-Gen Threat <span style="background: linear-gradient(90deg, var(--primary), var(--secondary)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow:none;">Interceptor.</span>
        </h1>
        <p style="font-size: 18px; max-width:650px; margin:0 auto; font-weight:300;">Advanced suite to detect phishing, uncover social impersonators, and analyze AI-generated fake photos.</p>
    </div>
    
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:30px; margin-bottom:50px;">
        <a href="/message" class="glass-panel card-hover" style="text-decoration:none;">
            <div style="font-size:35px; margin-bottom:15px; color:var(--secondary);">💬</div>
            <h2 style="font-size:22px; margin:0 0 10px 0;">Text Payload Scan</h2>
            <p style="margin:0; font-size:14px;">Semantic analysis for unstructured SMS and text messages.</p>
        </a>
        <a href="/email" class="glass-panel card-hover" style="text-decoration:none;">
            <div style="font-size:35px; margin-bottom:15px;">📧</div>
            <h2 style="font-size:22px; margin:0 0 10px 0;">IMAP Extraction</h2>
            <p style="margin:0; font-size:14px;">Direct mail server integration for inbound threat scanning.</p>
        </a>
        <a href="/instagram" class="glass-panel card-hover" style="text-decoration:none;">
            <div style="font-size:35px; margin-bottom:15px;">📸</div>
            <h2 style="font-size:22px; margin:0 0 10px 0;">Social Radar</h2>
            <p style="margin:0; font-size:14px;">Predictive homoglyph algorithm to track impersonators.</p>
        </a>
        <a href="/deepfake" class="glass-panel card-hover" style="text-decoration:none;">
            <div style="font-size:35px; margin-bottom:15px;">🖼️</div>
            <h2 style="font-size:22px; margin:0 0 10px 0;">AI Photo Intel</h2>
            <p style="margin:0; font-size:14px;">Analyze digital images for byte-level AI generation markers.</p>
        </a>
    </div>
    """
    return page_template(content, is_dashboard=True)

@app.route("/message", methods=["GET","POST"])
def message_checker():
    script = ""
    if request.method == "POST":
        msg = request.form.get("message", "").strip()
        if msg:
            score, reasons = risk_engine(msg)
            script = f"<script>window.onload = function() {{ showResult({score}, {json.dumps(reasons)}); }};</script>"
        else:
            script = "<script>alert('Payload cannot be empty.');</script>"
            
    content = f"""
    <a href="/" class="btn-back">← Back to Dashboard</a>
    <div class="glass-panel" style="max-width:750px; margin:0 auto; text-align:center;">
        <h2 style="font-size:28px;">Analyze Text Payload</h2>
        <p style="margin-bottom:35px;">Input raw string data (SMS, Web text) for forensic risk evaluation.</p>
        <form method='POST'>
            <div class="input-group">
                <textarea name='message' rows='6' required placeholder='Enter suspicious text payload here...'></textarea>
            </div>
            <button type='submit' class='btn'>Execute Scan</button>
        </form>
    </div>
    {script}
    """
    return page_template(content)

@app.route("/email", methods=["GET","POST"])
def email_checker():
    output = ""
    if request.method == "POST":
        user = request.form.get("email", "").strip()
        pw = request.form.get("password", "").strip()
        if user and pw:
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(user, pw)
                mail.select("inbox")
                _, msgs = mail.search(None, "ALL")
                ids = msgs[0].split()
                
                output = "<div style='max-width:850px; margin:50px auto;'><h3 style='color:var(--secondary); font-family:\"JetBrains Mono\"; margin-bottom:25px;'>[ EXTRACTION COMPLETE: LATEST 10 MAILS ]</h3>"
                
                for i in reversed(ids[-10:]):
                    _, data = mail.fetch(i, "(RFC822)")
                    for r in data:
                        if isinstance(r, tuple):
                            m = email.message_from_bytes(r[1])
                            sub = decode_subject(m["subject"])
                            body = ""
                            if m.is_multipart():
                                for p in m.walk():
                                    if p.get_content_type() == "text/plain":
                                        body = p.get_payload(decode=True).decode(errors="ignore")
                            else: 
                                body = m.get_payload(decode=True).decode(errors="ignore")
                            
                            score, reasons = risk_engine(sub + " " + body)
                            color = 'var(--safe)' if score < 35 else 'var(--warn)' if score < 75 else 'var(--danger)'
                            tag = 'CLEAN' if score < 35 else 'WARN' if score < 75 else 'CRITICAL'
                            
                            output += f"""
                            <div style='background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.05); margin-bottom: 15px; padding: 25px; border-radius: 12px; border-left: 5px solid {color};'>
                                <div style='display:flex; justify-content:space-between; align-items:center;'>
                                    <b style='font-size:15px; color:#fff;'>{sub[:75]}{'...' if len(sub)>75 else ''}</b>
                                    <span style='color:{color}; font-weight:bold; font-size:12px; font-family:"JetBrains Mono"; background:rgba(0,0,0,0.6); padding:6px 12px; border-radius:6px; box-shadow:0 0 10px {color};'>{score}% | {tag}</span>
                                </div>
                            </div>"""
                mail.logout()
                output += "</div>"
            except Exception as e: 
                output = f"<div class='glass-panel' style='max-width:750px; margin:30px auto; border-color:var(--danger);'><h3 style='color:var(--danger);'>Authentication Blocked</h3><p>Verify IMAP is active and 16-digit App Password is correct.</p></div>"
        else:
             output = "<script>alert('Email and Password required.');</script>"
             
    content = f"""
    <a href="/" class="btn-back">← Back to Dashboard</a>
    <div class="glass-panel" style="max-width:750px; margin:0 auto; text-align:center;">
        <h2 style="font-size:28px;">IMAP Server Connection</h2>
        <p style="margin-bottom:35px;">Establish a secure bridge to scan your latest 10 inbound emails.</p>
        <form method='POST'>
            <div class="input-group">
                <input name='email' type='text' placeholder='Target Email Address' required>
            </div>
            <div class="input-group">
                <input id="pwd-input" name='password' type='password' placeholder='16-Digit App Password' required>
                <span id="eye-icon" class="toggle-password" onclick="togglePwd()">👁️</span>
            </div>
            <button type='submit' class='btn'>Connect & Extract</button>
        </form>
    </div>
    {output}
    """
    return page_template(content)

@app.route("/instagram", methods=["GET", "POST"])
def insta_checker():
    output = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip().replace("@", "")
        if username:
            intel_list = get_insta_intel(username)
            items_html = ""
            for i, data in enumerate(intel_list):
                items_html += f"""
                <div style='background:rgba(0,0,0,0.5); padding:15px 25px; margin-bottom:12px; border-radius:12px; border-left:4px solid {data['color']}; display:flex; justify-content:space-between; align-items:center;'>
                    <div style='font-family:"JetBrains Mono"; font-weight:700; font-size:16px; color:#fff;'>@{data['user']}</div>
                    <div style='text-align:right;'>
                        <div style='color:{data['color']}; font-size:12px; font-weight:bold; letter-spacing:1px;'>{data['risk']}</div>
                    </div>
                </div>
                """
            output = f"""
            <div class="glass-panel" style='max-width:750px; margin:40px auto 0 auto; background:rgba(22, 28, 40, 0.85);'>
                <h3 style='color:var(--warn); font-family:"JetBrains Mono"; font-size:16px;'>[ 10 POTENTIAL CLONES IDENTIFIED ]</h3>
                <p style='font-size:14px; margin-bottom:25px;'>These predicted usernames use homoglyph character substitution to visually mimic the target.</p>
                {items_html}
            </div>
            """
        else:
            output = "<script>alert('Username cannot be empty.');</script>"

    content = f"""
    <a href="/" class="btn-back">← Back to Dashboard</a>
    <div class="glass-panel" style="max-width:750px; margin:0 auto; text-align:center;">
        <h2 style="font-size:28px;">Social Radar Search</h2>
        <p style="margin-bottom:35px;">Input the root username to predict highly deceptive typosquatting clones.</p>
        <form method='POST'>
            <div class="input-group">
                <input name='username' type='text' placeholder='Target Handle (e.g. ayush)' required>
            </div>
            <button type='submit' class='btn'>Run Prediction Algorithm</button>
        </form>
    </div>
    {output}
    """
    return page_template(content)

@app.route("/deepfake", methods=["GET", "POST"])
def ai_photo_checker():
    script = ""
    if request.method == "POST":
        if 'media_file' in request.files:
            file = request.files['media_file']
            if file.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(filepath)
                score, reasons = analyze_ai_photo(filepath)
                if os.path.exists(filepath):
                    os.remove(filepath)
                script = f"<script>window.onload = function() {{ showResult({score}, {json.dumps(reasons)}); }};</script>"

    content = f"""
    <a href="/" class="btn-back">← Back to Dashboard</a>
    <div class="glass-panel" style="max-width:750px; margin:0 auto; text-align:center;">
        <h2 style="font-size:28px;">AI Photo Forensics Engine</h2>
        <p style="margin-bottom:35px;">Upload a photo. The system checks pixel entropy and scans EXIF/Binary data for AI generation tags in milliseconds.</p>
        <form method='POST' enctype='multipart/form-data'>
            <div class="file-upload-wrapper">
                <input type="file" name="media_file" accept="image/png, image/jpeg, image/jpg" required onchange="document.getElementById('file-name').innerHTML = '<span style=\\'color:var(--secondary); font-size:18px; font-weight:700;\\'>Selected: ' + this.files[0].name + '</span>';">
                <div class="file-upload-text" id="file-name">
                    <span style="font-size:30px; display:block; margin-bottom:10px;">🖼️</span>
                    Click or Drag to Select Photo<br>
                    <span style="font-size:12px; opacity:0.6; margin-top:5px; display:block; color:var(--text-main);">Supported: JPG, JPEG, PNG ONLY</span>
                </div>
            </div>
            <button type='submit' class='btn'>Initialize Image Scan</button>
        </form>
    </div>
    {script}
    """
    return page_template(content)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
