"""Daily free wallpaper (run by .github/workflows/free-wallpaper.yml).

Expects the decrypted pool in $POOL (manifest.json, <scene>_{phone,tablet,desktop}.png, <scene>_thumb.png). Picks today's
scene (every scene once in a shuffled order before any repeat, never the same two days running),
puts only that scene in free/, and points catalog.json's freeSample/freebie at it.
"""
import datetime, glob, json, os, random, shutil

POOL = os.environ["POOL"]
scenes = json.load(open(f"{POOL}/manifest.json"))
cat = json.load(open("catalog.json"))
today = datetime.date.today()
current = (cat.get("freeSample") or {}).get("scene")
fs = cat.get("freeSample") or {}
if fs.get("day") == today.isoformat() and fs.get("files"):
    print(f"already picked today: {cat['freeSample']['title']}")   # reruns never skip ahead
    raise SystemExit(0)

n = len(scenes)
cycle, i = divmod(today.toordinal(), n)
order = sorted(scenes, key=lambda s: (s["week"], s["scene"]))
random.Random(f"pixel-free-{n}-{cycle}").shuffle(order)
pick = order[i]
if fs.get("day") == today.isoformat():          # today's scene already chosen; only its files change
    pick = next((s for s in scenes if s["scene"] == current), pick)
elif pick["scene"] == current:
    pick = order[(i + 1) % n]

os.makedirs("free", exist_ok=True)
for old in glob.glob("free/*"):
    os.remove(old)
files = {}
for dev in ("phone", "tablet", "desktop"):
    files[dev] = f"free/pixel.by.pixel.art_{pick['slug']}_{dev}.png"
    shutil.copy(f"{POOL}/{pick['scene']}_{dev}.png", files[dev])
shutil.copy(f"{POOL}/{pick['scene']}_thumb.png", "free/thumb.png")
cat["freeSample"] = {"scene": pick["scene"], "title": pick["title"], "files": files, "day": today.isoformat()}
cat["freebie"] = {"week": pick["week"], "scene": pick["scene"], "title": pick["title"],
                  "blurb": f"Try one before you buy: today's {pick['title']} scene, free, full quality, "
                           "for phone, tablet and desktop."}
with open("catalog.json", "w") as f:
    json.dump(cat, f, indent=2, ensure_ascii=False)
print(f"free wallpaper is now {pick['title']}")
