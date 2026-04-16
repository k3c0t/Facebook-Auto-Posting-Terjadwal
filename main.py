import time, json, os, random, subprocess, re
from datetime import datetime

import undetected_chromedriver as uc
from fake_useragent import UserAgent

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import google.generativeai as genai

# ===================== KONFIGURASI UMUM =====================

COOKIE_FILE = "cookies.json"
HISTORY_FILE = "history.json"
TEXTS_FILE = "texts.txt"
MEDIA_DIR = "media"

SCHEDULE = ["00:50", "15:00", "21:00"]

# ===================== KONFIGURASI AI =======================

# Masukkan API Key Gemini Anda di bawah ini
GEMINI_API_KEY = "API-KEY" 

# ===================== UI & LOGGING =====================

class LogColor:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = f"""{LogColor.CYAN}{LogColor.BOLD}
    =========================================================
        🚀 Fesnuk Feat Gemini - K3C0T - PBM - IDBTE4M 🚀             
    ========================================================={LogColor.RESET}
    """
    print(banner)

def log(level, message):
    ts = datetime.now().strftime("%H:%M:%S")
    
    if level == "INFO": prefix = f"{LogColor.CYAN}[*] INFO   {LogColor.RESET}"
    elif level == "SUCCESS": prefix = f"{LogColor.GREEN}[+] SUCCESS{LogColor.RESET}"
    elif level == "WARNING": prefix = f"{LogColor.YELLOW}[!] WARNING{LogColor.RESET}"
    elif level == "ERROR": prefix = f"{LogColor.RED}[x] ERROR  {LogColor.RESET}"
    elif level == "WAIT": prefix = f"{LogColor.MAGENTA}[~] WAIT   {LogColor.RESET}"
    elif level == "SKIP": prefix = f"{LogColor.YELLOW}[-] SKIP   {LogColor.RESET}"
    elif level == "AI": prefix = f"{LogColor.CYAN}[✦] GEMINI {LogColor.RESET}"
    else: prefix = f"[*] {level.ljust(7)}"

    print(f"{LogColor.BOLD}[{ts}]{LogColor.RESET} {prefix} | {message}")

def log_separator():
    print(f"{LogColor.CYAN}---------------------------------------------------------{LogColor.RESET}")

# ===================== INIT FOLDER & FILE =====================

if not os.path.exists(TEXTS_FILE):
    with open(TEXTS_FILE, "w", encoding="utf-8") as f:
        f.write("Status otomatis pertama 🚀\n\nStatus kedua nih, cek profil ya!\n\nSelamat pagi semuanya!")
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

# ===================== UTILS =====================

def sanitize_text(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)

def human_type(el, text):
    safe_text = sanitize_text(text)
    for c in safe_text:
        el.send_keys(c)
        time.sleep(random.uniform(0.05, 0.15))

def get_chrome_major_version():
    commands = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
    for cmd in commands:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                match = re.search(r'(\d+)\.\d+\.\d+\.\d+', result.stdout)
                if match: return int(match.group(1))
        except FileNotFoundError:
            continue
    return None

def setup_driver():
    ua = UserAgent().random
    options = uc.ChromeOptions()
    options.add_argument(f"user-agent={ua}")
    
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    version = get_chrome_major_version()
    
    if version:
        log("INFO", f"Terdeteksi Chrome versi {version}. Menyesuaikan driver...")
        return uc.Chrome(options=options, version_main=version)
    else:
        log("WARNING", "Gagal mendeteksi versi Chrome otomatis. Menggunakan default...")
        return uc.Chrome(options=options)


# ===================== AI GENERATOR =====================

def generate_ai_caption():
    if not GEMINI_API_KEY:
        return None
        
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 1. Deteksi jam saat ini di VPS
        jam = datetime.now().hour
        
        # 2. Tentukan suasana berdasarkan jam
        if 4 <= jam < 11:
            suasana = "pagi hari (berikan semangat pagi, ngopi, atau bersiap memulai hari)"
        elif 11 <= jam < 15:
            suasana = "siang hari (ingatkan istirahat, makan siang, atau menjaga fokus di tengah hari)"
        elif 15 <= jam < 18:
            suasana = "sore hari (sambut waktu pulang kerja, bersantai, atau evaluasi pencapaian hari ini)"
        else:
            suasana = "malam hari (ucapan selamat istirahat, renungan malam, atau persiapan tidur)"
            
        # 3. Masukkan suasana ke dalam Prompt AI secara dinamis
        prompt = f"""Buatkan 1 caption Facebook yang sangat menarik, natural, dan asik tentang motivasi kerja, bisnis, atau keseharian. 
        Konteks waktu saat ini adalah {suasana}. Wajib sesuaikan kata sapaan pembukanya dengan waktu tersebut!
        Gunakan bahasa Indonesia gaul tapi sopan. Gunakan emoji secukupnya. Jangan kaku seperti robot. Maksimal 3 kalimat pendek. Jangan berikan hashtag."""
        
        response = model.generate_content(prompt)
        if response.text:
            return response.text.strip()
    except Exception as e:
        log("WARNING", f"Gemini API Error: {str(e).splitlines()[0]}")
    
    return None

# ===================== MANAJEMEN KONTEN =====================

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"posted_texts": [], "posted_media": []}

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def get_content():
    history = load_history()
    selected_text = None
    is_ai = False
    
    # 1. Coba Generate Pakai AI
    log("AI", "Mencoba generate caption unik dengan AI...")
    ai_text = generate_ai_caption()
    
    if ai_text:
        selected_text = ai_text
        is_ai = True
        log("AI", "Caption AI berhasil dibuat!")
    else:
        # 2. Fallback: Ambil dari texts.txt jika AI gagal/API kosong
        log("INFO", "Beralih ke texts.txt (AI dinonaktifkan / gagal).")
        with open(TEXTS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            all_texts = [block.strip() for block in re.split(r'\n\s*\n', content) if block.strip()]
        avail_texts = [t for t in all_texts if t not in history["posted_texts"]]
        selected_text = random.choice(avail_texts) if avail_texts else None

    # 3. Ambil Media
    all_media = []
    if os.path.exists(MEDIA_DIR):
        all_media = [f for f in os.listdir(MEDIA_DIR) if os.path.isfile(os.path.join(MEDIA_DIR, f))]
    
    avail_media = [m for m in all_media if m not in history["posted_media"]]
    selected_media = random.choice(avail_media) if avail_media else None
    
    return selected_text, selected_media, history, is_ai

# ===================== CORE =====================

def do_post():
    log_separator()
    text, media_file, history, is_ai = get_content()
    
    if not text and not media_file:
        log("SKIP", "Semua teks manual & media sudah habis! Tambahkan konten baru.")
        return

    log("INFO", "Mempersiapkan Postingan Baru...")
    if text: 
        preview = text.replace('\n', ' ')[:40] + "..." if len(text) > 40 else text.replace('\n', ' ')
        label = "[AI Generated]" if is_ai else "[Manual Text]"
        log("INFO", f"Teks {label} : '{preview}'")
    if media_file: 
        log("INFO", f"Media : {media_file}")
    
    driver = None
    try:
        driver = setup_driver()
        log("INFO", "Membuka browser & menuju Facebook...")
        driver.get("https://www.facebook.com/")
        time.sleep(5)

        if not os.path.exists(COOKIE_FILE):
            log("ERROR", f"File {COOKIE_FILE} tidak ditemukan!")
            return

        with open(COOKIE_FILE, 'r') as f:
            cookies = json.load(f)
            for c in cookies:
                try: 
                    driver.add_cookie({
                        "name": c["name"], "value": c["value"],
                        "domain": c.get("domain", ".facebook.com"), "path": c.get("path", "/")
                    })
                except: pass

        log("INFO", "Menyuntikkan sesi (cookies)...")
        driver.refresh()
        time.sleep(5)

        log("INFO", "Mencari form pembuat status...")
        trigger_xpath = "//span[contains(text(), 'Apa yang Anda pikirkan') or contains(text(), \"What's on your mind\")]"
        btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, trigger_xpath)))
        driver.execute_script("arguments[0].click();", btn)

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']")))
        time.sleep(2)

        if text:
            log("INFO", "Mengetik status...")
            
            # Menggunakan XPath yang secara spesifik menargetkan Lexical Editor terbaru Facebook
            xpath_lexical = "//div[@data-lexical-editor='true' and @contenteditable='true' and @role='textbox']"
            
            try:
                # Tunggu maksimal 10 detik sampai kotak teks benar-benar muncul dan siap
                box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath_lexical))
                )
                
                log("INFO", "Kotak teks Lexical Editor ditemukan!")
                
                # Fokus ke kotak teks sebelum mengetik
                driver.execute_script("arguments[0].focus();", box)
                time.sleep(1)
                
                # Mulai mengetik
                human_type(box, text)
                time.sleep(2)
                
            except Exception as e:
                log("ERROR", "Gagal menemukan kotak teks baru. Pastikan pop-up sudah terbuka sempurna.")
                driver.save_screenshot("error_typing_lexical.png")
                return

        if media_file:
            log("INFO", "Mengunggah media...")
            upload_inputs = driver.find_elements(By.XPATH, "//div[@role='dialog']//input[@type='file']") or driver.find_elements(By.XPATH, "//input[@type='file']")
            if upload_inputs:
                abs_path = os.path.abspath(os.path.join(MEDIA_DIR, media_file))
                upload_inputs[0].send_keys(abs_path)
                time.sleep(12) 
                log("INFO", "Media berhasil terunggah ke form.")
            else:
                log("WARNING", "Input file media tidak ditemukan di halaman.")

        # Logika dinamis untuk melewati wizard video/Reels Facebook
        log("INFO", "Mengecek tahapan wizard / editor Reels...")
        
        # Jeda tambahan sebelum mulai mencari tombol agar animasi upload pertama selesai
        time.sleep(3)
        
        for i in range(3):
            try:
                next_btn_xpath = "//div[@role='button' and (@aria-label='Berikutnya' or @aria-label='Next' or .//span[text()='Berikutnya'] or .//span[text()='Next'])]"
                
                # CARI SEMUA TOMBOL (bukan hanya 1)
                buttons = driver.find_elements(By.XPATH, next_btn_xpath)
                
                clicked = False
                for btn in buttons:
                    # Cek apakah tombol ini benar-benar sedang tampil di layar Anda
                    if btn.is_displayed():
                        try:
                            # Coba klik menggunakan JavaScript
                            driver.execute_script("arguments[0].click();", btn)
                            clicked = True
                            log("INFO", f"Tombol 'Berikutnya' (Tahap {i+1}) ditekan.")
                            break # Hentikan pencarian tombol jika sudah berhasil diklik
                        except Exception as e:
                            continue # Jika gagal klik, coba tombol yang lain
                            
                if not clicked:
                    # Jika tidak ada satupun tombol Berikutnya yang terlihat di layar
                    log("INFO", "Tidak ada tombol 'Berikutnya' lagi di layar. Bersiap memposting...")
                    break 
                
                # Jeda WAJIB untuk menunggu transisi animasi halaman selesai
                time.sleep(4) 
                
            except Exception as e:
                log("INFO", "Selesai melewati tahapan wizard.")
                break 
            
            

        log("INFO", "Menekan tombol Posting...")
        post_btn_xpath = "//div[@role='dialog']//div[@role='button' and (@aria-label='Posting' or @aria-label='Post' or @aria-label='Kirim' or .//span[text()='Post' or text()='Posting'])]"
        post = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, post_btn_xpath)))
        driver.execute_script("arguments[0].click();", post)

        time.sleep(6) 
        log("SUCCESS", "POSTING BERHASIL DIKIRIM KE FACEBOOK!")

        # Hanya simpan ke history jika teks berasal dari manual texts.txt (AI selalu unik)
        if text and not is_ai: history["posted_texts"].append(text)
        if media_file: history["posted_media"].append(media_file)
        save_history(history)

    except Exception as e:
        log("ERROR", f"Terjadi kegagalan proses: {str(e).splitlines()[0]}")

    finally:
        log_separator()
        if driver:
            try: driver.quit()
            except: pass

# ===================== SCHEDULER =====================

def wait_time(t):
    while True:
        now = datetime.now().strftime("%H:%M")
        if now == t:
            return
        time.sleep(20)

def main():
    print_banner()
    log("INFO", "Sistem dijalankan. Memuat konfigurasi...")
    if GEMINI_API_KEY:
        log("AI", "Modul AI Aktif. Caption akan di-generate otomatis.")
    else:
        log("WARNING", "API Key Kosong. Menggunakan mode teks manual.")
        
    log("INFO", f"Jadwal terpantau: {', '.join(SCHEDULE)}")
    log_separator()
    
    while True:
        for t in SCHEDULE:
            log("WAIT", f"Menunggu jadwal pukul {t}...")
            wait_time(t)
            do_post()
            time.sleep(60) 

if __name__ == "__main__":
    main()
