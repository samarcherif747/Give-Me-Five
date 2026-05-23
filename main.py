import pygame
import random
import math
import os
import zipfile

pygame.init()
pygame.font.init()

audio_enabled = True
try:
    pygame.mixer.init()
except pygame.error:
    audio_enabled = False

# ═══════════════════════════════════════════════════════════════════════════════
# DISPLAY
# ═══════════════════════════════════════════════════════════════════════════════
CANVAS_W = 390
CANVAS_H = 700
SCALE = 1.1

WIN_W = int(CANVAS_W * SCALE)
WIN_H = int(CANVAS_H * SCALE)

window = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Give Me Five")
surf = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
clock = pygame.time.Clock()

# ═══════════════════════════════════════════════════════════════════════════════
# COLORS
# ═══════════════════════════════════════════════════════════════════════════════
COLOR = {
    "background_top": (12, 14, 35),
    "background_bottom": (18, 22, 52),
    "panel_dark": (24, 30, 70),
    "panel_light": (32, 40, 95),
    "panel_border": (55, 70, 140),
    "blue": (50, 130, 255),
    "purple": (140, 80, 255),
    "pink": (255, 80, 170),
    "gold": (255, 205, 60),
    "green": (60, 210, 120),
    "red": (255, 75, 90),
    "orange": (255, 145, 30),
    "cyan": (0, 210, 230),
    "text_white": (255, 255, 255),
    "text_soft": (200, 215, 255),
    "text_muted": (110, 130, 190),
    "text_dim": (60, 75, 130),
    "team1_blue": (50, 180, 255),
    "team2_pink": (255, 100, 180),
}

BADGE_COLORS = [
    COLOR["gold"],
    COLOR["orange"],
    COLOR["blue"],
    COLOR["purple"],
    COLOR["pink"],
]

# ═══════════════════════════════════════════════════════════════════════════════
# FONTS
# ═══════════════════════════════════════════════════════════════════════════════
def font(size, bold=False):
    for name in ("Segoe UI", "Arial", "DejaVu Sans", None):
        try:
            return pygame.font.SysFont(name, size, bold=bold)
        except Exception:
            pass
    return pygame.font.Font(None, size)

f_hero = font(44, bold=True)
f_heading = font(30, bold=True)
f_button = font(20, bold=True)
f_body = font(18)
f_label = font(14)
f_meta = font(12)
f_big = font(50, bold=True)

# ═══════════════════════════════════════════════════════════════════════════════
# LOGO (circular mask)
# ═══════════════════════════════════════════════════════════════════════════════
def make_circular_logo(image_surface, size):
    scaled = pygame.transform.smoothscale(image_surface, (size, size))
    circular = pygame.Surface((size, size), pygame.SRCALPHA)
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), (size // 2, size // 2), size // 2)
    circular.blit(scaled, (0, 0))
    circular.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return circular

logo = None
if os.path.exists("logo.png"):
    _raw = pygame.image.load("logo.png").convert_alpha()
    logo = make_circular_logo(_raw, 160)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════
QUESTION_TIME = 30
MAX_ROUNDS = 10
MAX_NAME_LEN = 14
WELCOME_DURATION = 2200

# ═══════════════════════════════════════════════════════════════════════════════
# AUDIO
# ═══════════════════════════════════════════════════════════════════════════════
AUDIO_ZIP = "give_me_five_audio_pack.zip"
AUDIO_DIR = "give_me_five_audio_pack"

if os.path.exists(AUDIO_ZIP) and not os.path.exists(AUDIO_DIR):
    try:
        with zipfile.ZipFile(AUDIO_ZIP, "r") as zf:
            zf.extractall(AUDIO_DIR)
    except Exception:
        pass

def audio_path(filename):
    p = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(p): return p
    if os.path.exists(filename): return filename
    return None

def load_sound(filename, volume=1.0):
    if not audio_enabled: return None
    p = audio_path(filename)
    if not p: return None
    try:
        s = pygame.mixer.Sound(p)
        s.set_volume(volume)
        return s
    except pygame.error:
        return None

SOUNDS = {
    "click": load_sound("click.wav", 0.35),
    "correct": load_sound("correct.wav", 0.45),
    "wrong": load_sound("wrong.wav", 0.40),
    "timer_tick": load_sound("timer_tick.wav", 0.30),
    "submit": load_sound("submit.wav", 0.40),
    "win": load_sound("win.wav", 0.50),
}

def play_sound(name):
    s = SOUNDS.get(name)
    if s: s.play()

def start_bg_music():
    if not audio_enabled: return
    p = audio_path("bg_music.wav")
    if not p: return
    try:
        pygame.mixer.music.load(p)
        pygame.mixer.music.set_volume(0.12)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

start_bg_music()

# ═══════════════════════════════════════════════════════════════════════════════
# SCREENS
# ═══════════════════════════════════════════════════════════════════════════════
WELCOME_SCREEN = 0
START_SCREEN = 1
NAMES_SCREEN = 2
CATEGORY_SCREEN = 3
PREP_SCREEN = 4
QUESTION_SCREEN = 5
RESULT_SCREEN = 6
FINAL_SCREEN = 7

current_screen = WELCOME_SCREEN

fading = False
fade_alpha = 0
fade_target = START_SCREEN

def go_to(next_screen):
    global fading, fade_alpha, fade_target
    fading = True
    fade_alpha = 0
    fade_target = next_screen

# ═══════════════════════════════════════════════════════════════════════════════
# GAME STATE
# ═══════════════════════════════════════════════════════════════════════════════
team1_score = 0
team2_score = 0
team1_name = "Team 1"
team2_name = "Team 2"
current_team = 1
round_index = 0
round_score = 0
selected_category = None
current_question = ""
answer_options = []

name_input = ["", ""]
name_field = 0

timer_start = 0
time_left = QUESTION_TIME
last_timer_tick_second = None
welcome_start = pygame.time.get_ticks()

# ═══════════════════════════════════════════════════════════════════════════════
# QUESTION BANK
# ═══════════════════════════════════════════════════════════════════════════════
QUESTION_BANK = {
    "General Culture": [
        ("Name 5 continents",
        [("Africa",5),("Europe",4),("Asia",3),("America",2),("Oceania",1)]),
        ("Name 5 world capitals",
        [("Paris",5),("Tokyo",4),("London",3),("Cairo",2),("Rome",1)]),
        ("Name 5 famous painters",
        [("Picasso",5),("Da Vinci",4),("Van Gogh",3),("Monet",2),("Dali",1)]),
        ("Name 5 world languages",
        [("Mandarin",5),("Spanish",4),("English",3),("Arabic",2),("French",1)]),
        ("Name 5 ancient wonders",
        [("Pyramid of Giza",5),("Colossus",4),("Lighthouse",3),
        ("Hanging Gardens",2),("Temple of Artemis",1)]),
        ("Name 5 famous composers",
        [("Mozart",5),("Beethoven",4),("Bach",3),("Chopin",2),("Vivaldi",1)]),
        ("Name 5 currencies",
        [("Dollar",5),("Euro",4),("Pound",3),("Yen",2),("Franc",1)]),
        ("Name 5 planets",
        [("Mars",5),("Jupiter",4),("Saturn",3),("Venus",2),("Neptune",1)]),
        ("Name 5 Nobel Prize categories",
        [("Peace",5),("Physics",4),("Chemistry",3),("Medicine",2),("Literature",1)]),
        ("Name 5 world religions",
        [("Islam",5),("Christianity",4),("Hinduism",3),("Buddhism",2),("Judaism",1)]),
    ],
    "Current Events": [
        ("Name 5 social media apps",
        [("Instagram",5),("TikTok",4),("Facebook",3),("Twitter",2),("Snapchat",1)]),
        ("Name 5 streaming platforms",
        [("Netflix",5),("Disney+",4),("Spotify",3),("YouTube",2),("Amazon Prime",1)]),
        ("Name 5 tech companies",
        [("Apple",5),("Google",4),("Microsoft",3),("Amazon",2),("Meta",1)]),
        ("Name 5 AI tools",
        [("ChatGPT",5),("Claude",4),("Gemini",3),("Midjourney",2),("Copilot",1)]),
        ("Name 5 smartphone brands",
        [("Apple",5),("Samsung",4),("Xiaomi",3),("Huawei",2),("Google",1)]),
        ("Name 5 electric car brands",
        [("Tesla",5),("Rivian",4),("NIO",3),("Lucid",2),("BMW i",1)]),
        ("Name 5 global organizations",
        [("UN",5),("WHO",4),("NATO",3),("IMF",2),("WTO",1)]),
        ("Name 5 cryptocurrencies",
        [("Bitcoin",5),("Ethereum",4),("Solana",3),("Dogecoin",2),("Ripple",1)]),
        ("Name 5 cloud providers",
        [("AWS",5),("Azure",4),("Google Cloud",3),("IBM Cloud",2),("Oracle",1)]),
        ("Name 5 space agencies",
        [("NASA",5),("ESA",4),("Roscosmos",3),("ISRO",2),("CNSA",1)]),
    ],
    "Fun & Random": [
        ("Name 5 ice cream flavors",
        [("Chocolate",5),("Vanilla",4),("Strawberry",3),("Mint",2),("Caramel",1)]),
        ("Name 5 pizza toppings",
        [("Cheese",5),("Pepperoni",4),("Mushroom",3),("Olives",2),("Onion",1)]),
        ("Name 5 board games",
        [("Chess",5),("Monopoly",4),("Scrabble",3),("Risk",2),("Clue",1)]),
        ("Name 5 superhero movies",
        [("Avengers",5),("Batman",4),("Spider-Man",3),("Superman",2),("Iron Man",1)]),
        ("Name 5 types of pasta",
        [("Spaghetti",5),("Penne",4),("Fettuccine",3),("Lasagna",2),("Rigatoni",1)]),
        ("Name 5 cartoon characters",
        [("Mickey Mouse",5),("Bugs Bunny",4),("Tom",3),("Scooby-Doo",2),("SpongeBob",1)]),
        ("Name 5 musical instruments",
        [("Guitar",5),("Piano",4),("Violin",3),("Drums",2),("Trumpet",1)]),
        ("Name 5 dog breeds",
        [("Labrador",5),("Poodle",4),("Bulldog",3),("Beagle",2),("Husky",1)]),
        ("Name 5 cat breeds",
        [("Persian",5),("Siamese",4),("Maine Coon",3),("Bengal",2),("Sphynx",1)]),
        ("Name 5 TV show genres",
        [("Drama",5),("Comedy",4),("Thriller",3),("Documentary",2),("Reality",1)]),
    ],
    "Sports": [
        ("Name 5 football clubs",
        [("Real Madrid",5),("Barcelona",4),("Man United",3),("Bayern",2),("Juventus",1)]),
        ("Name 5 Olympic sports",
        [("Swimming",5),("Athletics",4),("Gymnastics",3),("Cycling",2),("Boxing",1)]),
        ("Name 5 famous athletes",
        [("Messi",5),("Ronaldo",4),("LeBron James",3),("Usain Bolt",2),("Serena Williams",1)]),
        ("Name 5 NBA teams",
        [("Lakers",5),("Bulls",4),("Warriors",3),("Heat",2),("Celtics",1)]),
        ("Name 5 F1 teams",
        [("Ferrari",5),("Mercedes",4),("Red Bull",3),("McLaren",2),("Alpine",1)]),
        ("Name 5 combat sports",
        [("Boxing",5),("MMA",4),("Judo",3),("Wrestling",2),("Karate",1)]),
        ("Name 5 ball sports",
        [("Football",5),("Basketball",4),("Tennis",3),("Volleyball",2),("Rugby",1)]),
        ("Name 5 swimming strokes",
        [("Freestyle",5),("Backstroke",4),("Breaststroke",3),("Butterfly",2),("Medley",1)]),
        ("Name 5 World Cup host countries",
        [("Brazil",5),("France",4),("Germany",3),("South Africa",2),("Russia",1)]),
        ("Name 5 Grand Slam tournaments",
        [("Wimbledon",5),("Roland Garros",4),("US Open",3),("Australian Open",2),("Davis Cup",1)]),
    ],
    "Science": [
        ("Name 5 elements on the periodic table",
        [("Oxygen",5),("Carbon",4),("Hydrogen",3),("Gold",2),("Iron",1)]),
        ("Name 5 bones in the human body",
        [("Femur",5),("Skull",4),("Tibia",3),("Radius",2),("Sternum",1)]),
        ("Name 5 types of energy",
        [("Solar",5),("Nuclear",4),("Wind",3),("Kinetic",2),("Thermal",1)]),
        ("Name 5 famous scientists",
        [("Einstein",5),("Newton",4),("Curie",3),("Darwin",2),("Hawking",1)]),
        ("Name 5 programming languages",
        [("Python",5),("JavaScript",4),("Java",3),("C++",2),("Ruby",1)]),
        ("Name 5 blood types",
        [("A+",5),("B+",4),("O+",3),("AB+",2),("O-",1)]),
        ("Name 5 vitamins",
        [("Vitamin C",5),("Vitamin D",4),("Vitamin A",3),("Vitamin B12",2),("Vitamin E",1)]),
        ("Name 5 states of matter",
        [("Solid",5),("Liquid",4),("Gas",3),("Plasma",2),("BEC",1)]),
        ("Name 5 human organs",
        [("Heart",5),("Lungs",4),("Liver",3),("Brain",2),("Kidneys",1)]),
        ("Name 5 atmosphere layers",
        [("Troposphere",5),("Stratosphere",4),("Mesosphere",3),
        ("Thermosphere",2),("Exosphere",1)]),
    ],
}

CAT_NAMES = list(QUESTION_BANK.keys())
# Short 2-letter abbreviations that fit perfectly inside the 44px icon circle
CAT_ABBR = ["GC", "CE", "FR", "SP", "SC"]
CAT_COLORS = [
    COLOR["blue"],
    COLOR["pink"],
    COLOR["gold"],
    COLOR["green"],
    COLOR["purple"],
]

used_questions = {cat: [] for cat in QUESTION_BANK}

# ═══════════════════════════════════════════════════════════════════════════════
# CONFETTI
# ═══════════════════════════════════════════════════════════════════════════════
confetti = []

def spawn_confetti(n=30):
    for _ in range(n):
        confetti.append({
            "x": random.randint(0, CANVAS_W),
            "y": random.randint(-30, 0),
            "vx": random.uniform(-1.5, 1.5),
            "vy": random.uniform(2, 5),
            "r": random.randint(4, 9),
            "color": random.choice([
                COLOR["gold"], COLOR["pink"], COLOR["cyan"],
                COLOR["green"], COLOR["purple"], COLOR["blue"],
            ]),
            "shape": random.choice(["rect", "circle"]),
            "rot": random.uniform(0, 360),
            "spin": random.uniform(-4, 4),
            "opacity": 1.0,
        })

def draw_confetti():
    dead = []
    for p in confetti:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["rot"] = (p["rot"] + p["spin"]) % 360
        p["opacity"] -= 0.007
        if p["opacity"] <= 0 or p["y"] > CANVAS_H + 20:
            dead.append(p); continue
        a = int(p["opacity"] * 255)
        sz = p["r"] * 2
        tile = pygame.Surface((sz, sz), pygame.SRCALPHA)
        rgba = (*p["color"][:3], a)
        if p["shape"] == "circle":
            pygame.draw.circle(tile, rgba, (p["r"], p["r"]), p["r"])
        else:
            pygame.draw.rect(tile, rgba, (0, 0, sz, p["r"]))
        rt = pygame.transform.rotate(tile, p["rot"])
        surf.blit(rt, (int(p["x"]) - rt.get_width()//2, int(p["y"]) - rt.get_height()//2))
    for d in dead:
        if d in confetti: confetti.remove(d)

# ═══════════════════════════════════════════════════════════════════════════════
# DRAW HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def draw_rrect(surface, fill, rect, radius=14, bw=0, bc=None):
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    if bw and bc:
        pygame.draw.rect(surface, bc, rect, bw, border_radius=radius)

def draw_glow(surface, color, cx, cy, r, max_a=50):
    gc = pygame.Surface((r*4, r*4), pygame.SRCALPHA)
    for i in range(4):
        pygame.draw.circle(gc, (*color, max(0, max_a - i*12)), (r*2, r*2), r + i*9)
    surface.blit(gc, (cx - r*2, cy - r*2))

def draw_tc(surface, text, fnt, color, cx, cy, max_w=None):
    s = fnt.render(text, True, color)
    if max_w and s.get_width() > max_w:
        s = pygame.transform.smoothscale(s, (max_w, s.get_height()))
    surface.blit(s, (cx - s.get_width()//2, cy - s.get_height()//2))

def draw_tl(surface, text, fnt, color, lx, ty):
    surface.blit(fnt.render(text, True, color), (lx, ty))

def draw_wrapped(surface, text, fnt, color, cx, cy, max_w, lh=24):
    words = text.split()
    lines, line = [], ""
    for w in words:
        cand = (line + " " + w).strip()
        if fnt.size(cand)[0] <= max_w:
            line = cand
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    sy = cy - len(lines)*lh//2
    for ln in lines:
        draw_tc(surface, ln, fnt, color, cx, sy + lh//2)
        sy += lh

def draw_home_button():
    btn = BTN_HOME
    draw_rrect(surf, COLOR["panel_light"], btn, radius=9)
    il, it, iw, ih = btn.x+8, btn.y+4, btn.width-16, btn.height-8
    cx = il + iw//2
    rb = it + ih//2
    pygame.draw.polygon(surf, COLOR["text_muted"], [(cx, it+2), (il, rb), (il+iw, rb)])
    pygame.draw.rect(surf, COLOR["text_muted"], pygame.Rect(il+3, rb, iw-6, ih//2))
    pygame.draw.rect(surf, COLOR["panel_light"], pygame.Rect(cx-4, rb+4, 8, ih//2-4))

# ═══════════════════════════════════════════════════════════════════════════════
# STATIC BACKGROUND
# ═══════════════════════════════════════════════════════════════════════════════
bg = pygame.Surface((CANVAS_W, CANVAS_H))
for _y in range(CANVAS_H):
    t = _y / CANVAS_H
    c = tuple(int(COLOR["background_top"][i] + (COLOR["background_bottom"][i] - COLOR["background_top"][i]) * t) for i in range(3))
    pygame.draw.line(bg, c, (0, _y), (CANVAS_W, _y))
for _x in range(0, CANVAS_W, 28):
    for _y in range(0, CANVAS_H, 28):
        pygame.draw.circle(bg, (28, 34, 76), (_x, _y), 1)

# ═══════════════════════════════════════════════════════════════════════════════
# BUTTON RECTS
# ═══════════════════════════════════════════════════════════════════════════════
BTN_START = pygame.Rect(70, 430, 250, 56)
BTN_NAMES_OK = pygame.Rect(70, 590, 250, 56)
BTN_PREP_GO = pygame.Rect(70, 580, 250, 54)
BTN_SUBMIT = pygame.Rect(55, 626, 280, 50)
BTN_NEXT = pygame.Rect(95, 618, 200, 50)
BTN_RESTART = pygame.Rect(95, 576, 200, 56)
BTN_HOME = pygame.Rect(10, 10, 44, 34)

NAME_BOXES = [
    pygame.Rect(40, 290, CANVAS_W - 80, 52),
    pygame.Rect(40, 430, CANVAS_W - 80, 52),
]

# ═══════════════════════════════════════════════════════════════════════════════
# GAME HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def pick_question(category):
    pool = QUESTION_BANK[category]
    avail = [i for i in range(len(pool)) if i not in used_questions[category]]
    if not avail:
        used_questions[category].clear()
        avail = list(range(len(pool)))
    idx = random.choice(avail)
    used_questions[category].append(idx)
    return pool[idx]

def make_answer_cards(raw):
    opts = []
    for i, (text, pts) in enumerate(raw):
        opts.append({
            "text": text,
            "points": pts,
            "rect": pygame.Rect(16, 215 + i*76, CANVAS_W - 32, 64),
            "selected": False,
        })
    return opts

def calc_score():
    return sum(o["points"] for o in answer_options if o["selected"])

def tname(n):
    raw = team1_name if n == 1 else team2_name
    return raw.strip() if raw.strip() else f"Team {n}"

def tcol():
    return COLOR["team1_blue"] if current_team == 1 else COLOR["team2_pink"]

def reset_game():
    global team1_score, team2_score, team1_name, team2_name
    global current_team, round_index, used_questions
    global selected_category, name_input, name_field, last_timer_tick_second
    team1_score = team2_score = 0
    team1_name = "Team 1"; team2_name = "Team 2"
    current_team = 1; round_index = 0
    used_questions = {c: [] for c in QUESTION_BANK}
    selected_category = None
    name_input = ["", ""]; name_field = 0
    last_timer_tick_second = None

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════════
tick = 0
running = True

while running:
    tick += 1
    mx_r, my_r = pygame.mouse.get_pos()
    mx, my = mx_r / SCALE, my_r / SCALE
    now = pygame.time.get_ticks()

    # Auto-advance welcome
    if current_screen == WELCOME_SCREEN and not fading:
        if now - welcome_start > WELCOME_DURATION:
            go_to(START_SCREEN)

    # Timer
    if current_screen == QUESTION_SCREEN and not fading:
        elapsed = (now - timer_start) // 1000
        time_left = max(0, QUESTION_TIME - elapsed)
        if 1 <= time_left <= 5 and time_left != last_timer_tick_second:
            play_sound("timer_tick")
            last_timer_tick_second = time_left
        if time_left == 0:
            round_score = calc_score()
            if current_team == 1: team1_score += round_score
            else: team2_score += round_score
            play_sound("correct" if round_score > 0 else "wrong")
            go_to(RESULT_SCREEN)

    # ── EVENTS ────────────────────────────────────────────────────────────────
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and current_screen == NAMES_SCREEN and not fading:
            if event.key == pygame.K_TAB:
                name_field = 1 - name_field
            elif event.key == pygame.K_RETURN:
                if name_field == 0:
                    name_field = 1
                else:
                    team1_name = name_input[0].strip() or "Team 1"
                    team2_name = name_input[1].strip() or "Team 2"
                    go_to(CATEGORY_SCREEN)
            elif event.key == pygame.K_BACKSPACE:
                name_input[name_field] = name_input[name_field][:-1]
            else:
                if len(name_input[name_field]) < MAX_NAME_LEN:
                    name_input[name_field] += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and not fading:

            # Home button (available on all screens except welcome/start/names)
            if current_screen not in (WELCOME_SCREEN, START_SCREEN, NAMES_SCREEN):
                if BTN_HOME.collidepoint(mx, my):
                    play_sound("click"); reset_game(); confetti.clear()
                    go_to(START_SCREEN)

            if current_screen == START_SCREEN:
                if BTN_START.collidepoint(mx, my):
                    play_sound("click"); go_to(NAMES_SCREEN)

            elif current_screen == NAMES_SCREEN:
                for fi, box in enumerate(NAME_BOXES):
                    if box.collidepoint(mx, my):
                        play_sound("click"); name_field = fi
                if BTN_NAMES_OK.collidepoint(mx, my):
                    play_sound("click")
                    team1_name = name_input[0].strip() or "Team 1"
                    team2_name = name_input[1].strip() or "Team 2"
                    go_to(CATEGORY_SCREEN)

            elif current_screen == CATEGORY_SCREEN:
                for ci, cname in enumerate(CAT_NAMES):
                    row = pygame.Rect(18, 158 + ci * 92, CANVAS_W - 36, 78)
                    if row.collidepoint(mx, my):
                        play_sound("click"); selected_category = cname
                        go_to(PREP_SCREEN)

            elif current_screen == PREP_SCREEN:
                if BTN_PREP_GO.collidepoint(mx, my):
                    play_sound("click")
                    q, raw = pick_question(selected_category)
                    current_question = q
                    answer_options = make_answer_cards(raw)
                    time_left = QUESTION_TIME
                    timer_start = now
                    last_timer_tick_second = None
                    go_to(QUESTION_SCREEN)

            elif current_screen == QUESTION_SCREEN:
                for o in answer_options:
                    if o["rect"].collidepoint(mx, my):
                        o["selected"] = not o["selected"]; play_sound("click")
                if BTN_SUBMIT.collidepoint(mx, my):
                    play_sound("submit")
                    round_score = calc_score()
                    if current_team == 1: team1_score += round_score
                    else: team2_score += round_score
                    play_sound("correct" if round_score > 0 else "wrong")
                    go_to(RESULT_SCREEN)

            elif current_screen == RESULT_SCREEN:
                if BTN_NEXT.collidepoint(mx, my):
                    play_sound("click"); round_index += 1
                    if round_index >= MAX_ROUNDS:
                        spawn_confetti(60); play_sound("win"); go_to(FINAL_SCREEN)
                    else:
                        current_team = 2 if current_team == 1 else 1
                        go_to(PREP_SCREEN)

            elif current_screen == FINAL_SCREEN:
                if BTN_RESTART.collidepoint(mx, my):
                    play_sound("click"); reset_game(); confetti.clear()
                    go_to(START_SCREEN)

    # ── FADE ──────────────────────────────────────────────────────────────────
    if fading:
        fade_alpha += 16
        if fade_alpha >= 255:
            current_screen = fade_target
            fading = False; fade_alpha = 0
            if current_screen == FINAL_SCREEN:
                spawn_confetti(50)

    # ══════════════════════════════════════════════════════════════════════════
    # DRAW
    # ══════════════════════════════════════════════════════════════════════════
    surf.blit(bg, (0, 0))

    # Stars
    for si in range(14):
        a = (tick * 0.5 + si * 26) % 360
        sx = int(CANVAS_W * (((si * 137) % 97) / 97))
        sy = int(CANVAS_H * (((si * 83) % 97) / 97))
        sr = 1 + int(math.sin(math.radians(a)) > 0.5)
        pygame.draw.circle(surf, COLOR["text_dim"], (sx, sy), sr)

    draw_confetti()
    team_col = tcol()

    # ── WELCOME ───────────────────────────────────────────────────────────────
    if current_screen == WELCOME_SCREEN:
        orb_r = 108 + int(abs(math.sin(math.radians(tick * 2))) * 6)
        draw_glow(surf, COLOR["blue"], CANVAS_W//2, 268, orb_r, 45)
        pygame.draw.circle(surf, COLOR["panel_dark"], (CANVAS_W//2, 268), orb_r)
        pygame.draw.circle(surf, COLOR["blue"], (CANVAS_W//2, 268), orb_r, 3)
        if logo:
            surf.blit(logo, (CANVAS_W//2 - 80, 188))
        else:
            draw_tc(surf, "GMF", f_big, COLOR["gold"], CANVAS_W//2, 258)
        draw_tc(surf, "Give Me Five!", f_hero, COLOR["text_white"], CANVAS_W//2, 375)
        draw_tc(surf, "The Ultimate Team Quiz", f_label, COLOR["text_muted"], CANVAS_W//2, 410)
        filled = min(int((now - welcome_start) / WELCOME_DURATION * 180), 180)
        draw_rrect(surf, COLOR["panel_light"], pygame.Rect(CANVAS_W//2 - 90, 450, 180, 6), radius=3)
        draw_rrect(surf, COLOR["blue"], pygame.Rect(CANVAS_W//2 - 90, 450, filled, 6), radius=3)

    # ── START ─────────────────────────────────────────────────────────────────
    elif current_screen == START_SCREEN:
        draw_glow(surf, COLOR["purple"], CANVAS_W//2, 220, 120, 38)
        pygame.draw.circle(surf, COLOR["panel_dark"], (CANVAS_W//2, 220), 118)
        pygame.draw.circle(surf, COLOR["purple"], (CANVAS_W//2, 220), 118, 3)
        if logo:
            surf.blit(logo, (CANVAS_W//2 - 80, 140))
        else:
            draw_tc(surf, "GMF", f_big, COLOR["gold"], CANVAS_W//2, 212)
        draw_tc(surf, "Give Me Five!", f_hero, COLOR["text_white"], CANVAS_W//2, 362)
        draw_tc(surf, "The Ultimate Team Quiz", f_label, COLOR["text_muted"], CANVAS_W//2, 395)
        draw_glow(surf, COLOR["blue"], BTN_START.centerx, BTN_START.centery, 38, 28)
        draw_rrect(surf, COLOR["blue"], BTN_START, radius=28)
        draw_tc(surf, "START GAME", f_button, COLOR["text_white"], BTN_START.centerx, BTN_START.centery)

    # ── NAMES ─────────────────────────────────────────────────────────────────
    elif current_screen == NAMES_SCREEN:
        draw_tc(surf, "Name Your Teams", f_hero, COLOR["text_white"], CANVAS_W//2, 90)
        draw_tc(surf, "Tap a box and start typing", f_label, COLOR["text_muted"], CANVAS_W//2, 128)
        labels = ["Team 1 Name", "Team 2 Name"]
        fcols = [COLOR["team1_blue"], COLOR["team2_pink"]]
        for fi in range(2):
            box = NAME_BOXES[fi]
            fc = fcols[fi]
            focused = (fi == name_field)
            draw_tl(surf, labels[fi], f_label, fc, box.x + 6, box.y - 26)
            draw_rrect(surf, COLOR["panel_light"], box, radius=14,
            bw=3 if focused else 1, bc=fc if focused else COLOR["panel_border"])
            typed = name_input[fi]
            ts = f_body.render(typed if typed else "e.g. The Champions", True,
            COLOR["text_white"] if typed else COLOR["text_dim"])
            mw = box.width - 24
            if ts.get_width() > mw:
                ts = pygame.transform.smoothscale(ts, (mw, ts.get_height()))
            surf.blit(ts, (box.x + 14, box.centery - ts.get_height()//2))
            if focused and (tick // 30) % 2 == 0:
                cx = box.x + 14 + ts.get_width() + 2
                pygame.draw.line(surf, fc, (cx, box.centery-12), (cx, box.centery+12), 2)
        draw_glow(surf, COLOR["blue"], BTN_NAMES_OK.centerx, BTN_NAMES_OK.centery, 36, 26)
        draw_rrect(surf, COLOR["blue"], BTN_NAMES_OK, radius=28)
        draw_tc(surf, "LET'S PLAY ->", f_button, COLOR["text_white"],
        BTN_NAMES_OK.centerx, BTN_NAMES_OK.centery)
        draw_tc(surf, "TAB to switch | ENTER to confirm",
        f_meta, COLOR["text_dim"], CANVAS_W//2, 658)

    # ── CATEGORY ──────────────────────────────────────────────────────────────
    elif current_screen == CATEGORY_SCREEN:
        draw_home_button()
        draw_tc(surf, "Choose Your Category", f_heading, COLOR["text_white"], CANVAS_W//2, 60)
        draw_tc(surf, "This category is used for the whole game",
        f_meta, COLOR["text_muted"], CANVAS_W//2, 92)

        # Team name pills
        pw = (CANVAS_W - 46) // 2
        p1 = pygame.Rect(18, 110, pw, 36)
        p2 = pygame.Rect(p1.right + 10, 110, pw, 36)
        draw_rrect(surf, COLOR["panel_light"], p1, radius=18, bw=2, bc=COLOR["team1_blue"])
        draw_rrect(surf, COLOR["panel_light"], p2, radius=18, bw=2, bc=COLOR["team2_pink"])
        draw_tc(surf, tname(1), f_label, COLOR["team1_blue"], p1.centerx, p1.centery, pw-10)
        draw_tc(surf, tname(2), f_label, COLOR["team2_pink"], p2.centerx, p2.centery, pw-10)

        for ci, cname in enumerate(CAT_NAMES):
            acc = CAT_COLORS[ci]
            abbr = CAT_ABBR[ci]
            row = pygame.Rect(18, 158 + ci * 92, CANVAS_W - 36, 78)
            hov = row.collidepoint(mx, my)

            draw_rrect(surf, COLOR["panel_dark"] if hov else COLOR["panel_light"],
            row, radius=16, bw=2, bc=acc)

            # Left color stripe
            draw_rrect(surf, acc, pygame.Rect(row.x+1, row.y+12, 4, row.height-24), radius=2)

            # Icon circle — fixed size 44x44, starts at row.x+14
            ic_rect = pygame.Rect(row.x + 14, row.centery - 22, 44, 44)
            ic_surf = pygame.Surface((44, 44), pygame.SRCALPHA)
            pygame.draw.circle(ic_surf, (*acc, 50), (22, 22), 22)
            pygame.draw.circle(ic_surf, (*acc, 200), (22, 22), 22, 2)
            surf.blit(ic_surf, ic_rect.topleft)
            # Abbreviation centered inside circle using f_label (small enough to fit)
            draw_tc(surf, abbr, f_label, acc, ic_rect.centerx, ic_rect.centery)

            # Text zone: starts right of icon (x+14+44+8 = x+66), ends before arrow
            ICON_END = 66 # relative to row.x
            ARROW_ZONE = 28
            txt_start = row.x + ICON_END + 8
            txt_width = row.width - ICON_END - 8 - ARROW_ZONE
            txt_cx = txt_start + txt_width // 2

            draw_tc(surf, cname, f_button, COLOR["text_white"],
            txt_cx, row.centery - 10, txt_width)
            draw_tc(surf, f"{len(QUESTION_BANK[cname])} questions",
            f_meta, COLOR["text_muted"],
            txt_cx, row.centery + 14, txt_width)

            if hov:
                arr = f_button.render(">", True, acc)
                surf.blit(arr, (row.right - 22, row.centery - arr.get_height()//2))

    # ── PREP ──────────────────────────────────────────────────────────────────
    elif current_screen == PREP_SCREEN:
        draw_home_button()
        tag = pygame.Rect(CANVAS_W//2 - 78, 8, 156, 32)
        draw_rrect(surf, team_col, tag, radius=16)
        draw_tc(surf, f"{tname(current_team)}'s Turn",
        f_meta, COLOR["text_white"], tag.centerx, tag.centery, tag.width-10)

        ci = CAT_NAMES.index(selected_category)
        cat_col = CAT_COLORS[ci]
        cat_abbr = CAT_ABBR[ci]
        oy = 220

        draw_glow(surf, cat_col, CANVAS_W//2, oy, 106, 42)
        pygame.draw.circle(surf, COLOR["panel_dark"], (CANVAS_W//2, oy), 104)
        pygame.draw.circle(surf, cat_col, (CANVAS_W//2, oy), 104, 3)
        # Logo inside orb if available, else large abbreviation
        if logo:
            surf.blit(logo, (CANVAS_W//2 - 80, oy - 80))
        else:
            draw_tc(surf, cat_abbr, f_heading, cat_col, CANVAS_W//2, oy)

        draw_tc(surf, "Get Ready!", f_hero, COLOR["text_white"], CANVAS_W//2, 352)
        pill = pygame.Rect(CANVAS_W//2 - 80, 372, 160, 30)
        draw_rrect(surf, cat_col, pill, radius=15)
        draw_tc(surf, selected_category, f_meta, COLOR["text_white"], pill.centerx, pill.centery)

        rules = [("*", "Name all 5 answers"), ("-", "30 seconds on the clock"), ("+", "Top answers score more")]
        for ri, (icon, txt) in enumerate(rules):
            ry = 424 + ri * 46
            rr = pygame.Rect(28, ry, CANVAS_W - 56, 36)
            draw_rrect(surf, COLOR["panel_light"], rr, radius=10, bw=1, bc=COLOR["panel_border"])
            draw_tl(surf, icon, f_label, COLOR["gold"], 42, ry + 9)
            draw_tl(surf, txt, f_label, COLOR["text_soft"], 58, ry + 9)

        draw_glow(surf, cat_col, BTN_PREP_GO.centerx, BTN_PREP_GO.centery, 36, 28)
        draw_rrect(surf, cat_col, BTN_PREP_GO, radius=27)
        draw_tc(surf, "LET'S GO!", f_button, COLOR["text_white"],
        BTN_PREP_GO.centerx, BTN_PREP_GO.centery)

    # ── QUESTION ──────────────────────────────────────────────────────────────
    elif current_screen == QUESTION_SCREEN:
        draw_home_button()
        # Score strip
        ss = pygame.Rect(62, 10, CANVAS_W - 72, 30)
        draw_rrect(surf, COLOR["panel_light"], ss, radius=9)
        draw_tl(surf, f"{tname(1)} {team1_score}", f_meta, COLOR["team1_blue"], 70, ss.centery-8)
        t2t = f_meta.render(f"{tname(2)} {team2_score}", True, COLOR["team2_pink"])
        surf.blit(t2t, (CANVAS_W - 14 - t2t.get_width(), ss.centery - 8))
        # Timer bar
        tf = time_left / QUESTION_TIME
        tbc = COLOR["green"] if tf > 0.5 else COLOR["gold"] if tf > 0.25 else COLOR["red"]
        draw_rrect(surf, COLOR["panel_light"], pygame.Rect(14, 48, CANVAS_W-28, 14), radius=7)
        fw = int((CANVAS_W-28) * tf)
        if fw > 0: draw_rrect(surf, tbc, pygame.Rect(14, 48, fw, 14), radius=7)
        draw_tc(surf, f"{time_left}s", f_meta, tbc, CANVAS_W//2, 40)
        # Team tag
        at = pygame.Rect(CANVAS_W//2 - 68, 68, 136, 26)
        draw_rrect(surf, team_col, at, radius=13)
        draw_tc(surf, tname(current_team), f_meta, COLOR["text_white"], at.centerx, at.centery, at.width-10)
        # Question box
        qb = pygame.Rect(14, 100, CANVAS_W-28, 72)
        draw_rrect(surf, COLOR["panel_light"], qb, radius=14, bw=2, bc=COLOR["gold"])
        draw_wrapped(surf, current_question, f_body, COLOR["text_white"],
        qb.centerx, qb.centery, qb.width-22, 24)
        # Answer cards
        for o in answer_options:
            hov = o["rect"].collidepoint(mx, my)
            if o["selected"]:
                fc, bc = (22, 78, 48), COLOR["green"]
            elif hov:
                fc, bc = COLOR["panel_dark"], COLOR["blue"]
            else:
                fc, bc = COLOR["panel_light"], COLOR["panel_border"]
            draw_rrect(surf, fc, o["rect"], radius=14, bw=2, bc=bc)
            # Badge
            badge = pygame.Rect(o["rect"].x+9, o["rect"].centery-13, 30, 26)
            draw_rrect(surf, BADGE_COLORS[5-o["points"]], badge, radius=13)
            draw_tc(surf, str(o["points"]), f_meta, COLOR["text_white"], badge.centerx, badge.centery)
            # Answer text
            mw = o["rect"].width - 58
            ts = f_body.render(o["text"], True, COLOR["text_white"])
            if ts.get_width() > mw: ts = pygame.transform.smoothscale(ts, (mw, ts.get_height()))
            surf.blit(ts, (o["rect"].x+46, o["rect"].centery - ts.get_height()//2))
            if o["selected"]:
                draw_tc(surf, "V", f_button, COLOR["green"], o["rect"].right-20, o["rect"].centery)
        # Submit
        draw_glow(surf, team_col, BTN_SUBMIT.centerx, BTN_SUBMIT.centery, 34, 22)
        draw_rrect(surf, team_col, BTN_SUBMIT, radius=25)
        draw_tc(surf, "SUBMIT ANSWERS", f_button, COLOR["text_white"],
        BTN_SUBMIT.centerx, BTN_SUBMIT.centery)

    # ── RESULT ────────────────────────────────────────────────────────────────
    elif current_screen == RESULT_SCREEN:
        draw_home_button()
        rt = pygame.Rect(CANVAS_W//2 - 78, 8, 156, 32)
        draw_rrect(surf, team_col, rt, radius=16)
        draw_tc(surf, tname(current_team), f_meta, COLOR["text_white"], rt.centerx, rt.centery, rt.width-10)
        draw_tc(surf, str(round_score), f_big, COLOR["gold"], CANVAS_W//2, 88)
        draw_tc(surf, "points this round", f_label, COLOR["text_muted"], CANVAS_W//2, 122)
        pygame.draw.line(surf, COLOR["panel_border"], (28, 140), (CANVAS_W-28, 140), 1)
        draw_tc(surf, "Correct Answers", f_label, COLOR["text_muted"], CANVAS_W//2, 156)
        top = 170
        for o in answer_options:
            rr = pygame.Rect(14, top, CANVAS_W-28, 70)
            sel = o["selected"]
            draw_rrect(surf, (18,62,38) if sel else (58,20,30), rr, radius=13,
            bw=2, bc=COLOR["green"] if sel else COLOR["red"])
            badge = pygame.Rect(rr.x+9, rr.centery-13, 30, 26)
            draw_rrect(surf, BADGE_COLORS[5-o["points"]], badge, radius=13)
            draw_tc(surf, str(o["points"]), f_meta, COLOR["text_white"], badge.centerx, badge.centery)
            mw = rr.width - 62
            ts = f_body.render(o["text"], True, COLOR["text_white"])
            if ts.get_width() > mw: ts = pygame.transform.smoothscale(ts, (mw, ts.get_height()))
            surf.blit(ts, (rr.x+46, rr.centery - ts.get_height()//2))
            mark = "V" if sel else "X"
            draw_tc(surf, mark, f_button, COLOR["green"] if sel else COLOR["red"],
            rr.right-20, rr.centery)
            top += 76
        tots = pygame.Rect(14, top+2, CANVAS_W-28, 34)
        draw_rrect(surf, COLOR["panel_light"], tots, radius=10)
        draw_tl(surf, f"{tname(1)}: {team1_score}", f_meta, COLOR["team1_blue"], 22, tots.centery-8)
        t2t = f_meta.render(f"{tname(2)}: {team2_score}", True, COLOR["team2_pink"])
        surf.blit(t2t, (CANVAS_W-22-t2t.get_width(), tots.centery-8))
        lbl = "FINAL SCORES" if round_index + 1 >= MAX_ROUNDS else "NEXT ROUND ->"
        draw_rrect(surf, COLOR["blue"], BTN_NEXT, radius=25)
        draw_tc(surf, lbl, f_button, COLOR["text_white"], BTN_NEXT.centerx, BTN_NEXT.centery)

    # ── FINAL ─────────────────────────────────────────────────────────────────
    elif current_screen == FINAL_SCREEN:
        spawn_confetti(2)
        draw_tc(surf, "GAME OVER", f_heading, COLOR["gold"], CANVAS_W//2, 62)
        if team1_score > team2_score:
            wt, wc = f"{tname(1)} Wins!", COLOR["team1_blue"]
        elif team2_score > team1_score:
            wt, wc = f"{tname(2)} Wins!", COLOR["team2_pink"]
        else:
            wt, wc = "It's a Tie!", COLOR["gold"]
        draw_glow(surf, wc, CANVAS_W//2, 170, 100, 42)
        wb = pygame.Rect(44, 108, CANVAS_W-88, 118)
        draw_rrect(surf, COLOR["panel_dark"], wb, radius=20, bw=3, bc=wc)
        draw_tc(surf, "#1", f_heading, wc, CANVAS_W//2, 138)
        draw_tc(surf, wt, f_hero, wc, CANVAS_W//2, 188, wb.width-20)
        s1 = pygame.Rect(18, 252, 164, 128)
        s2 = pygame.Rect(208, 252, 164, 128)
        draw_rrect(surf, COLOR["panel_light"], s1, radius=18, bw=3, bc=COLOR["team1_blue"])
        draw_rrect(surf, COLOR["panel_light"], s2, radius=18, bw=3, bc=COLOR["team2_pink"])
        for card, score, name, col in [
            (s1, team1_score, tname(1), COLOR["team1_blue"]),
            (s2, team2_score, tname(2), COLOR["team2_pink"]),
        ]:
            draw_tc(surf, name, f_label, col, card.centerx, card.y+24, card.width-10)
            draw_tc(surf, str(score), f_big, COLOR["text_white"], card.centerx, card.y+72)
            draw_tc(surf, "pts", f_meta, COLOR["text_muted"], card.centerx, card.y+108)
        draw_tc(surf, f"{MAX_ROUNDS} rounds | {selected_category}",
        f_meta, COLOR["text_muted"], CANVAS_W//2, 398)
        draw_tc(surf, f"Winning margin: {abs(team1_score-team2_score)} pts",
        f_meta, COLOR["text_dim"], CANVAS_W//2, 420)
        pygame.draw.line(surf, COLOR["panel_border"], (28, 444), (CANVAS_W-28, 444), 1)
        draw_tc(surf, "Want a rematch?", f_label, COLOR["text_muted"], CANVAS_W//2, 464)
        draw_glow(surf, COLOR["purple"], BTN_RESTART.centerx, BTN_RESTART.centery, 36, 26)
        draw_rrect(surf, COLOR["purple"], BTN_RESTART, radius=28)
        draw_tc(surf, "PLAY AGAIN", f_button, COLOR["text_white"],
        BTN_RESTART.centerx, BTN_RESTART.centery)

    # ── FADE OVERLAY ──────────────────────────────────────────────────────────
    if fading:
        fo = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)
        fo.fill((*COLOR["background_top"], min(fade_alpha, 255)))
        surf.blit(fo, (0, 0))

    window.blit(pygame.transform.smoothscale(surf, (WIN_W, WIN_H)), (0, 0))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
