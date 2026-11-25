import os
import sys
import time
import subprocess
import re
import urllib.request
import webbrowser

def is_server_running():
    try:
        res = urllib.request.urlopen("http://127.0.0.1:5000", timeout=2)
        return res.status == 200
    except Exception:
        return False

def main():
    print("=" * 65)
    print("       🚗 ReVahan Online Public Server Launcher 🌐")
    print("=" * 65)
    print()

    # 1. Start Flask if not already running
    if is_server_running():
        print("[OK] ReVahan Flask server is already running on http://127.0.0.1:5000")
    else:
        print("[...] Starting ReVahan Flask server...")
        subprocess.Popen([sys.executable, "app.py"], cwd=r"C:\ReVahan_Project")
        for _ in range(15):
            time.sleep(1)
            if is_server_running():
                print("[OK] Flask server started successfully on http://127.0.0.1:5000!")
                break
        else:
            print("[WARN] Server took longer than expected to start, proceeding...")

    # 2. Check if cloudflared exists
    cf_path = r"C:\ReVahan_Project\cloudflared.exe"
    if not os.path.exists(cf_path):
        print(f"[ERROR] cloudflared.exe not found at {cf_path}")
        input("Press Enter to exit...")
        return

    # 3. Start Cloudflare Tunnel and monitor output
    print("[...] Connecting to Cloudflare global network to create public link...")
    proc = subprocess.Popen(
        [cf_path, "tunnel", "--url", "http://127.0.0.1:5000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    tunnel_url = None
    desktop = os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop')
    if not os.path.exists(desktop):
        desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')

    link_file = os.path.join(desktop, "ReVahan_Active_Public_Link.txt")
    shortcut_file = os.path.join(desktop, "ReVahan_Public_Online.url")

    # Read output line by line until we find trycloudflare.com
    for line in iter(proc.stdout.readline, ''):
        line_clean = line.strip()
        if "trycloudflare.com" in line_clean:
            match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line_clean)
            if match and not tunnel_url:
                tunnel_url = match.group(0)
                print()
                print("=" * 65)
                print(" 🎉 YOUR REVAHAN PUBLIC LINK IS READY & ACTIVE FOR ALL MEMBERS!")
                print("=" * 65)
                print(f" 👉 {tunnel_url}")
                print("=" * 65)
                print()
                print("Anyone in the world can open this link right now on phone, PC, etc.")
                print(f"Saved link to your Desktop at: ReVahan_Active_Public_Link.txt")
                print("Opening in Chrome now...")
                print()

                # Save to text file on Desktop
                with open(link_file, "w", encoding="utf-8") as f:
                    f.write(f"ReVahan Live Public Link (Share with all members):\n\n{tunnel_url}\n\nLast Generated: {time.ctime()}\n")

                # Update Desktop .url shortcut
                with open(shortcut_file, "w", encoding="utf-8") as f:
                    f.write(f"[InternetShortcut]\nURL={tunnel_url}\nIconFile=C:\\ReVahan_Project\\static\\images\\favicon.ico\nIconIndex=0\n")

                # Open in browser
                try:
                    webbrowser.open(tunnel_url)
                except Exception:
                    pass

        # Print tunnel status notifications periodically or keep running
        if proc.poll() is not None:
            print("[WARN] Tunnel process disconnected. Reconnecting in 3 seconds...")
            time.sleep(3)
            return main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nStopping...")
