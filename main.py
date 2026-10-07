"""
ChronoFlow - Professional Countdown Timer & Focus Suite
Built with CustomTkinter for sleek modern visuals, circular progress tracking,
Pomodoro focus workflows, precision stopwatch, and audio alarms.
"""

import sys
import os
import time
import math
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from sound_manager import SoundManager
from circular_display import CircularTimerDisplay
from preset_manager import PresetManager

# App Configuration
APP_NAME = "ChronoFlow"
APP_VERSION = "2.0 Pro"

# Color Palette
BG_DARK = "#0b1120"
CARD_BG = "#151e2e"
CARD_BORDER = "#1e293b"
ACCENT_CYAN = "#38bdf8"
ACCENT_ROSE = "#f43f5e"
ACCENT_EMERALD = "#10b981"
ACCENT_PURPLE = "#a855f7"
ACCENT_AMBER = "#f59e0b"
TEXT_MUTED = "#94a3b8"
TEXT_LIGHT = "#f8fafc"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ChronoFlowApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title(f"{APP_NAME} • Professional Timer")
        self.geometry("900x680")
        self.minsize(780, 600)
        self.configure(fg_color=BG_DARK)

        # Managers
        self.sound_mgr = SoundManager()
        self.preset_mgr = PresetManager()

        # Timer State
        self.mode = "COUNTDOWN"  # COUNTDOWN, POMODORO, STOPWATCH
        self.is_running = False
        self.is_paused = False
        
        # Countdown time in seconds
        self.total_seconds = 25 * 60  # Default 25 minutes
        self.remaining_seconds = float(self.total_seconds)
        self.last_tick_time = 0.0
        self.loop_timer = False

        # Pomodoro State
        self.pomo_focus_min = 25
        self.pomo_short_break_min = 5
        self.pomo_long_break_min = 15
        self.pomo_cycle_goal = 4
        self.pomo_current_cycle = 1
        self.pomo_stage = "FOCUS"  # FOCUS, SHORT_BREAK, LONG_BREAK

        # Stopwatch State
        self.stopwatch_elapsed = 0.0
        self.stopwatch_laps = []

        # Mini mode state
        self.is_mini_mode = False
        self.normal_geometry = "900x680"

        # Alarm completion banner state
        self.alarm_active = False

        # Build GUI
        self._init_layout()
        self._bind_shortcuts()
        self._update_timer_visuals()

        # Start master update loop
        self.after(100, self._master_tick)

    def _init_layout(self):
        # Master grid container
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 1. Top Header Navigation
        self.header_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=0, height=64)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Brand / Logo
        brand_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=20, pady=12, sticky="w")
        
        logo_label = ctk.CTkLabel(
            brand_frame,
            text="⚡ " + APP_NAME.upper(),
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=ACCENT_CYAN
        )
        logo_label.pack(side="left")

        sub_label = ctk.CTkLabel(
            brand_frame,
            text=" " + APP_VERSION,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="normal"),
            text_color=TEXT_MUTED
        )
        sub_label.pack(side="left", padx=(4, 0))

        # Mode Selector Tabs
        self.mode_selector = ctk.CTkSegmentedButton(
            self.header_frame,
            values=["⏳ Countdown", "🍅 Pomodoro", "⏱️ Stopwatch"],
            command=self._on_mode_changed,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            selected_color="#0284c7",
            selected_hover_color="#0369a1",
            unselected_color="#1e293b",
            unselected_hover_color="#334155",
            height=36
        )
        self.mode_selector.set("⏳ Countdown")
        self.mode_selector.grid(row=0, column=1, padx=20, pady=14)

        # Right Header Utilities
        util_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        util_frame.grid(row=0, column=2, padx=20, pady=12, sticky="e")

        # Always on top switch
        self.top_switch = ctk.CTkSwitch(
            util_frame,
            text="Pin on Top",
            command=self._toggle_always_on_top,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED,
            progress_color=ACCENT_CYAN,
            switch_width=38,
            switch_height=20
        )
        self.top_switch.pack(side="left", padx=8)

        # Mini mode toggle button
        self.mini_btn = ctk.CTkButton(
            util_frame,
            text="🗗 Mini View",
            command=self._toggle_mini_mode,
            width=90,
            height=30,
            fg_color="#1e293b",
            hover_color="#334155",
            text_color="#e2e8f0",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.mini_btn.pack(side="left", padx=6)

        # Sound Selector Dropdown
        self.sound_menu = ctk.CTkOptionMenu(
            util_frame,
            values=self.sound_mgr.get_available_sounds(),
            command=self._on_sound_selected,
            width=130,
            height=30,
            fg_color="#1e293b",
            button_color="#334155",
            button_hover_color="#475569",
            font=ctk.CTkFont(family="Segoe UI", size=11)
        )
        self.sound_menu.set(self.sound_mgr.current_sound)
        self.sound_menu.pack(side="left", padx=6)

        # Test Sound Button
        self.test_sound_btn = ctk.CTkButton(
            util_frame,
            text="🔊",
            command=self._test_sound,
            width=32,
            height=30,
            fg_color="#1e293b",
            hover_color="#334155",
            font=ctk.CTkFont(size=14)
        )
        self.test_sound_btn.pack(side="left", padx=(0, 4))

        # 2. Main Body Split Area (Left: Gauge & Controls, Right: Panels)
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
        self.body_frame.grid_columnconfigure(0, weight=6)
        self.body_frame.grid_columnconfigure(1, weight=5)
        self.body_frame.grid_rowconfigure(0, weight=1)

        # Left Column: Gauge Display & Quick Controls Card
        self.left_card = ctk.CTkFrame(
            self.body_frame,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=CARD_BORDER
        )
        self.left_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12), pady=0)
        self.left_card.grid_columnconfigure(0, weight=1)
        self.left_card.grid_rowconfigure(1, weight=1)

        # Alarm Banner (Hidden by default, shown on completion)
        self.alarm_banner = ctk.CTkFrame(self.left_card, fg_color="#ef4444", corner_radius=10)
        self.alarm_banner_label = ctk.CTkLabel(
            self.alarm_banner,
            text="⏰ TIME'S UP! Alarm ringing...",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#ffffff"
        )
        self.alarm_banner_label.pack(side="left", padx=16, pady=8)
        
        self.alarm_dismiss_btn = ctk.CTkButton(
            self.alarm_banner,
            text="Dismiss Alarm ✕",
            command=self._stop_alarm_alert,
            fg_color="#991b1b",
            hover_color="#7f1d1d",
            text_color="#ffffff",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            width=120,
            height=28
        )
        self.alarm_dismiss_btn.pack(side="right", padx=12, pady=8)

        # Circular Gauge Widget
        gauge_container = ctk.CTkFrame(self.left_card, fg_color="transparent")
        gauge_container.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        gauge_container.pack_propagate(True)

        self.circular_gauge = CircularTimerDisplay(gauge_container, size=320, bg_color=CARD_BG)
        self.circular_gauge.pack(expand=True, pady=10)

        # Quick Time Adjusters Row (Live ± Buttons)
        self.adjust_row = ctk.CTkFrame(self.left_card, fg_color="transparent")
        self.adjust_row.grid(row=2, column=0, pady=(0, 10))

        adjust_buttons = [
            ("-5m", -300),
            ("-1m", -60),
            ("+1m", 60),
            ("+5m", 300),
            ("+10m", 600)
        ]
        for label, delta in adjust_buttons:
            btn = ctk.CTkButton(
                self.adjust_row,
                text=label,
                command=lambda d=delta: self._quick_adjust_time(d),
                width=54,
                height=28,
                fg_color="#1e293b",
                hover_color="#334155",
                text_color="#94a3b8",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold")
            )
            btn.pack(side="left", padx=4)

        # Primary Action Buttons (Start/Pause, Reset, Repeat)
        actions_row = ctk.CTkFrame(self.left_card, fg_color="transparent")
        actions_row.grid(row=3, column=0, pady=(0, 18), padx=20, sticky="ew")
        actions_row.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_pause_btn = ctk.CTkButton(
            actions_row,
            text="▶ START",
            command=self._toggle_start_pause,
            height=46,
            fg_color=ACCENT_EMERALD,
            hover_color="#059669",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold")
        )
        self.start_pause_btn.grid(row=0, column=0, padx=6, sticky="ew")

        self.reset_btn = ctk.CTkButton(
            actions_row,
            text="↺ RESET",
            command=self._reset_timer,
            height=46,
            fg_color="#334155",
            hover_color="#475569",
            text_color="#f1f5f9",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        )
        self.reset_btn.grid(row=0, column=1, padx=6, sticky="ew")

        self.loop_btn = ctk.CTkButton(
            actions_row,
            text="🔁 Repeat: OFF",
            command=self._toggle_loop,
            height=46,
            fg_color="#1e293b",
            hover_color="#334155",
            text_color=TEXT_MUTED,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
        )
        self.loop_btn.grid(row=0, column=2, padx=6, sticky="ew")

        # Right Column: Multi-tab Sidebar (Countdown Config & Presets / Pomodoro / Stopwatch Laps)
        self.right_card = ctk.CTkFrame(
            self.body_frame,
            fg_color=CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=CARD_BORDER
        )
        self.right_card.grid(row=0, column=1, sticky="nsew", padx=(12, 0), pady=0)
        self.right_card.grid_rowconfigure(0, weight=1)
        self.right_card.grid_columnconfigure(0, weight=1)

        # Tab container for right side
        self._init_countdown_panel()
        self._init_pomodoro_panel()
        self._init_stopwatch_panel()

        # Display correct panel initially
        self._show_active_panel()

        # Mini Mode Floating Container (Hidden initially)
        self._init_mini_mode_ui()

    # ------------------ PANEL INITIALIZATION ------------------
    def _init_countdown_panel(self):
        self.panel_countdown = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.panel_countdown.grid_columnconfigure(0, weight=1)
        self.panel_countdown.grid_rowconfigure(2, weight=1)

        # Custom Duration Picker Section
        picker_label = ctk.CTkLabel(
            self.panel_countdown,
            text="SET DURATION",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_MUTED
        )
        picker_label.grid(row=0, column=0, sticky="w", padx=20, pady=(16, 6))

        inputs_frame = ctk.CTkFrame(self.panel_countdown, fg_color="#1e293b", corner_radius=12)
        inputs_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=4)
        inputs_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Hours
        h_box = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        h_box.grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkLabel(h_box, text="HOURS", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack()
        self.entry_hours = ctk.CTkEntry(h_box, width=64, height=36, justify="center", font=ctk.CTkFont(size=16, weight="bold"))
        self.entry_hours.insert(0, "00")
        self.entry_hours.pack(pady=4)

        # Minutes
        m_box = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        m_box.grid(row=0, column=1, padx=10, pady=10)
        ctk.CTkLabel(m_box, text="MINUTES", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack()
        self.entry_minutes = ctk.CTkEntry(m_box, width=64, height=36, justify="center", font=ctk.CTkFont(size=16, weight="bold"))
        self.entry_minutes.insert(0, "25")
        self.entry_minutes.pack(pady=4)

        # Seconds
        s_box = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        s_box.grid(row=0, column=2, padx=10, pady=10)
        ctk.CTkLabel(s_box, text="SECONDS", font=ctk.CTkFont(size=10, weight="bold"), text_color=TEXT_MUTED).pack()
        self.entry_seconds = ctk.CTkEntry(s_box, width=64, height=36, justify="center", font=ctk.CTkFont(size=16, weight="bold"))
        self.entry_seconds.insert(0, "00")
        self.entry_seconds.pack(pady=4)

        # Set and Save Button Row
        btn_row = ctk.CTkFrame(inputs_frame, fg_color="transparent")
        btn_row.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")
        btn_row.grid_columnconfigure((0, 1), weight=1)

        set_time_btn = ctk.CTkButton(
            btn_row,
            text="Apply Time",
            command=self._apply_custom_time,
            fg_color="#0284c7",
            hover_color="#0369a1",
            height=32,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        set_time_btn.grid(row=0, column=0, padx=4, sticky="ew")

        save_preset_btn = ctk.CTkButton(
            btn_row,
            text="+ Save Preset",
            command=self._open_save_preset_dialog,
            fg_color="#334155",
            hover_color="#475569",
            height=32,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_preset_btn.grid(row=0, column=1, padx=4, sticky="ew")

        # Presets List Section
        presets_head = ctk.CTkFrame(self.panel_countdown, fg_color="transparent")
        presets_head.grid(row=2, column=0, sticky="ew", padx=20, pady=(12, 4))
        ctk.CTkLabel(
            presets_head,
            text="QUICK PRESETS",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_MUTED
        ).pack(side="left")

        # Scrollable presets frame
        self.presets_scroll = ctk.CTkScrollableFrame(
            self.panel_countdown,
            fg_color="transparent",
            corner_radius=8
        )
        self.presets_scroll.grid(row=3, column=0, sticky="nsew", padx=16, pady=(0, 12))
        self.presets_scroll.grid_columnconfigure(0, weight=1)
        self.panel_countdown.grid_rowconfigure(3, weight=1)

        self._refresh_presets_ui()

    def _init_pomodoro_panel(self):
        self.panel_pomodoro = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.panel_pomodoro.grid_columnconfigure(0, weight=1)

        pomo_title = ctk.CTkLabel(
            self.panel_pomodoro,
            text="POMODORO FOCUS WORKFLOW",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=ACCENT_ROSE
        )
        pomo_title.pack(anchor="w", padx=20, pady=(16, 6))

        # Progress / Streak Indicators Card
        streak_card = ctk.CTkFrame(self.panel_pomodoro, fg_color="#1e293b", corner_radius=12)
        streak_card.pack(fill="x", padx=20, pady=8)
        
        self.pomo_status_label = ctk.CTkLabel(
            streak_card,
            text="Phase: Deep Work Focus",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color="#f8fafc"
        )
        self.pomo_status_label.pack(padx=14, pady=(12, 4))

        self.pomo_dots_label = ctk.CTkLabel(
            streak_card,
            text="🍅 ⚪ ⚪ ⚪  (Round 1 / 4)",
            font=ctk.CTkFont(family="Segoe UI", size=16),
            text_color=ACCENT_ROSE
        )
        self.pomo_dots_label.pack(padx=14, pady=(0, 12))

        # Pomodoro Durations Config
        cfg_frame = ctk.CTkFrame(self.panel_pomodoro, fg_color="#1e293b", corner_radius=12)
        cfg_frame.pack(fill="x", padx=20, pady=8)
        cfg_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(cfg_frame, text="Focus Time (min):", font=ctk.CTkFont(size=12)).grid(row=0, column=0, padx=12, pady=10, sticky="w")
        self.pomo_focus_entry = ctk.CTkEntry(cfg_frame, width=64, justify="center")
        self.pomo_focus_entry.insert(0, str(self.pomo_focus_min))
        self.pomo_focus_entry.grid(row=0, column=1, padx=12, pady=10, sticky="e")

        ctk.CTkLabel(cfg_frame, text="Short Break (min):", font=ctk.CTkFont(size=12)).grid(row=1, column=0, padx=12, pady=10, sticky="w")
        self.pomo_short_entry = ctk.CTkEntry(cfg_frame, width=64, justify="center")
        self.pomo_short_entry.insert(0, str(self.pomo_short_break_min))
        self.pomo_short_entry.grid(row=1, column=1, padx=12, pady=10, sticky="e")

        ctk.CTkLabel(cfg_frame, text="Long Break (min):", font=ctk.CTkFont(size=12)).grid(row=2, column=0, padx=12, pady=10, sticky="w")
        self.pomo_long_entry = ctk.CTkEntry(cfg_frame, width=64, justify="center")
        self.pomo_long_entry.insert(0, str(self.pomo_long_break_min))
        self.pomo_long_entry.grid(row=2, column=1, padx=12, pady=10, sticky="e")

        # Update Settings Button
        save_pomo_btn = ctk.CTkButton(
            cfg_frame,
            text="Update Pomodoro Intervals",
            command=self._apply_pomodoro_settings,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_pomo_btn.grid(row=3, column=0, columnspan=2, padx=12, pady=(4, 12), sticky="ew")

        # Skip Stage Button
        skip_btn = ctk.CTkButton(
            self.panel_pomodoro,
            text="⏭ Skip to Next Phase",
            command=self._skip_pomo_stage,
            fg_color="#334155",
            hover_color="#475569",
            text_color="#f1f5f9",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=36
        )
        skip_btn.pack(fill="x", padx=20, pady=12)

    def _init_stopwatch_panel(self):
        self.panel_stopwatch = ctk.CTkFrame(self.right_card, fg_color="transparent")
        self.panel_stopwatch.grid_columnconfigure(0, weight=1)
        self.panel_stopwatch.grid_rowconfigure(2, weight=1)

        sw_header = ctk.CTkFrame(self.panel_stopwatch, fg_color="transparent")
        sw_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 6))

        ctk.CTkLabel(
            sw_header,
            text="PRECISION STOPWATCH & LAPS",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=ACCENT_PURPLE
        ).pack(side="left")

        # Lap button row
        lap_actions = ctk.CTkFrame(self.panel_stopwatch, fg_color="transparent")
        lap_actions.grid(row=1, column=0, sticky="ew", padx=20, pady=4)
        lap_actions.grid_columnconfigure((0, 1), weight=1)

        self.lap_btn = ctk.CTkButton(
            lap_actions,
            text="🏁 Record Lap",
            command=self._record_stopwatch_lap,
            fg_color="#7c3aed",
            hover_color="#6d28d9",
            height=34,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.lap_btn.grid(row=0, column=0, padx=4, sticky="ew")

        clear_laps_btn = ctk.CTkButton(
            lap_actions,
            text="Clear Laps",
            command=self._clear_stopwatch_laps,
            fg_color="#334155",
            hover_color="#475569",
            height=34,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        clear_laps_btn.grid(row=0, column=1, padx=4, sticky="ew")

        # Scrollable Lap Times Table
        self.laps_scroll = ctk.CTkScrollableFrame(
            self.panel_stopwatch,
            fg_color="#1e293b",
            corner_radius=12
        )
        self.laps_scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 16))
        self.laps_scroll.grid_columnconfigure(0, weight=1)

        self._render_stopwatch_laps()

    def _show_active_panel(self):
        # Hide all
        self.panel_countdown.grid_forget()
        self.panel_pomodoro.grid_forget()
        self.panel_stopwatch.grid_forget()

        if self.mode == "COUNTDOWN":
            self.panel_countdown.grid(row=0, column=0, sticky="nsew")
            self.adjust_row.grid(row=2, column=0, pady=(0, 10))
            self.loop_btn.grid(row=0, column=2, padx=6, sticky="ew")
        elif self.mode == "POMODORO":
            self.panel_pomodoro.grid(row=0, column=0, sticky="nsew")
            self.adjust_row.grid(row=2, column=0, pady=(0, 10))
            self.loop_btn.grid_forget()
        elif self.mode == "STOPWATCH":
            self.panel_stopwatch.grid(row=0, column=0, sticky="nsew")
            self.adjust_row.grid_forget()
            self.loop_btn.grid_forget()

    # ------------------ MINI MODE ------------------
    def _init_mini_mode_ui(self):
        self.mini_frame = ctk.CTkFrame(self, fg_color=BG_DARK)
        self.mini_frame.grid_columnconfigure(0, weight=1)
        self.mini_frame.grid_rowconfigure(1, weight=1)

        # Header for mini view
        m_head = ctk.CTkFrame(self.mini_frame, fg_color="transparent")
        m_head.grid(row=0, column=0, sticky="ew", padx=12, pady=(8, 0))

        self.mini_title_label = ctk.CTkLabel(
            m_head,
            text="⚡ CHRONOFLOW",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=ACCENT_CYAN
        )
        self.mini_title_label.pack(side="left")

        expand_btn = ctk.CTkButton(
            m_head,
            text="⤢ Expand",
            command=self._toggle_mini_mode,
            width=70,
            height=24,
            fg_color="#1e293b",
            hover_color="#334155",
            font=ctk.CTkFont(size=11, weight="bold")
        )
        expand_btn.pack(side="right")

        # Huge digital display for mini
        self.mini_time_label = ctk.CTkLabel(
            self.mini_frame,
            text="00:25:00",
            font=ctk.CTkFont(family="Consolas", size=42, weight="bold"),
            text_color="#f8fafc"
        )
        self.mini_time_label.grid(row=1, column=0, pady=4)

        # Mini Controls
        m_ctrl = ctk.CTkFrame(self.mini_frame, fg_color="transparent")
        m_ctrl.grid(row=2, column=0, pady=(0, 12))

        self.mini_start_btn = ctk.CTkButton(
            m_ctrl,
            text="▶ Start",
            command=self._toggle_start_pause,
            width=90,
            height=32,
            fg_color=ACCENT_EMERALD,
            hover_color="#059669",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.mini_start_btn.pack(side="left", padx=4)

        self.mini_reset_btn = ctk.CTkButton(
            m_ctrl,
            text="↺ Reset",
            command=self._reset_timer,
            width=80,
            height=32,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.mini_reset_btn.pack(side="left", padx=4)

    def _toggle_mini_mode(self):
        self.is_mini_mode = not self.is_mini_mode
        if self.is_mini_mode:
            self.normal_geometry = self.geometry()
            self.header_frame.grid_forget()
            self.body_frame.grid_forget()
            self.mini_frame.grid(row=0, column=0, sticky="nsew")
            self.geometry("360x180")
            self.minsize(320, 160)
            self.attributes("-topmost", True)
            self.top_switch.select()
        else:
            self.mini_frame.grid_forget()
            self.header_frame.grid(row=0, column=0, sticky="ew")
            self.body_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=16)
            self.geometry(self.normal_geometry)
            self.minsize(780, 600)
            # Revert topmost to switch state
            self.attributes("-topmost", bool(self.top_switch.get()))

    def _toggle_always_on_top(self):
        val = bool(self.top_switch.get())
        self.attributes("-topmost", val)

    # ------------------ PRESETS UI ------------------
    def _refresh_presets_ui(self):
        for widget in self.presets_scroll.winfo_children():
            widget.destroy()

        presets = self.preset_mgr.get_presets()
        for idx, p in enumerate(presets):
            card = ctk.CTkFrame(self.presets_scroll, fg_color="#1e293b", corner_radius=8)
            card.pack(fill="x", pady=4, padx=4)
            card.grid_columnconfigure(0, weight=1)

            # Name and duration
            dur_str = f"{p['hours']:02d}:{p['minutes']:02d}:{p['seconds']:02d}"
            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.grid(row=0, column=0, padx=12, pady=8, sticky="w")
            
            p_title = ctk.CTkLabel(
                info_frame,
                text=p["name"],
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color="#f8fafc"
            )
            p_title.pack(anchor="w")

            p_dur = ctk.CTkLabel(
                info_frame,
                text=dur_str,
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=ACCENT_CYAN
            )
            p_dur.pack(anchor="w")

            # Load Button
            load_btn = ctk.CTkButton(
                card,
                text="Load",
                command=lambda p_item=p: self._load_preset(p_item),
                width=54,
                height=26,
                fg_color="#0284c7",
                hover_color="#0369a1",
                font=ctk.CTkFont(size=11, weight="bold")
            )
            load_btn.grid(row=0, column=1, padx=6, pady=8)

            # Delete button (only for non-built-in)
            if not p.get("builtin", False):
                del_btn = ctk.CTkButton(
                    card,
                    text="✕",
                    command=lambda i=idx: self._delete_preset(i),
                    width=28,
                    height=26,
                    fg_color="#ef4444",
                    hover_color="#dc2626",
                    font=ctk.CTkFont(size=11, weight="bold")
                )
                del_btn.grid(row=0, column=2, padx=(0, 8), pady=8)

    def _load_preset(self, preset):
        total_s = preset["hours"] * 3600 + preset["minutes"] * 60 + preset["seconds"]
        if total_s <= 0:
            return
        self._stop_alarm_alert()
        self.is_running = False
        self.is_paused = False
        self.total_seconds = total_s
        self.remaining_seconds = float(total_s)
        self.mode = "COUNTDOWN"
        self.mode_selector.set("⏳ Countdown")
        self._show_active_panel()
        self._update_timer_visuals()

    def _delete_preset(self, index):
        self.preset_mgr.delete_preset(index)
        self._refresh_presets_ui()

    def _open_save_preset_dialog(self):
        dialog = ctk.CTkInputDialog(
            text="Enter a name for this custom preset:",
            title="Save Timer Preset"
        )
        name = dialog.get_input()
        if name:
            try:
                h = int(self.entry_hours.get().strip() or "0")
                m = int(self.entry_minutes.get().strip() or "0")
                s = int(self.entry_seconds.get().strip() or "0")
                if h * 3600 + m * 60 + s > 0:
                    self.preset_mgr.add_preset(name, h, m, s)
                    self._refresh_presets_ui()
                else:
                    messagebox.showwarning("Invalid Duration", "Please specify a duration greater than 0.")
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric time values.")

    # ------------------ TIMER CONTROLS & LOGIC ------------------
    def _on_mode_changed(self, selected_mode):
        self._stop_alarm_alert()
        self.is_running = False
        self.is_paused = False

        if "Countdown" in selected_mode:
            self.mode = "COUNTDOWN"
            self.remaining_seconds = float(self.total_seconds)
        elif "Pomodoro" in selected_mode:
            self.mode = "POMODORO"
            self._setup_pomo_phase("FOCUS")
        elif "Stopwatch" in selected_mode:
            self.mode = "STOPWATCH"
            self.stopwatch_elapsed = 0.0

        self._show_active_panel()
        self._update_timer_visuals()

    def _toggle_start_pause(self):
        self._stop_alarm_alert()
        if not self.is_running:
            # Starting / Resuming
            self.is_running = True
            self.is_paused = False
            self.last_tick_time = time.monotonic()
        else:
            # Pausing
            self.is_running = False
            self.is_paused = True

        self._update_timer_visuals()

    def _reset_timer(self):
        self._stop_alarm_alert()
        self.is_running = False
        self.is_paused = False

        if self.mode == "COUNTDOWN":
            self.remaining_seconds = float(self.total_seconds)
        elif self.mode == "POMODORO":
            self.pomo_current_cycle = 1
            self._setup_pomo_phase("FOCUS")
        elif self.mode == "STOPWATCH":
            self.stopwatch_elapsed = 0.0

        self._update_timer_visuals()

    def _quick_adjust_time(self, delta_seconds):
        if self.mode == "COUNTDOWN":
            self.remaining_seconds = max(0.0, self.remaining_seconds + delta_seconds)
            # Adjust total_seconds accordingly if remaining exceeded initial total
            if self.remaining_seconds > self.total_seconds:
                self.total_seconds = self.remaining_seconds
        elif self.mode == "POMODORO":
            self.remaining_seconds = max(0.0, self.remaining_seconds + delta_seconds)
            if self.remaining_seconds > self.total_seconds:
                self.total_seconds = self.remaining_seconds
        self._update_timer_visuals()

    def _toggle_loop(self):
        self.loop_timer = not self.loop_timer
        if self.loop_timer:
            self.loop_btn.configure(text="🔁 Repeat: ON", fg_color="#0284c7", text_color="#ffffff")
        else:
            self.loop_btn.configure(text="🔁 Repeat: OFF", fg_color="#1e293b", text_color=TEXT_MUTED)

    def _apply_custom_time(self):
        try:
            h = int(self.entry_hours.get().strip() or "0")
            m = int(self.entry_minutes.get().strip() or "0")
            s = int(self.entry_seconds.get().strip() or "0")
            total = h * 3600 + m * 60 + s
            if total <= 0:
                messagebox.showwarning("Invalid Time", "Please enter a duration greater than zero.")
                return

            self._stop_alarm_alert()
            self.is_running = False
            self.is_paused = False
            self.total_seconds = total
            self.remaining_seconds = float(total)
            self._update_timer_visuals()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integers for hours, minutes, and seconds.")

    # ------------------ POMODORO LOGIC ------------------
    def _setup_pomo_phase(self, phase):
        self.pomo_stage = phase
        if phase == "FOCUS":
            dur = self.pomo_focus_min * 60
            self.pomo_status_label.configure(text=f"Phase: Focus Session #{self.pomo_current_cycle}")
        elif phase == "SHORT_BREAK":
            dur = self.pomo_short_break_min * 60
            self.pomo_status_label.configure(text="Phase: Short Coffee Break ☕")
        elif phase == "LONG_BREAK":
            dur = self.pomo_long_break_min * 60
            self.pomo_status_label.configure(text="Phase: Extended Rest Break 🌿")

        self.total_seconds = dur
        self.remaining_seconds = float(dur)
        self._update_pomo_dots()

    def _update_pomo_dots(self):
        dots = []
        for i in range(1, self.pomo_cycle_goal + 1):
            if i < self.pomo_current_cycle:
                dots.append("🍅")
            elif i == self.pomo_current_cycle:
                dots.append("🔴" if self.pomo_stage == "FOCUS" else "☕")
            else:
                dots.append("⚪")
        dot_str = " ".join(dots)
        self.pomo_dots_label.configure(text=f"{dot_str}  (Round {self.pomo_current_cycle}/{self.pomo_cycle_goal})")

    def _advance_pomo_stage(self):
        if self.pomo_stage == "FOCUS":
            if self.pomo_current_cycle >= self.pomo_cycle_goal:
                self._setup_pomo_phase("LONG_BREAK")
            else:
                self._setup_pomo_phase("SHORT_BREAK")
        elif self.pomo_stage == "SHORT_BREAK":
            self.pomo_current_cycle += 1
            self._setup_pomo_phase("FOCUS")
        elif self.pomo_stage == "LONG_BREAK":
            self.pomo_current_cycle = 1
            self._setup_pomo_phase("FOCUS")

    def _skip_pomo_stage(self):
        self._stop_alarm_alert()
        self.is_running = False
        self.is_paused = False
        self._advance_pomo_stage()
        self._update_timer_visuals()

    def _apply_pomodoro_settings(self):
        try:
            f = int(self.pomo_focus_entry.get().strip() or "25")
            s = int(self.pomo_short_entry.get().strip() or "5")
            l = int(self.pomo_long_entry.get().strip() or "15")
            if f <= 0 or s <= 0 or l <= 0:
                messagebox.showwarning("Invalid Input", "Intervals must be positive.")
                return
            self.pomo_focus_min = f
            self.pomo_short_break_min = s
            self.pomo_long_break_min = l
            self._setup_pomo_phase(self.pomo_stage)
            self._update_timer_visuals()
            messagebox.showinfo("Pomodoro Updated", "Pomodoro interval durations saved!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers.")

    # ------------------ STOPWATCH LOGIC ------------------
    def _record_stopwatch_lap(self):
        if self.mode != "STOPWATCH":
            return
        lap_total = self.stopwatch_elapsed
        lap_count = len(self.stopwatch_laps) + 1
        last_total = self.stopwatch_laps[-1]["total"] if self.stopwatch_laps else 0.0
        lap_split = lap_total - last_total

        self.stopwatch_laps.append({
            "lap_num": lap_count,
            "split": lap_split,
            "total": lap_total
        })
        self._render_stopwatch_laps()

    def _clear_stopwatch_laps(self):
        self.stopwatch_laps.clear()
        self._render_stopwatch_laps()

    def _render_stopwatch_laps(self):
        for widget in self.laps_scroll.winfo_children():
            widget.destroy()

        if not self.stopwatch_laps:
            empty_lbl = ctk.CTkLabel(
                self.laps_scroll,
                text="No recorded laps yet.\nPress 'Record Lap' while stopwatch runs.",
                font=ctk.CTkFont(size=11),
                text_color=TEXT_MUTED
            )
            empty_lbl.pack(pady=20)
            return

        # Find fastest and slowest splits (if >= 2 laps)
        min_split = min(l["split"] for l in self.stopwatch_laps) if len(self.stopwatch_laps) >= 2 else None
        max_split = max(l["split"] for l in self.stopwatch_laps) if len(self.stopwatch_laps) >= 2 else None

        for lap in reversed(self.stopwatch_laps):
            row = ctk.CTkFrame(self.laps_scroll, fg_color="#182234", corner_radius=6)
            row.pack(fill="x", pady=3, padx=2)
            row.grid_columnconfigure((0, 1, 2), weight=1)

            # Lap num
            num_lbl = ctk.CTkLabel(
                row,
                text=f"Lap {lap['lap_num']:02d}",
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                text_color=TEXT_LIGHT
            )
            num_lbl.grid(row=0, column=0, padx=8, pady=6, sticky="w")

            # Split
            split_str = f"+{self._format_stopwatch_time(lap['split'])}"
            split_color = ACCENT_EMERALD if lap["split"] == min_split else (
                ACCENT_ROSE if lap["split"] == max_split else TEXT_MUTED
            )
            split_lbl = ctk.CTkLabel(
                row,
                text=split_str,
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color=split_color
            )
            split_lbl.grid(row=0, column=1, padx=8, pady=6)

            # Total
            total_lbl = ctk.CTkLabel(
                row,
                text=self._format_stopwatch_time(lap["total"]),
                font=ctk.CTkFont(family="Consolas", size=11, weight="bold"),
                text_color=TEXT_LIGHT
            )
            total_lbl.grid(row=0, column=2, padx=8, pady=6, sticky="e")

    # ------------------ SOUND CONTROLS ------------------
    def _on_sound_selected(self, choice):
        self.sound_mgr.current_sound = choice

    def _test_sound(self):
        self.sound_mgr.play_sound()

    # ------------------ ALARM COMPLETION ------------------
    def _trigger_completion(self):
        self.is_running = False
        self.is_paused = False
        self.alarm_active = True
        
        # Show alarm banner
        self.alarm_banner.grid(row=0, column=0, sticky="ew", padx=16, pady=(12, 0))
        self.circular_gauge.start_pulse()

        # Play alarm sound in loop
        self.sound_mgr.start_alarm_loop(loops=4)

        # Handle loop mode or Pomodoro progression
        if self.mode == "COUNTDOWN" and self.loop_timer:
            self.after(3000, self._auto_restart_countdown)
        elif self.mode == "POMODORO":
            self.after(3000, self._advance_pomo_stage)

    def _auto_restart_countdown(self):
        if self.alarm_active and self.loop_timer:
            self._stop_alarm_alert()
            self.remaining_seconds = float(self.total_seconds)
            self.is_running = True
            self.last_tick_time = time.monotonic()
            self._update_timer_visuals()

    def _stop_alarm_alert(self):
        if self.alarm_active:
            self.alarm_active = False
            self.alarm_banner.grid_forget()
            self.circular_gauge.stop_pulse()
            self.sound_mgr.stop_alarm()
            self._update_timer_visuals()

    # ------------------ MASTER TICK LOOP ------------------
    def _master_tick(self):
        now = time.monotonic()
        if self.is_running:
            dt = now - self.last_tick_time
            self.last_tick_time = now

            if self.mode in ("COUNTDOWN", "POMODORO"):
                self.remaining_seconds -= dt
                if self.remaining_seconds <= 0.0:
                    self.remaining_seconds = 0.0
                    self._update_timer_visuals()
                    self._trigger_completion()
                else:
                    self._update_timer_visuals()
            elif self.mode == "STOPWATCH":
                self.stopwatch_elapsed += dt
                self._update_timer_visuals()
        else:
            self.last_tick_time = now

        # High-resolution refresh: 50ms for buttery-smooth gauge animation
        self.after(50, self._master_tick)

    # ------------------ VISUAL REFRESH ------------------
    def _update_timer_visuals(self):
        # Update Start/Pause button appearance
        if self.is_running:
            self.start_pause_btn.configure(
                text="❚❚ PAUSE",
                fg_color=ACCENT_AMBER,
                hover_color="#d97706"
            )
            self.mini_start_btn.configure(
                text="❚❚ Pause",
                fg_color=ACCENT_AMBER,
                hover_color="#d97706"
            )
            status_text = "RUNNING"
        elif self.is_paused:
            self.start_pause_btn.configure(
                text="▶ RESUME",
                fg_color=ACCENT_EMERALD,
                hover_color="#059669"
            )
            self.mini_start_btn.configure(
                text="▶ Resume",
                fg_color=ACCENT_EMERALD,
                hover_color="#059669"
            )
            status_text = "PAUSED"
        elif self.alarm_active:
            status_text = "TIME'S UP!"
        else:
            self.start_pause_btn.configure(
                text="▶ START",
                fg_color=ACCENT_EMERALD,
                hover_color="#059669"
            )
            self.mini_start_btn.configure(
                text="▶ Start",
                fg_color=ACCENT_EMERALD,
                hover_color="#059669"
            )
            status_text = "READY"

        # Format time strings and calculate fraction
        if self.mode in ("COUNTDOWN", "POMODORO"):
            time_display = self._format_seconds(int(math.ceil(self.remaining_seconds)))
            fraction = (self.remaining_seconds / self.total_seconds) if self.total_seconds > 0 else 0.0
            pct_val = int(fraction * 100)
            subtext = f"{pct_val}% REMAINING"

            if self.mode == "COUNTDOWN":
                mode_title = "COUNTDOWN"
                self.circular_gauge.set_accent_color(ACCENT_CYAN, "#0284c7")
            else:
                if self.pomo_stage == "FOCUS":
                    mode_title = f"FOCUS • ROUND {self.pomo_current_cycle}/{self.pomo_cycle_goal}"
                    self.circular_gauge.set_accent_color(ACCENT_ROSE, "#be123c")
                else:
                    mode_title = "RELAX BREAK"
                    self.circular_gauge.set_accent_color(ACCENT_EMERALD, "#059669")
        else:
            # STOPWATCH
            time_display = self._format_stopwatch_time(self.stopwatch_elapsed)
            # Cycle every 60 seconds for circular progress
            fraction = (self.stopwatch_elapsed % 60.0) / 60.0
            mode_title = "STOPWATCH"
            subtext = f"{len(self.stopwatch_laps)} Laps Recorded"
            self.circular_gauge.set_accent_color(ACCENT_PURPLE, "#7c3aed")

        # Update circular gauge
        self.circular_gauge.update_display(
            fraction=fraction,
            time_str=time_display,
            status_str=status_text,
            mode_title=mode_title,
            subtext=subtext
        )

        # Update Mini Display
        self.mini_time_label.configure(text=time_display)
        self.mini_title_label.configure(text=f"⚡ {mode_title}")

    # ------------------ TIME FORMATTERS ------------------
    @staticmethod
    def _format_seconds(seconds):
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    @staticmethod
    def _format_stopwatch_time(elapsed):
        total_m = int(elapsed // 60)
        s = int(elapsed % 60)
        cs = int((elapsed * 100) % 100)
        return f"{total_m:02d}:{s:02d}.{cs:02d}"

    # ------------------ KEYBOARD SHORTCUTS ------------------
    def _bind_shortcuts(self):
        self.bind("<space>", lambda e: self._toggle_start_pause())
        self.bind("<r>", lambda e: self._reset_timer())
        self.bind("<R>", lambda e: self._reset_timer())
        self.bind("<m>", lambda e: self._toggle_mini_mode())
        self.bind("<M>", lambda e: self._toggle_mini_mode())
        self.bind("<Escape>", lambda e: self._toggle_mini_mode() if self.is_mini_mode else None)

def main():
    app = ChronoFlowApp()
    app.mainloop()

if __name__ == "__main__":
    main()
