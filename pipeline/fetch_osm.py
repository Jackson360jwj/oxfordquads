import subprocess, os, time
W,S,E,N = -1.2765, 51.7435, -1.2385, 51.7765
COLS, ROWS = 4, 4                      # 16 tiles keeps each under the 50k node cap
os.makedirs("tiles", exist_ok=True)
dx, dy = (E-W)/COLS, (N-S)/ROWS
ok = 0
for r in range(ROWS):
    for c in range(COLS):
        w, s = W + c*dx, S + r*dy
        e, n = w + dx, s + dy
        f = f"tiles/t{r}{c}.xml"
        if os.path.exists(f) and os.path.getsize(f) > 5000:
            ok += 1; continue
        url = f"https://api.openstreetmap.org/api/0.6/map?bbox={w:.5f},{s:.5f},{e:.5f},{n:.5f}"
        code = subprocess.run(["curl","-sS","-L","--max-time","180","-H","User-Agent: OxfordCollegeAccess/1.0",
                               url,"-o",f,"-w","%{http_code}"], capture_output=True, text=True).stdout.strip()
        size = os.path.getsize(f) if os.path.exists(f) else 0
        print(f"  tile {r}{c}  HTTP {code}  {size//1024} KB", flush=True)
        if code == "200" and size > 5000: ok += 1
        time.sleep(1.2)
print(f"{ok}/{COLS*ROWS} tiles fetched")
