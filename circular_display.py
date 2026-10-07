"""
Circular Progress Display for ChronoFlow Timer.
High-precision canvas widget rendering a circular gauge, digital clock, and status indicators.
"""

import math
import tkinter as tk

class CircularTimerDisplay(tk.Canvas):
    def __init__(self, parent, size=320, bg_color="#182234", **kwargs):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        self.size = size
        self.bg_color = bg_color
        self.center = size / 2
        self.radius = (size / 2) - 24
        self.track_width = 12
        
        # Color palettes
        self.track_color = "#27354a"
        self.accent_color = "#38bdf8"  # Electric cyan default
        self.glow_color = "#0284c7"
        self.text_color = "#f8fafc"
        self.subtext_color = "#94a3b8"
        self.badge_bg = "#1e293b"
        self.badge_fg = "#38bdf8"
        
        # Current state
        self.fraction = 1.0  # 1.0 = full, 0.0 = empty
        self.time_str = "00:00:00"
        self.status_str = "READY"
        self.mode_title = "COUNTDOWN"
        self.subtext = "100% Remaining"
        
        # Pulsing state for completion alert
        self._pulse_state = False
        self._pulsing = False

        self.draw()

    def set_accent_color(self, primary_color, glow_color=None):
        self.accent_color = primary_color
        self.glow_color = glow_color or primary_color
        self.draw()

    def update_display(self, fraction, time_str, status_str="READY", mode_title="COUNTDOWN", subtext=""):
        self.fraction = max(0.0, min(1.0, fraction))
        self.time_str = time_str
        self.status_str = status_str
        self.mode_title = mode_title
        self.subtext = subtext
        self.draw()

    def start_pulse(self):
        """Starts a visual pulsing animation when the timer expires."""
        self._pulsing = True
        self._pulse_tick()

    def stop_pulse(self):
        self._pulsing = False
        self.draw()

    def _pulse_tick(self):
        if not self._pulsing:
            return
        self._pulse_state = not self._pulse_state
        self.draw()
        self.after(500, self._pulse_tick)

    def draw(self):
        self.delete("all")
        cx, cy = self.center, self.center
        r = self.radius
        w = self.track_width
        
        # 1. Subtle background glow halo
        halo_color = "#141e2e"
        self.create_oval(
            cx - r - 8, cy - r - 8,
            cx + r + 8, cy + r + 8,
            fill=halo_color, outline="", width=0
        )

        # 2. Outer Track Arc (360 degrees)
        self.create_arc(
            cx - r, cy - r,
            cx + r, cy + r,
            start=0, extent=359.99,
            style="arc", width=w,
            outline=self.track_color
        )

        # 3. Active Progress Arc
        # Fraction runs from 1.0 down to 0.0 (or 0.0 to 1.0 for stopwatch)
        extent_angle = - (self.fraction * 359.99)
        active_color = "#ef4444" if (self._pulsing and self._pulse_state) else self.accent_color
        
        if abs(extent_angle) > 0.5:
            self.create_arc(
                cx - r, cy - r,
                cx + r, cy + r,
                start=90, extent=extent_angle,
                style="arc", width=w,
                outline=active_color
            )

            # 4. Glowing pip at the head of the arc
            theta_deg = 90 - (self.fraction * 360)
            theta_rad = math.radians(theta_deg)
            pip_x = cx + r * math.cos(theta_rad)
            pip_y = cy - r * math.sin(theta_rad)
            
            pip_radius = w / 2 + 2
            # Outer subtle glow of pip
            self.create_oval(
                pip_x - pip_radius - 2, pip_y - pip_radius - 2,
                pip_x + pip_radius + 2, pip_y + pip_radius + 2,
                fill="", outline=self.glow_color, width=2
            )
            # Solid pip
            self.create_oval(
                pip_x - pip_radius, pip_y - pip_radius,
                pip_x + pip_radius, pip_y + pip_radius,
                fill="#ffffff", outline=active_color, width=2
            )

        # 5. Inner decorative circle
        inner_r = r - 16
        self.create_oval(
            cx - inner_r, cy - inner_r,
            cx + inner_r, cy + inner_r,
            fill="#101927", outline="#1c283d", width=1
        )

        # 6. Mode & Round pill at top
        pill_y = cy - 65
        self.create_text(
            cx, pill_y,
            text=self.mode_title.upper(),
            fill="#7dd3fc",
            font=("Segoe UI", 10, "bold"),
            justify="center"
        )

        # 7. Huge Central Digital Timer
        # Choose font size depending on length of string (e.g. with milliseconds or standard)
        font_size = 36 if len(self.time_str) <= 8 else 30
        self.create_text(
            cx, cy - 8,
            text=self.time_str,
            fill="#f8fafc" if not (self._pulsing and self._pulse_state) else "#f87171",
            font=("Consolas", font_size, "bold"),
            justify="center"
        )

        # 8. Status Badge pill
        badge_y = cy + 42
        badge_text = f"● {self.status_str}" if self.status_str == "RUNNING" else self.status_str
        badge_color = "#10b981" if self.status_str == "RUNNING" else (
            "#f59e0b" if self.status_str == "PAUSED" else (
                "#ef4444" if "TIME'S UP" in self.status_str else "#64748b"
            )
        )
        self.create_text(
            cx, badge_y,
            text=badge_text,
            fill=badge_color,
            font=("Segoe UI", 10, "bold")
        )

        # 9. Subtext / Percentage at bottom of circle
        if self.subtext:
            self.create_text(
                cx, cy + 68,
                text=self.subtext,
                fill="#94a3b8",
                font=("Segoe UI", 9)
            )
