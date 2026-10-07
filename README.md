# ⚡ ChronoFlow — Professional Python Countdown & Focus Suite

**ChronoFlow** is a modern, high-precision desktop timer suite built with Python and CustomTkinter. It features a circular gauge visualizer, versatile timer modes (Countdown, Pomodoro, Stopwatch), custom alert chimes, persistent presets, and a floating Picture-in-Picture Mini Mode.

---

## 🌟 Key Features

### 1. ⏳ Precision Countdown Timer
- **Live Circular Progress Arc**: Smooth 50ms animated circular track displaying remaining percentage and time.
- **Quick Adjust Bar**: Live `+1m`, `+5m`, `+10m`, `-1m`, `-5m` adjustment buttons while running or paused.
- **Custom Duration Input**: Direct input for Hours, Minutes, and Seconds.
- **Auto-Repeat / Loop Mode**: Automatically loops timer upon completion (ideal for interval workouts, meditation, or cooking).

### 2. 🍅 Pomodoro Focus System
- **Structured Productivity Cycles**: 25m Focus ➔ 5m Short Break ➔ 15m Long Break every 4 rounds.
- **Visual Streak Badges**: Live indicators tracking rounds (e.g. `🍅 🍅 ⚪ ⚪`).
- **Customizable Intervals**: Easily edit work and rest session lengths.
- **Phase Skip**: Fast-forward between focus and rest sessions with 1 click.

### 3. ⏱️ Millisecond Precision Stopwatch
- Sub-second hundredths precision (`00:00.00`).
- **Lap Recording**: Logs Lap #, Split Time, and Cumulative Total.
- **Smart Highlighting**: Automatically highlights fastest (green) and slowest (red) laps.

### 4. 🗗 Floating Mini Mode (Picture-in-Picture)
- Shrinks to a compact 360×180 floating widget with large digital clock and essential controls.
- Automatically stays **Always-on-Top** so you can keep track while coding, gaming, or studying.
- Hit `M` or click **⤢ Expand** to return to the full dashboard.

### 5. 🔊 High-Quality Audio Alarms
- Zero external audio drivers needed; uses clean synthesized `.wav` sound files:
  - **Digital Chime**
  - **Triple Beep**
  - **Zen Bell**
  - **Windows Asterisk**
  - **Mute / Visual Only**
- Audio test preview button (`🔊`) and dismissable alarm banner.

### 6. 💾 Persistent Presets
- Built-in presets (Deep Focus, Quick Break, Power Nap, Power Hour, HIIT Interval, etc.).
- Save and name custom timers with JSON persistence (`presets.json`).

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Space` | Start / Pause / Resume |
| `R` | Reset Timer |
| `M` | Toggle Mini Floating Mode |
| `Esc` | Exit Mini Mode back to Dashboard |

---

## 🚀 How to Run

1. Make sure Python 3.8+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```
