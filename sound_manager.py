"""
Sound Manager for ChronoFlow Countdown Timer.
Generates and plays smooth synthesized alert sounds without external dependencies.
"""

import os
import wave
import math
import struct
import threading
import winsound

SOUNDS_DIR = os.path.join(os.path.dirname(__file__), "sounds")

SOUND_PRESETS = {
    "Digital Chime": "chime.wav",
    "Triple Beep": "beep.wav",
    "Zen Bell": "zen.wav",
    "Windows Asterisk": "system",
    "Mute": "none"
}

def ensure_sound_files():
    """Generates clean WAV sound files if they do not exist."""
    os.makedirs(SOUNDS_DIR, exist_ok=True)
    
    # 1. Chime
    chime_path = os.path.join(SOUNDS_DIR, "chime.wav")
    if not os.path.exists(chime_path):
        _synthesize_wav(chime_path, [(523.25, 0.22), (659.25, 0.22), (783.99, 0.35), (1046.50, 0.7)])

    # 2. Beep
    beep_path = os.path.join(SOUNDS_DIR, "beep.wav")
    if not os.path.exists(beep_path):
        _synthesize_wav(beep_path, [(880, 0.12), (0, 0.05), (880, 0.12), (0, 0.05), (1174.66, 0.35)])

    # 3. Zen Bell
    zen_path = os.path.join(SOUNDS_DIR, "zen.wav")
    if not os.path.exists(zen_path):
        _synthesize_wav(zen_path, [(440, 0.35), (554.37, 0.35), (659.25, 0.85)])

def _synthesize_wav(filepath, notes, sample_rate=44100):
    total_samples = []
    for freq, duration in notes:
        n_samples = int(sample_rate * duration)
        if freq == 0:
            total_samples.extend([0] * n_samples)
            continue
        for i in range(n_samples):
            t = i / sample_rate
            envelope = math.exp(-3.5 * t / duration)
            sample = math.sin(2 * math.pi * freq * t) * envelope
            total_samples.append(int(sample * 28000))
            
    with wave.open(filepath, "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        data = struct.pack("<" + "h" * len(total_samples), *total_samples)
        f.writeframes(data)

class SoundManager:
    def __init__(self):
        ensure_sound_files()
        self.current_sound = "Digital Chime"
        self._is_alarm_playing = False
        self._stop_alarm_event = threading.Event()

    def get_available_sounds(self):
        return list(SOUND_PRESETS.keys())

    def play_sound(self, sound_name=None):
        """Plays the selected sound once asynchronously."""
        name = sound_name or self.current_sound
        if name == "Mute":
            return

        def _play():
            try:
                if name == "Windows Asterisk":
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                else:
                    filename = SOUND_PRESETS.get(name, "chime.wav")
                    filepath = os.path.join(SOUNDS_DIR, filename)
                    if os.path.exists(filepath):
                        winsound.PlaySound(filepath, winsound.SND_FILENAME)
                    else:
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception as e:
                print(f"Sound play error: {e}")

        threading.Thread(target=_play, daemon=True).start()

    def start_alarm_loop(self, loops=3, on_finish=None):
        """Plays repeated alarm notification until stopped or after `loops` times."""
        if self.current_sound == "Mute":
            if on_finish:
                on_finish()
            return

        self.stop_alarm()
        self._stop_alarm_event.clear()
        self._is_alarm_playing = True

        def _loop():
            count = 0
            while not self._stop_alarm_event.is_set() and count < loops:
                try:
                    if self.current_sound == "Windows Asterisk":
                        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                        self._stop_alarm_event.wait(1.0)
                    else:
                        filename = SOUND_PRESETS.get(self.current_sound, "chime.wav")
                        filepath = os.path.join(SOUNDS_DIR, filename)
                        if os.path.exists(filepath):
                            winsound.PlaySound(filepath, winsound.SND_FILENAME)
                        else:
                            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                        self._stop_alarm_event.wait(0.6)
                except Exception as e:
                    print(f"Alarm loop error: {e}")
                count += 1
            
            self._is_alarm_playing = False
            if on_finish:
                on_finish()

        threading.Thread(target=_loop, daemon=True).start()

    def stop_alarm(self):
        self._stop_alarm_event.set()
        self._is_alarm_playing = False
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except Exception:
            pass
