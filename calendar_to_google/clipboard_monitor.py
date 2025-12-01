"""Clipboard monitoring functionality with cross-platform support."""

import sys
import threading
import time
import pyperclip


class ClipboardMonitor:
    """Monitor clipboard changes across platforms."""

    def __init__(self, callback):
        """
        Initialize clipboard monitor.

        Args:
            callback: Function to call when clipboard changes (receives clipboard text)
        """
        self.callback = callback
        self._running = False
        self._last_content = ""
        self._monitor_thread = None
        self._hotkey_available = False

    def start(self):
        """Start monitoring clipboard."""
        if self._running:
            return

        self._running = True
        try:
            self._last_content = pyperclip.paste()
        except Exception:
            self._last_content = ""

        # Try to use keyboard hotkey on Windows (most reliable)
        # Fall back to polling on other platforms
        if sys.platform == 'win32':
            try:
                import keyboard
                keyboard.add_hotkey('ctrl+c', self._on_copy, suppress=False)
                self._hotkey_available = True
                print("Clipboard monitoring started (hotkey mode)")
            except Exception as e:
                print(f"Hotkey registration failed: {e}")
                self._start_polling()
        else:
            # macOS/Linux: use polling (keyboard library requires root on Linux)
            self._start_polling()

    def _start_polling(self):
        """Start polling-based clipboard monitoring."""
        self._hotkey_available = False
        self._monitor_thread = threading.Thread(target=self._poll_clipboard, daemon=True)
        self._monitor_thread.start()
        print("Clipboard monitoring started (polling mode)")

    def _poll_clipboard(self):
        """Poll clipboard for changes."""
        while self._running:
            try:
                current_content = pyperclip.paste()
                if current_content and current_content.strip():
                    if current_content != self._last_content:
                        self._last_content = current_content
                        self.callback(current_content)
            except Exception:
                pass
            time.sleep(0.5)  # Check every 500ms

    def stop(self):
        """Stop monitoring."""
        self._running = False
        if self._hotkey_available:
            try:
                import keyboard
                keyboard.unhook_all_hotkeys()
            except Exception:
                pass

    def _on_copy(self):
        """Handle Ctrl+C press (Windows only)."""
        if not self._running:
            return

        # Wait a moment for clipboard to update
        def check_clipboard():
            time.sleep(0.1)
            try:
                current_content = pyperclip.paste()
                if current_content and current_content.strip():
                    if current_content != self._last_content:
                        self._last_content = current_content
                        self.callback(current_content)
            except Exception as e:
                print(f"Clipboard error: {e}")

        threading.Thread(target=check_clipboard, daemon=True).start()

    def get_current_clipboard(self):
        """Get current clipboard content."""
        try:
            return pyperclip.paste()
        except Exception:
            return ""
