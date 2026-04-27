#!/usr/bin/env python3
import subprocess, sys, importlib, os, json, time, threading, asyncio, sqlite3, logging, re, uuid
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# --- GESTIÓN DE DEPENDENCIAS ---
_DEPS = [
    ("speech_recognition","speechrecognition"), ("edge_tts","edge-tts"),
    ("requests","requests"), ("cryptography","cryptography"),
    ("websockets","websockets"), ("psutil","psutil"),
    ("sklearn","scikit-learn"), ("bs4","beautifulsoup4")
]
for imp, pkg in _DEPS:
    try: importlib.import_module(imp)
    except: subprocess.check_call([sys.executable,"-m","pip","install",pkg,"--quiet"])

import speech_recognition as sr, psutil, requests, websockets, edge_tts
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC

# --- CONFIGURACIÓN JARVIS 2026 ---
WAKE_WORD, USER_NAME = "x3", "Alexander"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH, KEY_FILE = BASE_DIR/"x3_memory.db", BASE_DIR/".x3_key"
ICSA_2026, TOPE_UF_2026 = 0.035, 87.8
WS_PORT, HTTP_PORT = 8765, 8080
TMP_AUDIO = BASE_DIR/"x3_mic.wav"

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("X3")

# --- SEGURIDAD AES-128 ---
def _init_vault():
    if not KEY_FILE.exists():
        KEY_FILE.write_bytes(Fernet.generate_key())
        os.chmod(KEY_FILE, 0o600)
    return Fernet(KEY_FILE.read_bytes())

_F = _init_vault()
encrypt = lambda s: _F.encrypt(s.encode()).decode()
decrypt = lambda s: _F.decrypt(s.encode()).decode()

class MemoryVault:
    def __init__(self):
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.execute("CREATE TABLE IF NOT EXISTS vault(key TEXT PRIMARY KEY, val TEXT)")
    def save(self, k, v):
        self.conn.execute("INSERT OR REPLACE INTO vault VALUES(?,?)", (k, encrypt(str(v))))
        self.conn.commit()
    def get(self, k):
        row = self.conn.execute("SELECT val FROM vault WHERE key=?", (k,)).fetchone()
        return decrypt(row) if row else None

# --- INTELIGENCIA NLU SVC ---
class OmniNLU:
    def __init__(self):
        self.vec = TfidfVectorizer()
        self.clf = SVC(kernel='linear', probability=True)
        data = [
            ("analiza web", "web"), ("disección url", "web"),
            ("compara archivos", "audit"), ("similitud documentos", "audit"),
            ("punto de quiebre", "finanzas"), ("alza isapre", "finanzas"),
            ("estado sistema", "sys"), ("hola x3", "greet"), ("apagar", "off")
        ]
        t, l = zip(*data)
        self.clf.fit(self.vec.fit_transform(t), l)
    def predict(self, text):
        return self.clf.predict(self.vec.transform([text.lower()]))

# --- NÚCLEO X3 ÉLITE ---
class X3EliteV4:
    def __init__(self):
        self.vault = MemoryVault()
        self.nlu = OmniNLU()
        self.transcript = "Sistemas listos, Alexander."
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    def handle(self, cmd):
        intent = self.nlu.predict(cmd)
        log.info(f"Comando: {cmd} | Intent: {intent}")
        
        if intent == "web":
            url = re.search(r'(https?://[^\s]+)', cmd)
            res = self.scrape(url.group(0)) if url else "Proporcione URL."
        elif intent == "finanzas":
            res = f"APB 2026: Límite alza {ICSA_2026*100}%. Tope imponible {TOPE_UF_2026} UF."
        elif intent == "sys":
            res = f"Sistema: CPU {psutil.cpu_percent()}% | RAM {psutil.virtual_memory().percent}%."
        elif intent == "greet":
            res = f"A sus órdenes, señor {USER_NAME}."
        elif intent == "off":
            self.say("Cerrando protocolos. Adiós.")
            os._exit(0)
        else: res = f"Procesando '{intent}': {cmd}"
        
        self.transcript = res
        self.say(res)

    def scrape(self, url):
        try:
            r = requests.get(url, timeout=5)
            s = BeautifulSoup(r.text, 'html.parser')
            return f"DISECCIÓN {url}: {s.get_text()[:300]}..."
        except: return "Error de red."

    def say(self, text):
        print(f"X3 > {text}")
        async def _s():
            p = BASE_DIR/f"x3_{uuid.uuid4().hex}.mp3"
            await edge_tts.Communicate(text, "es-CL-CatalinaNeural").save(str(p))
            cmd = f"afplay {p}" if sys.platform=="darwin" else f"termux-media-player play {p}"
            os.system(f"{cmd} 2>/dev/null && rm {p}")
        asyncio.run_coroutine_threadsafe(_s(), self.loop)

# --- SERVIDORES (WS + HTTP) ---
async def ws_handler(ws):
    while True:
        try:
            data = {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent, "transcript": x3.transcript}
            await ws.send(json.dumps(data))
            await asyncio.sleep(2)
        except: break

def run_http():
    os.chdir(BASE_DIR)
    with open("index.html", "w") as f:
        f.write("""<!DOCTYPE html><html><head><title>X3 HUD</title>
        <script type="module">
        import * as THREE from 'https://cdn.skypack.dev/three@0.171.0';
        const scene=new THREE.Scene(); const cam=new THREE.PerspectiveCamera(75,window.innerWidth/window.innerHeight,0.1,1000);
        const ren=new THREE.WebGLRenderer({antialias:true,alpha:true}); ren.setSize(window.innerWidth,window.innerHeight);
        document.body.appendChild(ren.domElement);
        const geo=new THREE.IcosahedronGeometry(2,1); const mat=new THREE.MeshBasicMaterial({color:0x00f2ff,wireframe:true});
        const mesh=new THREE.Mesh(geo,mat); scene.add(mesh); cam.position.z=5;
        const ws=new WebSocket('ws://'+location.hostname+':8765');
        ws.onmessage=(e)=>{
            const d=json.parse(e.data);
            document.getElementById('cpu').textContent=d.cpu;
            document.getElementById('log').textContent=d.transcript;
        };
        function animate(){ requestAnimationFrame(animate); mesh.rotation.y+=0.01; ren.render(scene,cam); } animate();
        </script>
        <style>body{margin:0;background:#00050a;color:#00f2ff;font-family:monospace;overflow:hidden}
        #hud{position:fixed;top:20px;left:20px;padding:20px;background:rgba(0,20,40,0.8);border-left:2px solid}
        </style></head><body><div id="hud"><h1>X3 ELITE v4.1</h1>CPU: <span id="cpu">0</span>%<p id="log"></p></div></body></html>""")
    HTTPServer(('', HTTP_PORT), SimpleHTTPRequestHandler).serve_forever()

if __name__ == "__main__":
    x3 = X3EliteV4()
    threading.Thread(target=run_http, daemon=True).start()
    log.info(f"HUD en http://localhost:{HTTP_PORT}")
    
    start_ws = websockets.serve(ws_handler, "0.0.0.0", WS_PORT)
    asyncio.get_event_loop().run_until_complete(start_ws)
    
    rec = sr.Recognizer()
    with sr.Microphone() as source: rec.adjust_for_ambient_noise(source)
    while True:
        try:
            with sr.Microphone() as s: 
                audio = rec.listen(s, timeout=5)
                text = rec.recognize_google(audio, language="es-CL").lower()
                if WAKE_WORD in text: x3.handle(text.replace(WAKE_WORD,"").strip())
        except: pass
