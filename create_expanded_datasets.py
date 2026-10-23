"""
create_expanded_datasets.py — Generate high-quality expanded multi-domain review datasets for OpinionLens.

Adds:
1. dataset/audio_headphones.csv
   - Sony WH-1000XM4 Wireless Headphones (SONY_WH1000XM4) — 135 reviews
   - Apple AirPods Pro 2nd Gen (AIRPODS_PRO_2) — 130 reviews
2. dataset/smartwatches.csv
   - Apple Watch Series 8 (APPLE_WATCH_S8) — 135 reviews
   - Samsung Galaxy Watch 5 (GALAXY_WATCH_5) — 125 reviews
3. dataset/gaming_consoles.csv
   - Sony PlayStation 5 (PS5_CONSOLE) — 140 reviews
   - Valve Steam Deck OLED (STEAM_DECK_OLED) — 130 reviews
4. dataset/smart_home.csv
   - Amazon Echo Dot 5th Gen (ECHO_DOT_GEN5) — 125 reviews
   - Google Nest Cam Battery (NEST_CAM_INDOOR) — 120 reviews
5. Appends to dataset/laptops.csv
   - Dell XPS 15 9530 (DELL_XPS_15) — 125 reviews
   - Lenovo ThinkPad X1 Carbon Gen 11 (THINKPAD_X1_CARBON) — 120 reviews
"""

import csv
import random
from pathlib import Path

DATASET_DIR = Path(__file__).parent / "dataset"
DATASET_DIR.mkdir(parents=True, exist_ok=True)

first_names = [
    "Alexander", "Charlotte", "Daniel", "Elena", "Felix", "Grace", "Henry", "Isla",
    "Jack", "Kavya", "Liam", "Maya", "Nathan", "Olivia", "Pranav", "Quinn",
    "Rohan", "Sophia", "Thomas", "Uma", "Victor", "Wendy", "Xavier", "Yasmine", "Zachary"
]

def make_name(i):
    return f"{random.choice(first_names)} {random.choice(first_names)[0]}. ({i})"

# ==============================================================================
# 1. AUDIO & HEADPHONES (Sony WH-1000XM4 & Apple AirPods Pro 2)
# ==============================================================================
AUDIO_FILE = DATASET_DIR / "audio_headphones.csv"

sony_seed = [
    # Positive majority: ANC, battery, soundstage
    ("Marcus Vance", "u_sony_01", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", 5, "Best noise cancellation on the market", "The active noise cancellation is pure sorcery. It completely silences airplane engine rumble and noisy open-plan offices. Soundstage is warm, bass is deep and punchy, and the 30-hour battery life easily lasts through a week of commutes.", 62, 65, "12-Nov-23"),
    ("Chloe Bennett", "u_sony_02", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", 5, "Unbelievable battery life and multipoint", "Multipoint Bluetooth connection switches seamlessly between my MacBook and iPhone. Ear cups are soft and plush for all-day wearing. LDAC codec delivers superb audio clarity on high-res FLAC files.", 45, 48, "15-Nov-23"),
    ("Arjun Patel", "u_sony_03", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", 4, "Great travel headphones with rich bass", "Comfort is stellar. The folding design fits snugly in the travel case. Quick attention mode by cupping the right ear cup is super handy when ordering coffee.", 30, 32, "19-Nov-23"),

    # Contested: Microphone call quality and touch controls in winter
    ("David Kim", "u_sony_04", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", 2, "Microphone is muffled for Zoom calls", "Audio playback is fantastic, but the built-in microphones are awful for voice calls. Colleagues constantly complain that I sound robotic and distant in meeting rooms.", 58, 62, "23-Nov-23"),
    ("Rachel Green", "u_sony_05", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", 3, "Touch controls are finicky in cold weather", "Swiping for volume on the ear cup is unreliable outdoors during winter. When wearing gloves it doesn't register at all. Physical buttons would have been much better.", 39, 43, "28-Nov-23"),
    ("Kevin Miller", "u_sony_06", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", 4, "Call quality is acceptable indoors", "Microphone picks up some background ambient noise outside, but for quiet indoor home office calls it works perfectly fine.", 22, 25, "02-Dec-23"),

    # Critical Safety Risks: Right ear cup battery overheating & headband bracket fracture
    ("Brian Harris", "u_sony_07", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", 1, "Right ear cup overheating burning hot", "While fast charging via USB-C, the right ear cup became dangerously hot to the touch with an acrid burning odor. The plastic deformed slightly near the hinge. Extreme fire hazard.", 74, 78, "08-Dec-23"),
    ("Laura Simmons", "u_sony_08", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", 1, "Battery swelling inside ear cup", "After 10 months, noticed the right ear pad bulging outwards due to severe battery swelling. Stopped using immediately for fear of battery explosion.", 65, 70, "14-Dec-23"),
    ("Samir Khan", "u_sony_09", "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", 1, "Headband plastic hinge snapped spontaneously", "The swivel hinge bracket snapped cleanly in half while placing them on my head. Thin brittle plastic with no metal reinforcement. Sony denied warranty repair.", 51, 55, "19-Dec-23"),
]

airpods_seed = [
    # Positive majority: Transparency mode, spatial audio, integration
    ("Jessica Taylor", "u_ap_01", "Apple AirPods Pro (2nd Generation)", "AIRPODS_PRO_2", 5, "Transparency mode is basically magic", "Adaptive Transparency mode lets you converse naturally while filtering out harsh construction noises. The H2 chip sound quality is a major leap over Gen 1 with tighter sub-bass and crisp instrument separation.", 59, 63, "10-Oct-23"),
    ("Timothy Clark", "u_ap_02", "Apple AirPods Pro (2nd Generation)", "AIRPODS_PRO_2", 5, "Seamless Apple ecosystem switching", "Touch swipe volume control on the stem is ultra responsive. Precision Finding on the MagSafe case with the built-in speaker saved me twice already when misplaced in the couch.", 42, 45, "14-Oct-23"),
    ("Neha Gupta", "u_ap_03", "Apple AirPods Pro (2nd Generation)", "AIRPODS_PRO_2", 4, "Great noise cancellation for gym", "ANC blocks out loud gym music effortlessly. The XS ear tip size finally fits my smaller ears without falling out during treadmill sprints.", 28, 30, "18-Oct-23"),

    # Contested: Ear tip comfort and silicone seal pressure
    ("Robert Chen", "u_ap_04", "Apple AirPods Pro (2nd Generation)", "AIRPODS_PRO_2", 2, "Ear canal pressure headache after an hour", "The vacuum seal created by the silicone tips creates uncomfortable ear canal pressure. After 45 minutes of wearing I get a dull headache. Had to switch to foam tips.", 47, 51, "24-Oct-23"),
    ("Amanda Scott", "u_ap_05", "Apple AirPods Pro (2nd Generation)", "AIRPODS_PRO_2", 3, "Tips slip out when sweating", "During heavy running or workouts the silicone tips get slick with sweat and loosen every 10 minutes. Requires constant readjusting.", 34, 38, "29-Oct-23"),

    # Critical Safety Risks: MagSafe charging case overheating & ear canal chemical irritation
    ("Derek Foster", "u_ap_06", "Apple AirPods Pro (2nd Generation)", "AIRPODS_PRO_2", 1, "MagSafe case overheated and smelled of smoke", "Case became blistering hot while sitting on the wireless charging pad. Emitted a distinct burning plastic smell and left a scorch mark on the nightstand. Dangerous overheating hazard.", 82, 86, "05-Nov-23"),
    ("Hannah Morales", "u_ap_07", "Apple AirPods Pro (2nd Generation)", "AIRPODS_PRO_2", 1, "Severe ear canal rash and allergic burning", "Developed intense itching, weeping fluid, and chemical burn rash in both ear canals after 3 days. Dermatologist diagnosed allergic contact dermatitis to the silicone tip material.", 68, 73, "12-Nov-23"),
    ("Craig Anderson", "u_ap_08", "Apple AirPods Pro (2nd Generation)", "AIRPODS_PRO_2", 1, "Case battery swelling split the seam", "The MagSafe charging case expanded like a small balloon overnight. The plastic seam cracked open showing internal battery swelling. Apple replaced unit at genius bar.", 71, 75, "18-Nov-23"),
]

audio_rows = []
# Expand Sony WH-1000XM4 to 135 reviews
audio_rows.extend(sony_seed)
for i in range(len(sony_seed), 135):
    rtype = random.choices(["pos", "contested_mic", "contested_touch", "risk_heat", "risk_swelling", "neutral"], weights=[68, 14, 8, 3, 2, 5])[0]
    name = make_name(i)
    uid = f"user_sony_{i}"
    date = f"{random.randint(1, 28)}-Dec-23"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Phenomenal sound and ANC", "Traveler's best friend", "Battery lasts forever", "Supreme comfort"])
        text = random.choice([
            "Noise cancellation is top tier. Sound quality is rich with punchy bass and crystal clear mids.",
            "30 hours of battery life is real. USB-C fast charging gives 5 hours in just 10 minutes.",
            "Very comfortable headband cushion. Can wear on 10 hour international flights without ear fatigue.",
            "Multi-device pairing works great between laptop and phone. High resolution LDAC sound is superb."
        ])
    elif rtype == "contested_mic":
        rating = random.choice([2, 3])
        title = "Microphone quality is lacking"
        text = random.choice([
            "Audio playback is 5 stars, but mic audio for calls sounds muffled and captures background noise.",
            "People say I sound distant on Zoom calls. Mic is definitely the weakest link of these headphones."
        ])
    elif rtype == "contested_touch":
        rating = 3
        title = "Touch gestures can be sluggish"
        text = "Touch sensor on the right ear cup takes some getting used to. Sometimes double tap doesn't register."
    elif rtype == "risk_heat":
        rating = 1
        title = "Dangerous ear cup overheating"
        text = "Right ear cup started overheating severely during normal charging. Smelled burning electrical components."
    elif rtype == "risk_swelling":
        rating = 1
        title = "Severe battery swelling"
        text = "Battery swelling pushed the ear cover outwards. Avoid charging overnight due to serious fire risk."
    else:
        rating = 3
        title = "Good headphones with minor flaws"
        text = "Solid sound quality and good noise cancelling. Companion mobile app has too many unnecessary menus."
    audio_rows.append((name, uid, "Sony WH-1000XM4 Wireless Noise Cancelling Headphones", "SONY_WH1000XM4", rating, title, text, random.randint(1, 30), random.randint(2, 35), date))

# Expand AirPods Pro 2 to 130 reviews
audio_rows.extend(airpods_seed)
for i in range(len(airpods_seed), 130):
    rtype = random.choices(["pos", "contested_fit", "contested_anc", "risk_heat", "risk_burn", "neutral"], weights=[70, 14, 7, 3, 2, 4])[0]
    name = make_name(i + 200)
    uid = f"user_ap_{i}"
    date = f"{random.randint(1, 28)}-Jan-24"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Incredible transparency & ANC", "Must-have for iPhone owners", "Crisp sound and deep bass", "Small case huge sound"])
        text = random.choice([
            "Transparency mode sounds like you aren't wearing earbuds at all. ANC is eerily quiet.",
            "Spatial audio with head tracking makes movies feel like a cinema. MagSafe charging case is pocketable.",
            "Touch volume controls on the stems work reliably. Battery life with case easily lasts 30 hours.",
            "Mic call clarity is great for work calls. H2 chip connectivity with Apple devices is instant."
        ])
    elif rtype == "contested_fit":
        rating = random.choice([2, 3])
        title = "Fit can be loose during jogging"
        text = random.choice([
            "Silicone tips slowly loosen during sweaty runs and lose the bass seal. Needs third-party foam tips.",
            "Slight pressure in ear canal after 2 hours of continuous use. Otherwise audio is great."
        ])
    elif rtype == "contested_anc":
        rating = 3
        title = "ANC firmware updates altered sound"
        text = "Recent firmware update seems to have softened high-frequency noise cancellation slightly."
    elif rtype == "risk_heat":
        rating = 1
        title = "Case overheating and melting charger"
        text = "Charging case became extremely hot to the touch while charging and emitted burning plastic smoke."
    elif rtype == "risk_burn":
        rating = 1
        title = "Severe ear rash and skin irritation"
        text = "Developing itchy red skin rash and burning irritation inside ear canal from the silicone ear tip material."
    else:
        rating = 3
        title = "Good earbuds but expensive"
        text = "High price tag for incremental upgrade over Gen 1. Sound is clean and battery life is standard 6 hours."
    audio_rows.append((name, uid, "Apple AirPods Pro (2nd Generation)", "AIRPODS_PRO_2", rating, title, text, random.randint(1, 28), random.randint(2, 32), date))

with open(AUDIO_FILE, "w", newline="", encoding="latin1") as f:
    writer = csv.writer(f)
    for r in audio_rows:
        writer.writerow(r)
print(f"Created {AUDIO_FILE.name} with {len(audio_rows)} reviews across 2 audio products.")


# ==============================================================================
# 2. SMARTWATCHES & WEARABLES (Apple Watch Series 8 & Samsung Galaxy Watch 5)
# ==============================================================================
WATCHES_FILE = DATASET_DIR / "smartwatches.csv"

aw8_seed = [
    # Positive majority: Display, ECG/health sensors, crash detection, fitness
    ("Markus Thorne", "u_aw_01", "Apple Watch Series 8 (GPS, 45mm Aluminum)", "APPLE_WATCH_S8", 5, "Best smartwatch display and health features", "The always-on retina display is razor sharp even in blazing direct sunlight. Heart rate tracking is spot on compared to my chest strap monitor. Crash detection and ECG give immense peace of mind.", 61, 64, "05-Sep-23"),
    ("Sarah Jenkins", "u_aw_02", "Apple Watch Series 8 (GPS, 45mm Aluminum)", "APPLE_WATCH_S8", 5, "Fitness tracking and watchOS 10 are flawless", "Sleep stage breakdown is surprisingly informative. Apple Pay on wrist makes contactless payments instantaneous. Haptic engine notifications are gentle yet unmissable.", 44, 47, "11-Sep-23"),
    ("Vijay Ramaswamy", "u_aw_03", "Apple Watch Series 8 (GPS, 45mm Aluminum)", "APPLE_WATCH_S8", 4, "Premium build and fast charging", "Fast charging is a huge upgrade: reaches 80% in 45 minutes while I take a shower. Aluminum unibody is durable and lightweight on the wrist.", 32, 35, "18-Sep-23"),

    # Contested: 18-hour battery life (daily charging requirement)
    ("Daniel Craig", "u_aw_04", "Apple Watch Series 8 (GPS, 45mm Aluminum)", "APPLE_WATCH_S8", 2, "Battery life is infuriatingly short", "Having to charge a watch every single day is ridiculous. If you track an outdoor GPS workout and sleep, you barely make it 18 hours before getting low power alerts.", 72, 77, "25-Sep-23"),
    ("Monica Bell", "u_aw_05", "Apple Watch Series 8 (GPS, 45mm Aluminum)", "APPLE_WATCH_S8", 3, "Battery lasts a day and a half at best", "Low Power Mode helps stretch it to 30 hours, but disables always-on display and background heart rate sampling which defeats the purpose.", 38, 42, "02-Oct-23"),

    # Critical Safety Risks: Optical sensor contact dermatitis / skin burn & swollen battery lifting screen
    ("Julian Ross", "u_aw_06", "Apple Watch Series 8 (GPS, 45mm Aluminum)", "APPLE_WATCH_S8", 1, "Skin burn and blistering under sensor", "Optical sensor back glass overheated during an outdoor run, causing a red circular skin burn and blister on my wrist. Had to see a doctor for topical burn cream. Dangerous overheating sensor.", 89, 93, "12-Oct-23"),
    ("Rachel Foster", "u_aw_07", "Apple Watch Series 8 (GPS, 45mm Aluminum)", "APPLE_WATCH_S8", 1, "Battery swelling popped screen off body", "Woke up to find the OLED display completely popped out of the aluminum chassis due to severe lithium battery swelling. Apple Store confirmed battery expansion.", 77, 82, "19-Oct-23"),
    ("Ethan Cole", "u_aw_08", "Apple Watch Series 8 (GPS, 45mm Aluminum)", "APPLE_WATCH_S8", 1, "Extreme overheating while fast charging", "Magnetic fast charger puck and back of watch became scalding hot. Left a brown burn mark on the wood nightstand.", 64, 68, "26-Oct-23"),
]

gw5_seed = [
    # Positive majority: BioActive sensor, sapphire crystal, Wear OS
    ("David Lee", "u_gw_01", "Samsung Galaxy Watch 5 (44mm Bluetooth)", "GALAXY_WATCH_5", 5, "Tough sapphire crystal and great health tools", "Sapphire crystal screen glass is virtually scratch-proof. Body composition BIA sensor provides helpful muscle and body fat metrics. Google Wear OS brings Google Maps and Play Store apps.", 53, 56, "15-Aug-23"),
    ("Ananya Roy", "u_gw_02", "Samsung Galaxy Watch 5 (44mm Bluetooth)", "GALAXY_WATCH_5", 5, "Great companion for Galaxy phone", "Advanced sleep coaching gives personalized tips. Speaker and microphone work well for quick wrist phone calls. Snappy animations with Exynos chip.", 39, 42, "22-Aug-23"),
    ("Christopher Nolan", "u_gw_03", "Samsung Galaxy Watch 5 (44mm Bluetooth)", "GALAXY_WATCH_5", 4, "Durable sports tracker", "Lightweight armor aluminum casing. GPS tracks running routes accurately without phone tethering.", 27, 29, "29-Aug-23"),

    # Contested: ECG and Blood Pressure locked to Samsung phones only
    ("Simon Peter", "u_gw_04", "Samsung Galaxy Watch 5 (44mm Bluetooth)", "GALAXY_WATCH_5", 2, "ECG features locked unless you own a Samsung phone", "If you pair this with a Pixel, OnePlus or Xiaomi phone, Samsung locks the ECG and Blood Pressure monitor behind their proprietary Samsung Health Monitor app. Very anti-consumer.", 69, 73, "06-Sep-23"),
    ("Karen Miller", "u_gw_05", "Samsung Galaxy Watch 5 (44mm Bluetooth)", "GALAXY_WATCH_5", 3, "Battery life is mediocre 2 days", "Better than Apple Watch at around 36 to 40 hours, but still needs charging every second night.", 35, 38, "14-Sep-23"),

    # Critical Safety Risks: Overheating during wireless charging puck & wrist allergic rash
    ("Anthony Wright", "u_gw_06", "Samsung Galaxy Watch 5 (44mm Bluetooth)", "GALAXY_WATCH_5", 1, "Severe overheating on charging puck with burning smell", "Watch displayed overheating warning triangle and shut down while charging. Back glass was blisteringly hot and smelled like burned adhesive. Major battery risk.", 84, 88, "21-Sep-23"),
    ("Lisa Chang", "u_gw_07", "Samsung Galaxy Watch 5 (44mm Bluetooth)", "GALAXY_WATCH_5", 1, "Severe wrist rash and chemical burn", "Suffered redness, severe itching, and blistering rash directly under the nickel sensors. Dermatologist warned against wearing.", 59, 63, "28-Sep-23"),
]

watch_rows = []
watch_rows.extend(aw8_seed)
for i in range(len(aw8_seed), 135):
    rtype = random.choices(["pos", "contested_battery", "risk_burn", "risk_swelling", "neutral"], weights=[68, 18, 3, 3, 8])[0]
    name = make_name(i)
    uid = f"user_aw_{i}"
    date = f"{random.randint(1, 28)}-Nov-23"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Best smartwatch available", "Crisp display and fast", "Heart monitoring gives confidence", "Love watchOS 10"])
        text = random.choice([
            "Always on display is bright and legible in sun. Heart rate and workout tracking are unmatched.",
            "Crash detection and fall detection provide genuine safety. Haptic vibrations feel so natural.",
            "Fast charging means I never worry about battery. 40 minutes on charger while cooking dinner is plenty.",
            "Water resistance for swimming is great. Built in compass and GPS track hikes accurately."
        ])
    elif rtype == "contested_battery":
        rating = random.choice([2, 3])
        title = "Battery barely makes 18 hours"
        text = random.choice([
            "Charging every single day is tedious. Wish it could last 3 full days like competitors.",
            "Outdoor GPS tracking drains battery rapidly. Requires planning charges around sleep tracking."
        ])
    elif rtype == "risk_burn":
        rating = 1
        title = "Severe skin burn from sensor"
        text = "Suffered red skin burn and blister on wrist under optical sensor during workout due to sensor overheating."
    elif rtype == "risk_swelling":
        rating = 1
        title = "Swollen battery lifted glass"
        text = "Internal battery swelling warped and lifted the OLED screen away from the aluminum chassis."
    else:
        rating = 3
        title = "Good watch with minor quirks"
        text = "Good smartwatch features, but expensive accessories and proprietary bands."
    watch_rows.append((name, uid, "Apple Watch Series 8 (GPS, 45mm Aluminum)", "APPLE_WATCH_S8", rating, title, text, random.randint(1, 25), random.randint(2, 30), date))

watch_rows.extend(gw5_seed)
for i in range(len(gw5_seed), 125):
    rtype = random.choices(["pos", "contested_lock", "contested_battery", "risk_heat", "risk_rash", "neutral"], weights=[66, 15, 9, 3, 2, 5])[0]
    name = make_name(i + 300)
    uid = f"user_gw_{i}"
    date = f"{random.randint(1, 28)}-Dec-23"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Great Wear OS smartwatch", "Sapphire glass is scratch proof", "Accurate fitness metrics", "Fast wireless charging"])
        text = random.choice([
            "Sapphire glass has zero scratches despite hitting door frames. Sleep tracking metrics are comprehensive.",
            "Google Wear OS has all necessary apps: Google Maps, Spotify, Keep. Battery lasts full 2 days.",
            "Solid aluminum construction. Microphone and speaker are clear for taking phone calls on wrist.",
            "Body composition scanner matches smart scale measurements. Very impressed with value."
        ])
    elif rtype == "contested_lock":
        rating = random.choice([2, 3])
        title = "Non-Samsung phone restrictions"
        text = "Disappointed that ECG and Blood Pressure features are restricted unless paired with a Samsung phone."
    elif rtype == "contested_battery":
        rating = 3
        title = "Average battery life"
        text = "Battery lasts roughly 36 hours. Better than 1 day but still requires frequent charging."
    elif rtype == "risk_heat":
        rating = 1
        title = "Dangerous overheating on charger"
        text = "Watch suffered severe overheating on wireless charging puck with high temperature warning and burning odor."
    elif rtype == "risk_rash":
        rating = 1
        title = "Sensor contact skin rash"
        text = "Severe allergic contact dermatitis and skin irritation developed directly beneath the rear optical sensor."
    else:
        rating = 3
        title = "Decent watch"
        text = "Decent health tracker with nice screen, but strap can trap sweat during high intensity workouts."
    watch_rows.append((name, uid, "Samsung Galaxy Watch 5 (44mm Bluetooth)", "GALAXY_WATCH_5", rating, title, text, random.randint(1, 25), random.randint(2, 30), date))

with open(WATCHES_FILE, "w", newline="", encoding="latin1") as f:
    writer = csv.writer(f)
    for r in watch_rows:
        writer.writerow(r)
print(f"Created {WATCHES_FILE.name} with {len(watch_rows)} reviews across 2 smartwatch products.")


# ==============================================================================
# 3. GAMING CONSOLES & HANDHELDS (Sony PS5 & Valve Steam Deck OLED)
# ==============================================================================
GAMING_FILE = DATASET_DIR / "gaming_consoles.csv"

ps5_seed = [
    # Positive majority: 4K 60/120fps graphics, DualSense haptics, instant SSD loading
    ("Marcus Brody", "u_ps5_01", "Sony PlayStation 5 Console (Disc Edition)", "PS5_CONSOLE", 5, "Generational leap in graphics and DualSense haptics", "The custom Gen4 NVMe SSD completely eliminates loading screens in Spider-Man 2 and Demon's Souls. The DualSense haptic feedback and adaptive triggers add visceral immersion you have to feel to believe. Whisper quiet cooling.", 88, 92, "10-Jul-23"),
    ("Elena Rostova", "u_ps5_02", "Sony PlayStation 5 Console (Disc Edition)", "PS5_CONSOLE", 5, "Flawless 4K 60fps performance and HDR", "Games look breathtaking on an OLED TV with HDR and 120Hz VRR support. Interface is slick and 3D audio through Pulse 3D headset is positional pinpoint accurate.", 64, 67, "16-Jul-23"),
    ("Tariq Al-Mansoor", "u_ps5_03", "Sony PlayStation 5 Console (Disc Edition)", "PS5_CONSOLE", 4, "Incredible game library and speed", "Backward compatibility with PS4 games at 60fps is a massive plus. Storage expansion slot for M.2 SSD makes adding 2TB seamless.", 41, 44, "23-Jul-23"),

    # Contested: Console physical dimensions and DualSense stick drift
    ("Gareth Evans", "u_ps5_04", "Sony PlayStation 5 Console (Disc Edition)", "PS5_CONSOLE", 2, "DualSense analog stick drift after 5 months", "Both included DualSense controllers developed severe left stick drift within 5 months of normal play. Characters move on their own. Potentiometers wear out way too fast. Sony needs Hall effect sticks.", 95, 100, "30-Jul-23"),
    ("Melissa Brooks", "u_ps5_05", "Sony PlayStation 5 Console (Disc Edition)", "PS5_CONSOLE", 3, "Massive chassis barely fits in entertainment unit", "The console is absurdly tall and bulky. You definitely need vertical clearance and open airflow to prevent heat accumulation in TV cabinets.", 48, 52, "08-Aug-23"),

    # Critical Safety Risks: Power supply coil whine sparking & liquid metal thermal shutdown
    ("Sean O'Connor", "u_ps5_06", "Sony PlayStation 5 Console (Disc Edition)", "PS5_CONSOLE", 1, "Internal power supply spark and burning circuit smell", "Loud pop and sparks came out of the rear exhaust vent while playing Final Fantasy XVI, followed by heavy chemical smoke. Console died immediately. Breaker tripped. Severe electrical fire hazard.", 112, 118, "15-Aug-23"),
    ("Hiroshi Tanaka", "u_ps5_07", "Sony PlayStation 5 Console (Disc Edition)", "PS5_CONSOLE", 1, "Severe overheating thermal shutdown with liquid metal leak", "Console was shutting down after 15 minutes with 'PS5 is too hot' warning. Service shop found liquid metal thermal compound had pooled at the bottom of the APU heatsink due to vertical standing. Catastrophic overheating.", 98, 104, "22-Aug-23"),
    ("Connor Walsh", "u_ps5_08", "Sony PlayStation 5 Console (Disc Edition)", "PS5_CONSOLE", 1, "Extreme coil whine vibrating chassis", "Loud electrical coil whine buzz that can be heard across the room during high GPU load. Sounds like high-voltage arcing.", 71, 76, "29-Aug-23"),
]

deck_seed = [
    # Positive majority: 90Hz OLED HDR screen, handheld PC library, ergonomics, SteamOS
    ("Leo Sterling", "u_sd_01", "Valve Steam Deck OLED (512 GB)", "STEAM_DECK_OLED", 5, "The pinnacle of handheld PC gaming", "The 7.4-inch 90Hz OLED HDR display is drop-dead gorgeous. Deep inky blacks and vibrant colors make Cyberpunk 2077 look stunning. The revised fan is virtually silent and battery life is doubled over the LCD model.", 76, 80, "15-Nov-23"),
    ("Chloe Nguyen", "u_sd_02", "Valve Steam Deck OLED (512 GB)", "STEAM_DECK_OLED", 5, "SteamOS makes PC gaming console-simple", "Sleep and resume function works instantly like a Nintendo Switch. Full access to my entire Steam backlog. Ergonomic grip is comfortable for hours.", 55, 58, "20-Nov-23"),
    ("Devon Bailey", "u_sd_03", "Valve Steam Deck OLED (512 GB)", "STEAM_DECK_OLED", 4, "Great trackpads and emulation powerhouse", "Dual haptic trackpads make mouse-driven strategy games like Civilization playable on a handheld. Emulation performance up to PS2/Switch is stellar.", 38, 41, "27-Nov-23"),

    # Contested: Weight / bulkiness for small hands and battery drain in AAA games
    ("Brenda Cox", "u_sd_04", "Valve Steam Deck OLED (512 GB)", "STEAM_DECK_OLED", 3, "Too heavy for extended handheld sessions without propping", "Weighs nearly 640 grams. While ergonomic, holding it up in bed makes your wrists fatigue after an hour. Definitely a chunky handheld.", 49, 54, "04-Dec-23"),
    ("Jason Rivera", "u_sd_05", "Valve Steam Deck OLED (512 GB)", "STEAM_DECK_OLED", 3, "AAA games still chew through battery in 2 hours", "Indie games like Hades run for 7-8 hours, but demanding titles like Baldur's Gate 3 drain the 50Wh battery in under 2.5 hours at full TDP.", 42, 46, "11-Dec-23"),

    # Critical Safety Risks: Battery swelling warping back plate & charger thermal hazard
    ("Tobias Schmidt", "u_sd_06", "Valve Steam Deck OLED (512 GB)", "STEAM_DECK_OLED", 1, "Battery swelling warped back casing", "After 4 months of heavy play, the internal battery swollen so much that the rear casing seam split and the right shoulder trigger jammed. Major safety hazard.", 88, 93, "18-Dec-23"),
    ("Patrick Hayes", "u_sd_07", "Valve Steam Deck OLED (512 GB)", "STEAM_DECK_OLED", 1, "45W USB-C charger plug melted inside port", "The included 45W power adapter melted the plastic casing inside the top USB-C charging port. Smoke and scorched smell filled the room. Had to RMA entire unit.", 94, 99, "25-Dec-23"),
]

gaming_rows = []
gaming_rows.extend(ps5_seed)
for i in range(len(ps5_seed), 140):
    rtype = random.choices(["pos", "contested_drift", "contested_size", "risk_spark", "risk_heat", "neutral"], weights=[66, 17, 8, 3, 2, 4])[0]
    name = make_name(i)
    uid = f"user_ps5_{i}"
    date = f"{random.randint(1, 28)}-Sep-23"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Phenomenal console power", "Instant load times with SSD", "DualSense haptics are futuristic", "Whisper quiet gaming"])
        text = random.choice([
            "Gen4 SSD makes fast travel truly instantaneous. Graphics on an HDMI 2.1 OLED TV look stunning.",
            "DualSense triggers with adaptive resistance give a unique physical feel to every weapon.",
            "Much quieter cooling than PS4 Pro. Excellent PlayStation Plus library with hundreds of games.",
            "4K 60fps performance mode delivers silky smooth gameplay. Solid industrial build quality."
        ])
    elif rtype == "contested_drift":
        rating = random.choice([2, 3])
        title = "DualSense stick drift problem"
        text = random.choice([
            "Left analog stick started drifting after 4 months of FPS games. Replacement controllers are pricey.",
            "Controllers should use Hall effect magnetic sensors to eliminate potentiometer wear."
        ])
    elif rtype == "contested_size":
        rating = 3
        title = "Very large console footprint"
        text = "Console is bulky and heavy. Needs proper ventilation space in TV entertainment stands."
    elif rtype == "risk_spark":
        rating = 1
        title = "Power supply sparked and popped"
        text = "Console emitted loud electrical sparks from the back power socket followed by burning chemical smoke."
    elif rtype == "risk_heat":
        rating = 1
        title = "Severe thermal overheating shutdown"
        text = "Console suffered catastrophic overheating with thermal warning screens and auto shutoff during 4K gameplay."
    else:
        rating = 3
        title = "Good gaming machine"
        text = "Great exclusives, but 825GB base storage fills up quickly with modern 100GB game installs."
    gaming_rows.append((name, uid, "Sony PlayStation 5 Console (Disc Edition)", "PS5_CONSOLE", rating, title, text, random.randint(1, 35), random.randint(2, 40), date))

gaming_rows.extend(deck_seed)
for i in range(len(deck_seed), 130):
    rtype = random.choices(["pos", "contested_battery", "contested_weight", "risk_swelling", "risk_melt", "neutral"], weights=[68, 16, 7, 3, 2, 4])[0]
    name = make_name(i + 400)
    uid = f"user_sd_{i}"
    date = f"{random.randint(1, 28)}-Jan-24"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["OLED screen is gorgeous", "Handheld PC dream come true", "Great battery on indie games", "Ergonomics are top notch"])
        text = random.choice([
            "90Hz OLED HDR screen has vibrant colors and pure blacks. SteamOS suspend/resume is pure magic.",
            "Can play my entire PC backlog anywhere. Fans are much quieter than original LCD Deck.",
            "Trackpads make desktop navigation and strategy games effortless. Excellent community controller layouts.",
            "Battery life improved by 40-50% over LCD version. High quality thumbsticks and buttons."
        ])
    elif rtype == "contested_battery":
        rating = random.choice([2, 3])
        title = "Heavy battery drain on AAA games"
        text = "High-end 3D games drain the battery in about 2 hours. Keep a 45W power bank handy for travel."
    elif rtype == "contested_weight":
        rating = 3
        title = "Bulky in smaller hands"
        text = "Wide chassis and 640g weight can cause forearm fatigue during marathon gaming sessions."
    elif rtype == "risk_swelling":
        rating = 1
        title = "Battery swelling cracked casing"
        text = "Severe lithium battery swelling pushed against the back case and jammed the right bumper button."
    elif rtype == "risk_melt":
        rating = 1
        title = "USB-C charging port overheating"
        text = "USB-C charging port became scorching hot and melted the connector head during fast charging."
    else:
        rating = 3
        title = "Good handheld with Linux quirks"
        text = "Great device, though anti-cheat in some multiplayer games prevents them from running on SteamOS."
    gaming_rows.append((name, uid, "Valve Steam Deck OLED (512 GB)", "STEAM_DECK_OLED", rating, title, text, random.randint(1, 30), random.randint(2, 35), date))

with open(GAMING_FILE, "w", newline="", encoding="latin1") as f:
    writer = csv.writer(f)
    for r in gaming_rows:
        writer.writerow(r)
print(f"Created {GAMING_FILE.name} with {len(gaming_rows)} reviews across 2 gaming console products.")


# ==============================================================================
# 4. SMART HOME & IOT (Amazon Echo Dot Gen 5 & Google Nest Cam)
# ==============================================================================
SMART_HOME_FILE = DATASET_DIR / "smart_home.csv"

echo_seed = [
    # Positive majority: Alexa voice recognition, improved bass sound, smart home routines
    ("William Harper", "u_ed_01", "Amazon Echo Dot (5th Generation) Smart Speaker", "ECHO_DOT_GEN5", 5, "Surprising bass response and crystal clear Alexa", "The audio upgrade in Gen 5 is noticeable right away: much deeper bass and clear vocal response from a compact sphere. Alexa hears wake words across the room even over music.", 48, 51, "04-Aug-23"),
    ("Grace Kelly", "u_ed_02", "Amazon Echo Dot (5th Generation) Smart Speaker", "ECHO_DOT_GEN5", 5, "Built-in temperature sensor makes routines automated", "Room temperature sensor automatically triggers my smart fan when the bedroom reaches 24C. Tap gesture to pause alarms is super handy on nightstand.", 36, 39, "12-Aug-23"),
    ("Deepak Joshi", "u_ed_03", "Amazon Echo Dot (5th Generation) Smart Speaker", "ECHO_DOT_GEN5", 4, "Great budget smart home speaker", "Matter support makes pairing smart plugs effortless. Crisp sound for podcasts and news briefings in the kitchen.", 25, 27, "19-Aug-23"),

    # Contested: Alexa sponsored advertisements & privacy microphone
    ("Martin Riggs", "u_ed_04", "Amazon Echo Dot (5th Generation) Smart Speaker", "ECHO_DOT_GEN5", 2, "Alexa keeps saying 'By the way' with product recommendations", "Tired of asking for weather and getting an unsolicited pitch: 'By the way, did you know you can order paper towels on Amazon?'. Intrusive advertising.", 68, 73, "27-Aug-23"),
    ("Claire Underwood", "u_ed_05", "Amazon Echo Dot (5th Generation) Smart Speaker", "ECHO_DOT_GEN5", 3, "WiFi drops occasionally on 5GHz band", "Every couple of weeks it loses connection and glows yellow until power-cycled. Works better on 2.4GHz.", 31, 34, "05-Sep-23"),

    # Critical Safety Risks: AC adapter overheating/sparking & sudden loud audio static shrieks
    ("Franklin Moore", "u_ed_06", "Amazon Echo Dot (5th Generation) Smart Speaker", "ECHO_DOT_GEN5", 1, "Power adapter brick overheated and melted outlet", "The 15W wall power plug became scalding hot and started melting the plastic around the wall receptacle. Heavy acrid burning plastic smell. Serious fire hazard.", 79, 83, "14-Sep-23"),
    ("Natalie Portman", "u_ed_07", "Amazon Echo Dot (5th Generation) Smart Speaker", "ECHO_DOT_GEN5", 1, "Sudden electrical pop and internal smoke", "Heard a loud electrical pop from inside the speaker followed by a small puff of smoke. Device is dead. Unplugged immediately.", 67, 72, "22-Sep-23"),
    ("Barry Allen", "u_ed_08", "Amazon Echo Dot (5th Generation) Smart Speaker", "ECHO_DOT_GEN5", 1, "Severe adapter heating burned fingers", "Unplugging the adapter after feeling warmth burned my fingertips. Thermal overload protection failed.", 54, 58, "30-Sep-23"),
]

nest_seed = [
    # Positive majority: 1080p HDR night vision, on-device AI event detection, magnetic mount
    ("Arthur Pendelton", "u_nc_01", "Google Nest Cam (Outdoor or Indoor, Battery)", "NEST_CAM_INDOOR", 5, "Crisp night vision and smart event alerts", "On-device intelligence accurately differentiates between animals, people, vehicles and packages without needing a paid cloud subscription for basic clips. 1080p HDR video is clear even with headlights.", 52, 55, "08-Oct-23"),
    ("Zoe Saldana", "u_nc_02", "Google Nest Cam (Outdoor or Indoor, Battery)", "NEST_CAM_INDOOR", 5, "Magnetic mount makes recharging effortless", "The heavy-duty magnetic base holds the camera securely against steel gutters. Detaches in two seconds to plug in USB-C charger. Google Home app integration is snappy.", 38, 41, "15-Oct-23"),
    ("Vikram Batra", "u_nc_03", "Google Nest Cam (Outdoor or Indoor, Battery)", "NEST_CAM_INDOOR", 4, "Reliable outdoor security camera", "Clean minimalist modern look. Two-way audio lets me speak clearly with delivery drivers through the app.", 29, 31, "22-Oct-23"),

    # Contested: Google Home app vs old Nest app & battery life in winter
    ("Howard Wolowitz", "u_nc_04", "Google Nest Cam (Outdoor or Indoor, Battery)", "NEST_CAM_INDOOR", 2, "Battery drains in 3 weeks during cold winter", "Google claims up to 3 months battery life, but in freezing winter temperatures with busy street activity, the battery drops to zero in under 20 days.", 63, 67, "30-Oct-23"),
    ("Rajesh Koothrappali", "u_nc_05", "Google Nest Cam (Outdoor or Indoor, Battery)", "NEST_CAM_INDOOR", 3, "Google Home app lacks scrubbable timeline of old Nest app", "Migrating from the legacy Nest app to Google Home app is a downgrade for reviewing 24/7 video history.", 44, 48, "08-Nov-23"),

    # Critical Safety Risks: Battery failure in freezing weather & camera housing blistering hot while streaming
    ("Leonard Hofstadter", "u_nc_06", "Google Nest Cam (Outdoor or Indoor, Battery)", "NEST_CAM_INDOOR", 1, "Camera body blistering hot while plugged in outdoor", "When connected to continuous wired power adapter, the aluminum camera body reached scalding temperatures. Battery swelling cracked the rear seal.", 78, 83, "17-Nov-23"),
    ("Bernadette Rosten", "u_nc_07", "Google Nest Cam (Outdoor or Indoor, Battery)", "NEST_CAM_INDOOR", 1, "Battery swelling warped weather seal and ruined lens", "Internal battery swelling pushed against the front glass lens, breaking the IP65 weather seal and letting rain ruin the sensor. Fire hazard.", 69, 74, "25-Nov-23"),
]

smart_home_rows = []
smart_home_rows.extend(echo_seed)
for i in range(len(echo_seed), 125):
    rtype = random.choices(["pos", "contested_ad", "contested_wifi", "risk_heat", "risk_spark", "neutral"], weights=[68, 15, 8, 3, 2, 4])[0]
    name = make_name(i)
    uid = f"user_ed_{i}"
    date = f"{random.randint(1, 28)}-Oct-23"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Great sound for small size", "Alexa makes home automation easy", "Accurate temperature automation", "Clear microphones"])
        text = random.choice([
            "Bass response is surprisingly deep for such a small orb. Sound fills a medium bedroom cleanly.",
            "Far field microphones pick up my voice even with cooking ventilator running. Great timer tool.",
            "Temperature sensor works reliably with smart plugs to turn on space heater. Tap to snooze is great.",
            "Pairs seamlessly with Fire TV Stick as an external speaker. Excellent value for money."
        ])
    elif rtype == "contested_ad":
        rating = random.choice([2, 3])
        title = "Unsolicited Alexa suggestions"
        text = "Alexa is helpful, but the unsolicited product promotions after answering questions are annoying."
    elif rtype == "contested_wifi":
        rating = 3
        title = "Occasional WiFi disconnection"
        text = "Drops WiFi once a month and requires pulling the power cord to reboot."
    elif rtype == "risk_heat":
        rating = 1
        title = "Severe power adapter overheating"
        text = "Power adapter plug became blisteringly hot and scorched the wall outlet with burning plastic smell."
    elif rtype == "risk_spark":
        rating = 1
        title = "Electrical popping and smoke"
        text = "Internal circuit popped loudly with electrical sparks and faint smoke from bottom base."
    else:
        rating = 3
        title = "Decent smart speaker"
        text = "Does the job for morning alarms and Spotify music, but proprietary power plug is annoying."
    smart_home_rows.append((name, uid, "Amazon Echo Dot (5th Generation) Smart Speaker", "ECHO_DOT_GEN5", rating, title, text, random.randint(1, 20), random.randint(2, 25), date))

smart_home_rows.extend(nest_seed)
for i in range(len(nest_seed), 120):
    rtype = random.choices(["pos", "contested_battery", "contested_app", "risk_heat", "risk_swelling", "neutral"], weights=[66, 17, 8, 3, 2, 4])[0]
    name = make_name(i + 500)
    uid = f"user_nc_{i}"
    date = f"{random.randint(1, 28)}-Dec-23"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Top notch video clarity", "Intelligent AI detection", "Super strong magnetic mount", "Clear two-way audio"])
        text = random.choice([
            "1080p HDR footage is crystal clear day and night. Person and package detection is very accurate.",
            "Magnetic mounting system makes taking camera down for charging take 5 seconds.",
            "Clean look and solid weatherproofing. Cloud clip recording works well even without subscription.",
            "Instant notifications when movement detected in driveway. Audio intercom is loud and clear."
        ])
    elif rtype == "contested_battery":
        rating = random.choice([2, 3])
        title = "Battery drains faster in winter"
        text = "Battery life drops significantly when temperatures dip below freezing. Needs frequent recharging."
    elif rtype == "contested_app":
        rating = 3
        title = "Google Home app could be better"
        text = "Reviewing timeline video clips can feel clunky in Google Home compared to older Nest software."
    elif rtype == "risk_heat":
        rating = 1
        title = "Camera body overheating while streaming"
        text = "Metal camera housing becomes scalding hot to the touch during continuous live view."
    elif rtype == "risk_swelling":
        rating = 1
        title = "Battery swelling warped housing"
        text = "Battery swelling ruptured the weatherproof seal around the front lens after 7 months."
    else:
        rating = 3
        title = "Good camera"
        text = "Video quality is high, but 24/7 continuous recording requires wired power cable accessory."
    smart_home_rows.append((name, uid, "Google Nest Cam (Outdoor or Indoor, Battery)", "NEST_CAM_INDOOR", rating, title, text, random.randint(1, 22), random.randint(2, 28), date))

with open(SMART_HOME_FILE, "w", newline="", encoding="latin1") as f:
    writer = csv.writer(f)
    for r in smart_home_rows:
        writer.writerow(r)
print(f"Created {SMART_HOME_FILE.name} with {len(smart_home_rows)} reviews across 2 smart home products.")


# ==============================================================================
# 5. EXPAND LAPTOPS DATASET (Dell XPS 15 & Lenovo ThinkPad X1 Carbon)
# ==============================================================================
LAPTOPS_FILE = DATASET_DIR / "laptops.csv"

dell_seed = [
    # Positive majority: 3.5K OLED display, carbon fiber palm rest, performance
    ("Vincent Chase", "u_xps_01", "Dell XPS 15 9530 (OLED 3.5K, Core i7, RTX 4060)", "DELL_XPS_15", 5, "Breathtaking OLED display and CNC aluminum chassis", "The 3.5K OLED touchscreen has mind-blowing contrast and 100% DCI-P3 color coverage for Lightroom photo grading. CNC machined aluminum and woven carbon fiber palm rest feel insanely luxurious.", 58, 62, "12-Sep-23"),
    ("Eric Murphy", "u_xps_02", "Dell XPS 15 9530 (OLED 3.5K, Core i7, RTX 4060)", "DELL_XPS_15", 5, "Powerhouse laptop for creative workflows", "Intel Core i7 combined with RTX 4060 renders 4K Premiere timelines without stuttering. Quad speakers with Waves MaxxAudio produce rich bass.", 44, 47, "18-Sep-23"),
    ("Ari Gold", "u_xps_03", "Dell XPS 15 9530 (OLED 3.5K, Core i7, RTX 4060)", "DELL_XPS_15", 4, "Sleek workstation with great trackpad", "Glass trackpad is massive and smooth. InfinityEdge thin bezels give an immersive screen-to-body ratio.", 31, 33, "25-Sep-23"),

    # Contested: Fan noise under load and thermal throttling
    ("Lloyd Lee", "u_xps_04", "Dell XPS 15 9530 (OLED 3.5K, Core i7, RTX 4060)", "DELL_XPS_15", 2, "Jet engine fan noise and palm rest heating", "Under combined CPU/GPU load during gaming or rendering, the twin fans ramp up to a loud high-pitched whine. Keyboard deck above function keys becomes uncomfortably hot.", 72, 78, "04-Oct-23"),
    ("Billy Walsh", "u_xps_05", "Dell XPS 15 9530 (OLED 3.5K, Core i7, RTX 4060)", "DELL_XPS_15", 3, "OLED panel drains battery in 5 hours", "The OLED screen looks incredible, but real world battery life drops to roughly 5 to 6 hours of office work.", 39, 43, "12-Oct-23"),

    # Critical Safety Risks: 130W USB-C charger overheating & battery swelling trackpad push
    ("Turtle", "u_xps_06", "Dell XPS 15 9530 (OLED 3.5K, Core i7, RTX 4060)", "DELL_XPS_15", 1, "130W charger brick reached boiling heat with smoking cord", "The Dell 130W USB-C charging brick became too hot to hold and the rubber boot at the connector began melting and smoking. Dangerous electrical hazard.", 88, 93, "20-Oct-23"),
    ("Drama", "u_xps_07", "Dell XPS 15 9530 (OLED 3.5K, Core i7, RTX 4060)", "DELL_XPS_15", 1, "Battery swelling raised glass trackpad until cracked", "Internal battery swelling pushed the glass trackpad upwards until it cracked and stopped clicking. Severe lithium battery safety hazard.", 79, 84, "28-Oct-23"),
]

thinkpad_seed = [
    # Positive majority: Legendary ThinkPad keyboard, lightweight carbon fiber, matte display
    ("Donald Draper", "u_tp_01", "Lenovo ThinkPad X1 Carbon Gen 11 (Core i7, 16GB RAM)", "THINKPAD_X1_CARBON", 5, "The gold standard enterprise typing experience", "Keyboard has 1.5mm key travel, deep tactile feedback, and ergonomic dish-shaped keycaps that make writing long reports a joy. Weighs only 1.12kg (2.48 lbs). Ultra durable carbon fiber lid.", 63, 67, "02-Aug-23"),
    ("Peggy Olson", "u_tp_02", "Lenovo ThinkPad X1 Carbon Gen 11 (Core i7, 16GB RAM)", "THINKPAD_X1_CARBON", 5, "Best road warrior laptop on earth", "Matte anti-glare display eliminates all overhead office fluorescent glare. Full port selection (HDMI 2.0, two Thunderbolt 4, two USB-A) without needing dongles.", 49, 52, "09-Aug-23"),
    ("Roger Sterling", "u_tp_03", "Lenovo ThinkPad X1 Carbon Gen 11 (Core i7, 16GB RAM)", "THINKPAD_X1_CARBON", 4, "Red TrackPoint and stellar build", "TrackPoint nub is indispensable on tight airplane tray tables where you can't use a mouse. Military-grade MIL-STD 810H durability.", 35, 38, "16-Aug-23"),

    # Contested: Modest battery life with Intel 13th Gen P-series & speaker sound
    ("Pete Campbell", "u_tp_04", "Lenovo ThinkPad X1 Carbon Gen 11 (Core i7, 16GB RAM)", "THINKPAD_X1_CARBON", 3, "Intel 13th Gen runs warm and drains battery", "Battery life is around 7-8 hours. The fan spins up during basic multi-tab Chrome browsing and chassis underside gets warm.", 54, 59, "24-Aug-23"),
    ("Joan Holloway", "u_tp_05", "Lenovo ThinkPad X1 Carbon Gen 11 (Core i7, 16GB RAM)", "THINKPAD_X1_CARBON", 3, "Speakers lack bass compared to MacBook", "Down-firing speakers are crisp for conference calls, but music playback sounds thin and hollow.", 28, 31, "01-Sep-23"),

    # Critical Safety Risks: Motherboard USB-C charging circuit burnout & thermal throttling shutdown
    ("Bert Cooper", "u_tp_06", "Lenovo ThinkPad X1 Carbon Gen 11 (Core i7, 16GB RAM)", "THINKPAD_X1_CARBON", 1, "Thunderbolt port sparked and burned motherboard", "While connecting the 65W Lenovo charger, a loud spark came out of the primary Thunderbolt port with burning circuit odor. Laptop went black and failed to power back on.", 84, 89, "10-Sep-23"),
    ("Ken Cosgrove", "u_tp_07", "Lenovo ThinkPad X1 Carbon Gen 11 (Core i7, 16GB RAM)", "THINKPAD_X1_CARBON", 1, "Extreme overheating causing sudden thermal shutdown", "CPU hit 100C within 2 minutes of compiling and laptop shut off without warning. Thermal paste application from factory was completely dry.", 71, 76, "19-Sep-23"),
]

existing_laptops = []
if LAPTOPS_FILE.exists():
    with open(LAPTOPS_FILE, "r", encoding="latin1") as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                existing_laptops.append(row)

filtered_laptops = [r for r in existing_laptops if r[3] not in ("DELL_XPS_15", "THINKPAD_X1_CARBON")]

filtered_laptops.extend(dell_seed)
for i in range(len(dell_seed), 125):
    rtype = random.choices(["pos", "contested_fan", "contested_bat", "risk_charger", "risk_trackpad", "neutral"], weights=[66, 17, 8, 3, 2, 4])[0]
    name = make_name(i + 600)
    uid = f"user_xps_{i}"
    date = f"{random.randint(1, 28)}-Nov-23"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Stunning OLED display", "Creative powerhouse", "Premium aluminum build", "Great quad speakers"])
        text = random.choice([
            "3.5K OLED screen is unbelievable. Blacks are pure, colors pop for photo and video editing.",
            "RTX 4060 graphics handle 3D rendering and video editing with ease. CNC aluminum chassis is sleek.",
            "Massive responsive glass trackpad. Keyboard travel is comfortable for all day typing.",
            "Four speaker sound system provides impressive volume and clarity for music and films."
        ])
    elif rtype == "contested_fan":
        rating = random.choice([2, 3])
        title = "Loud fans and keyboard deck warmth"
        text = "Twin cooling fans get quite loud under gaming loads and palm rest warms up noticeably."
    elif rtype == "contested_bat":
        rating = 3
        title = "OLED battery trade-off"
        text = "Gorgeous display comes with a battery penalty of roughly 5 to 6 hours off the wall plug."
    elif rtype == "risk_charger":
        rating = 1
        title = "Severe charger brick overheating"
        text = "130W USB-C power adapter overheated to a dangerous degree and emitted burning plastic odor."
    elif rtype == "risk_trackpad":
        rating = 1
        title = "Battery swelling raised trackpad"
        text = "Lithium battery swelling warped the bottom chassis and pushed the glass trackpad out of alignment."
    else:
        rating = 3
        title = "Solid high end laptop"
        text = "Great build and screen, but base model only includes USB-C ports requiring adapter dongles."
    filtered_laptops.append((name, uid, "Dell XPS 15 9530 (OLED 3.5K, Core i7, RTX 4060)", "DELL_XPS_15", rating, title, text, random.randint(1, 25), random.randint(2, 30), date))

filtered_laptops.extend(thinkpad_seed)
for i in range(len(thinkpad_seed), 120):
    rtype = random.choices(["pos", "contested_battery", "contested_speaker", "risk_spark", "risk_heat", "neutral"], weights=[68, 16, 7, 3, 2, 4])[0]
    name = make_name(i + 700)
    uid = f"user_tp_{i}"
    date = f"{random.randint(1, 28)}-Dec-23"
    if rtype == "pos":
        rating = random.choice([4, 5])
        title = random.choice(["Unbeatable keyboard feel", "Featherlight executive laptop", "Matte screen cuts glare", "TrackPoint efficiency"])
        text = random.choice([
            "The keyboard remains unmatched in the industry. Tactile, dished keys prevent typing fatigue.",
            "1.1kg carbon fiber chassis makes it the ultimate lightweight business travel machine.",
            "Matte screen eliminates glare in bright conference rooms. Excellent array of legacy and modern ports.",
            "TrackPoint navigation is precise and fast. Sturdy hinges and MIL-STD rugged build."
        ])
    elif rtype == "contested_battery":
        rating = random.choice([2, 3])
        title = "Intel 13th gen battery drain"
        text = "Battery life tops out around 7-8 hours. Fan kicks in during Zoom calls and light multitasking."
    elif rtype == "contested_speaker":
        rating = 3
        title = "Tinny speaker audio"
        text = "Speakers are optimized for voice calls; for music and movies sound lacks low end punch."
    elif rtype == "risk_spark":
        rating = 1
        title = "Thunderbolt port electrical spark"
        text = "Loud spark popped out of Thunderbolt port when connecting dock, resulting in motherboard failure."
    elif rtype == "risk_heat":
        rating = 1
        title = "Thermal shutdown under CPU compile"
        text = "Severe CPU overheating caused sudden emergency shutdown during sustained heavy compilation."
    else:
        rating = 3
        title = "Reliable business laptop"
        text = "Excellent durability and typing experience, though price is steep compared to consumer alternatives."
    filtered_laptops.append((name, uid, "Lenovo ThinkPad X1 Carbon Gen 11 (Core i7, 16GB RAM)", "THINKPAD_X1_CARBON", rating, title, text, random.randint(1, 22), random.randint(2, 28), date))

with open(LAPTOPS_FILE, "w", newline="", encoding="latin1") as f:
    writer = csv.writer(f)
    for r in filtered_laptops:
        writer.writerow(r)
print(f"Updated {LAPTOPS_FILE.name}: now has {len(filtered_laptops)} reviews across 3 flagship laptop models.")

print("\n" + "=" * 60)
print("SUCCESS: All expanded multi-domain datasets generated successfully!")
print("=" * 60)
