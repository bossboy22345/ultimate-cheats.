"""Simple desktop auto clicker with support for up to 100 CPS.

Usage:
  python autoclicker.py

This app is implemented with Tkinter and currently supports actual mouse clicking
on Windows via the Win32 `mouse_event` API.
"""

from __future__ import annotations

import ctypes
import platform
import threading
import time
import tkinter as tk
from tkinter import ttk

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004


class AutoClickerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Auto Clicker (1-100 CPS)")
        self.root.resizable(False, False)

        self.cps_var = tk.IntVar(value=10)
        self.status_var = tk.StringVar(value="Idle")

        self.running = False
        self._thread: threading.Thread | None = None

        frame = ttk.Frame(root, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Clicks Per Second").grid(row=0, column=0, sticky="w")
        self.cps_scale = ttk.Scale(
            frame,
            from_=1,
            to=100,
            orient="horizontal",
            command=self._on_scale,
            length=280,
        )
        self.cps_scale.set(self.cps_var.get())
        self.cps_scale.grid(row=1, column=0, pady=(6, 6), sticky="ew")

        self.cps_value = ttk.Label(frame, text="10 CPS")
        self.cps_value.grid(row=2, column=0, sticky="w")

        button_row = ttk.Frame(frame)
        button_row.grid(row=3, column=0, pady=(12, 6), sticky="ew")

        self.start_btn = ttk.Button(button_row, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=(0, 8))

        self.stop_btn = ttk.Button(button_row, text="Stop", command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=1)

        ttk.Label(frame, textvariable=self.status_var).grid(row=4, column=0, sticky="w", pady=(8, 0))
        ttk.Label(
            frame,
            text="Tip: move your mouse over the target and press Start.",
            foreground="#555",
        ).grid(row=5, column=0, sticky="w", pady=(4, 0))

        if platform.system() != "Windows":
            self.status_var.set("Unsupported OS: clicking is implemented for Windows only.")
            self.start_btn.configure(state="disabled")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _on_scale(self, value: str) -> None:
        cps = max(1, min(100, int(float(value))))
        self.cps_var.set(cps)
        self.cps_value.configure(text=f"{cps} CPS")

    def _click_loop(self) -> None:
        while self.running:
            interval = 1 / max(1, self.cps_var.get())
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            time.sleep(interval)

    def start(self) -> None:
        if self.running:
            return

        if platform.system() != "Windows":
            self.status_var.set("Auto click is unavailable on this OS.")
            return

        self.running = True
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_var.set(f"Running at {self.cps_var.get()} CPS")

        self._thread = threading.Thread(target=self._click_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self.running:
            return

        self.running = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_var.set("Stopped")

    def on_close(self) -> None:
        self.stop()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    AutoClickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
