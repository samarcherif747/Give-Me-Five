# 🎯 Give Me Five

> **The Ultimate Team Quiz Game**

A fast-paced, colorful multiplayer quiz game built with Python and Pygame. Challenge your friends in a battle of knowledge across five diverse categories!

[📄 See Poster.pdf](./Poster.pdf)

---

## 🎮 Features

- **5 Dynamic Categories**: General Culture, Current Events, Fun & Random, Sports, Science
- **50 Total Questions**: 10 questions per category with 5 answer options each
- **Timed Gameplay**: 30-second countdown timer per question
- **Scoring System**: Answers ranked by difficulty (1-5 points)
- **Team Battles**: 2-player competitive mode with 10 rounds
- **Beautiful UI**: Dark theme with smooth animations, glows, confetti effects
- **Audio Support**: Click sounds, correct/wrong feedback, background music (optional)
- **Custom Team Names**: Personalize your teams before each game
- **Responsive Design**: 390×700 canvas with smooth scaling

---

## 📋 System Requirements

- **Python 3.10+**
- **Pygame 2.6+**
- **macOS / Linux / Windows**
- **SDL2 Libraries** (for audio support on macOS, handled by Homebrew)

---

## ⚙️ Installation

### 1. Clone or Download

```bash
cd Give-Me-Five
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you're on **macOS** and need audio support:

```bash
brew install sdl2 sdl2_image sdl2_mixer sdl2_ttf sdl2_gfx
```

### 4. Run the Game

```bash
python3 main.py
```

---

## 🎯 How to Play

### Game Flow

1. **Welcome Screen** → Displays logo and game title
2. **Start Screen** → Press "START GAME" to begin
3. **Team Names** → Enter custom names for both teams (or use defaults)
4. **Category Selection** → Choose 1 category (used for entire game)
5. **Game Loop** (10 rounds):
   - Prep screen with rules and countdown
   - 30-second question with 5 answer choices
   - Select all correct answers and submit
   - View results for that round
6. **Final Screen** → See final scores and winner

### Controls

| Action | Control |
| ------ | ------- |
| **Tap/Click** | Select answers or buttons |
| **TAB** | Switch between team name fields |
| **ENTER** | Confirm team names or navigate |
| **BACKSPACE** | Delete text input |
| **Home Button** | Return to start screen anytime |

### Scoring

- **Top Answer** = 5 points
- **2nd Answer** = 4 points
- **3rd Answer** = 3 points
- **4th Answer** = 2 points
- **5th Answer** = 1 point

**Each round:** Select all 5 correct answers to maximize your score.

---

## 🎨 Categories

| Category | Theme | Questions |
| -------- | ----- | --------- |
| 🌍 **General Culture** | Art, history, languages, wonders | 10 |
| 📰 **Current Events** | Tech, social media, AI, crypto | 10 |
| 🎉 **Fun & Random** | Games, food, movies, animals | 10 |
| ⚽ **Sports** | Football, Olympics, athletes, F1 | 10 |
| 🔬 **Science** | Chemistry, biology, elements, space | 10 |

---

## 🎵 Audio Assets (Optional)

To enable audio, place these files in a `give_me_five_audio_pack.zip` or folder:

```plaintext
give_me_five_audio_pack/
├── click.wav
├── correct.wav
├── wrong.wav
├── timer_tick.wav
├── submit.wav
├── win.wav
└── bg_music.wav
```

The game will gracefully handle missing audio files. An audio pack is already included in this repository!

---

## 🖼️ Custom Assets (Optional)

### Logo

Place a `logo.png` file in the game directory to replace the "GMF" text with your custom logo. The logo will be automatically masked into a circle.

---

## 🎨 Game Design

- **Resolution**: 390×700px (1.1× scale to 429×770)
- **Theme**: Dark blue gradient background with accent colors
- **Animation**: Smooth fades, glowing buttons, rotating confetti
- **Fonts**: Cross-platform fallbacks (Segoe UI → Arial → DejaVu Sans)

---

## 📝 File Structure

```plaintext
Give-Me-Five/
├── main.py                        # Main game file
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── Poster.pdf                     # Game poster
├── logo.png                       # (Optional) Custom logo
├── give_me_five_audio_pack.zip    # Audio files
├── give_me_five_audio_pack/       # Extracted audio directory
└── venv/                          # Virtual environment
```

---

## 🚀 Tips & Tricks

- **Prepare mentally**: You have 30 seconds per question—no time for hesitation!
- **Know the order**: Top answers are harder; they're listed first for a reason
- **Strategy**: In competitive rounds, discuss and agree on answers before submitting
- **Replay**: Play different categories for varied difficulty
- **Audio immersion**: Use the audio pack for better game feedback

---

## 🐛 Troubleshooting

### Game won't start

```bash
python3 -m py_compile main.py  # Check syntax
```

### No audio

- Ensure `give_me_five_audio_pack.zip` exists in the game directory
- On macOS, install SDL2: `brew install sdl2`

### Slow performance

- Close other applications
- Check your system's display scaling (runs at 60 FPS)

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE).

Made with ❤️ using **Pygame**

---

## 👥 Credits

- **Framework**: Pygame Community
- **Font Rendering**: Cross-platform system fonts
- **Game Design**: "Give Me Five" Quiz Concept

---

**Ready to test your knowledge? Start a game now!**

```bash
source venv/bin/activate && python3 main.py
```

See **Poster.pdf** for a visual guide to the game!
