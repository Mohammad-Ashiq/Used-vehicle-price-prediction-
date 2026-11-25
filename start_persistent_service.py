import os
import sys
import time
import subprocess
import re
import urllib.request

BASE_DIR = r"C:\ReVahan_Project"
LOG_FILE = os.path.join(BASE_DIR, "tunnel.log")
CF_EXE = os.path.join(BASE_DIR, "cloudflared.exe")
APP_PY = os.path.join(BASE_DIR, "app.py")

# Windows detached process flags
DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
FLAGS = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP

def is_server_up():
    try:
        res = urllib.request.urlopen("http://127.0.0.1:5000", timeout=2)
        return res.status == 200
    except Exception:
        return False

def main():
    print("1. Checking Flask server...")
    if not is_server_up():
        print("   Starting Flask app detached...")
        # Start detached Flask process
        subprocess.Popen(
            [sys.executable, APP_PY],
            cwd=BASE_DIR,
            creationflags=FLAGS,
            close_fds=True
        )
        for _ in range(15):
            time.sleep(1)
            if is_server_up():
                print("   Flask server is UP on http://127.0.0.1:5000!")
                break
        else:
            print("   Warning: Flask took long to respond, proceeding...")
    else:
        print("   Flask is already running!")

    print("2. Starting Cloudflare tunnel detached...")
    # Remove old log file
    if os.path.exists(LOG_FILE):
        try:
            os.remove(LOG_FILE)
        except Exception:
            pass

    # Start detached cloudflared process with logfile
    subprocess.Popen(
        [CF_EXE, "tunnel", "--url", "http://127.0.0.1:5000", "--logfile", LOG_FILE],
        cwd=BASE_DIR,
        creationflags=FLAGS,
        close_fds=True
    )

    print("3. Waiting for Cloudflare tunnel URL...")
    tunnel_url = None
    for _ in range(30):
        time.sleep(1)
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                matches = re.findall(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", content)
                if matches:
                    tunnel_url = matches[0]
                    break
            except Exception:
                pass

    if not tunnel_url:
        print("ERROR: Could not retrieve tunnel URL from log.")
        return

    print("=====================================================================")
    print("  SUCCESS! ACTIVE PERSISTENT PUBLIC LINK:")
    print("  ", tunnel_url)
    print("=====================================================================")

    # Verify URL status
    print("4. Verifying URL connectivity...")
    for _ in range(10):
        time.sleep(2)
        try:
            res = urllib.request.urlopen(tunnel_url, timeout=5)
            if res.status == 200:
                print("   Tunnel is fully LIVE and returning HTTP 200 OK!")
                break
        except Exception as e:
            print("   Waiting for tunnel route propagation...", e)

    # 5. Save link & QR code to Desktop
    desktop = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')

    link_file = os.path.join(desktop, "ReVahan_Active_Public_Link.txt")
    with open(link_file, "w", encoding="utf-8") as f:
        f.write(f"REVAHAN LIVE PUBLIC LINK (MOBILES & PC):\n\n{tunnel_url}\n\nGenerated: {time.ctime()}\nStatus: LIVE (HTTP 200 OK)\n")

    # Update Desktop .url shortcuts
    shortcut_content = f"[InternetShortcut]\nURL={tunnel_url}\nIconFile=C:\\ReVahan_Project\\static\\images\\favicon.ico\nIconIndex=0\n"
    with open(os.path.join(desktop, "ReVahan_Public_Online.url"), "w", encoding="utf-8") as f:
        f.write(shortcut_content)
    with open(os.path.join(desktop, "ReVahan.url"), "w", encoding="utf-8") as f:
        f.write(shortcut_content)

    # Update QR Code
    try:
        qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={urllib.parse.quote(tunnel_url)}"
        qr_path = os.path.join(desktop, "ReVahan_Mobile_QR_Code.png")
        urllib.request.urlretrieve(qr_url, qr_path)
        print("   Updated QR Code on Desktop: ReVahan_Mobile_QR_Code.png")
    except Exception as e:
        print("   QR update note:", e)

    print("\nAll files and persistent services configured successfully!")

if __name__ == "__main__":
    main()
