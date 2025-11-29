"""System tray application with right-click menu."""

import threading
import webbrowser
from io import BytesIO

import pystray
from PIL import Image, ImageDraw

from .clipboard_monitor import ClipboardMonitor
from .date_parser import DateParser, ParsedEvent
from .google_calendar import (
    GoogleCalendarClient, setup_credentials, select_credentials_file,
    prompt_credentials_setup, CREDENTIALS_FILE
)
from .edit_dialog import show_edit_dialog


class TrayApp:
    """System tray application."""

    def __init__(self):
        """Initialize the tray app."""
        self.clipboard_monitor = ClipboardMonitor(self._on_clipboard_change)
        self.date_parser = DateParser()
        self.calendar_client = GoogleCalendarClient()
        self.last_parsed_event: ParsedEvent | None = None
        self.icon: pystray.Icon | None = None
        self._notification_text = ""

    def _create_icon_image(self, color="green"):
        """Create a simple calendar icon."""
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Calendar background
        if color == "green":
            bg_color = (76, 175, 80, 255)  # Green
        elif color == "yellow":
            bg_color = (255, 193, 7, 255)  # Yellow
        else:
            bg_color = (158, 158, 158, 255)  # Gray

        # Draw calendar body
        draw.rounded_rectangle(
            [(4, 12), (60, 60)],
            radius=6,
            fill=bg_color
        )

        # Calendar header
        draw.rectangle([(4, 12), (60, 24)], fill=(66, 66, 66, 255))

        # Calendar rings
        draw.ellipse([(16, 6), (24, 14)], fill=(66, 66, 66, 255))
        draw.ellipse([(40, 6), (48, 14)], fill=(66, 66, 66, 255))

        # Draw a simple "+" on the calendar
        draw.rectangle([(29, 32), (35, 52)], fill=(255, 255, 255, 255))
        draw.rectangle([(22, 39), (42, 45)], fill=(255, 255, 255, 255))

        return image

    def _on_clipboard_change(self, text: str):
        """Handle clipboard content change."""
        parsed = self.date_parser.parse(text)
        if parsed:
            self.last_parsed_event = parsed
            # Update icon to yellow to indicate detected event
            if self.icon:
                self.icon.icon = self._create_icon_image("yellow")

            # Show notification
            date_str = parsed.start_date.strftime('%Y/%m/%d')
            if not parsed.all_day:
                date_str += " " + parsed.start_date.strftime('%H:%M')
            self._show_notification(
                "Date Detected",
                f"{parsed.title}\n{date_str}\nRight-click to add to Google Calendar"
            )
            print(f"[Detected] {parsed.title} - {date_str}")

    def _add_to_calendar_with_edit(self, icon, item):
        """Show edit dialog and add to Google Calendar."""
        text = self.clipboard_monitor.get_current_clipboard()
        if not text:
            self._show_notification("Error", "Clipboard is empty.")
            return

        parsed = self.date_parser.parse(text)
        if not parsed:
            self._show_notification("Error", "No date detected.")
            return

        # Show edit dialog in separate thread to avoid blocking
        def show_dialog():
            edited = show_edit_dialog(
                title=parsed.title,
                start_date=parsed.start_date,
                all_day=parsed.all_day,
                description=text
            )

            if edited and not edited.cancelled:
                # Create ParsedEvent from edited data
                event = ParsedEvent(
                    title=edited.title,
                    start_date=edited.start_date,
                    end_date=edited.end_date,
                    all_day=edited.all_day,
                    description=edited.description
                )
                self._do_add_to_calendar(event)

        threading.Thread(target=show_dialog, daemon=True).start()

    def _do_add_to_calendar(self, event: ParsedEvent):
        """Actually add event to calendar."""
        if not self.calendar_client.is_configured():
            # Show dialog to select credentials file
            if prompt_credentials_setup():
                self._show_notification(
                    "Setup Complete",
                    "認証情報を登録しました。再度イベントを追加してください。"
                )
                # Update icon color
                if self.icon:
                    self.icon.icon = self._create_icon_image("yellow")
            return

        if not self.calendar_client.is_authenticated():
            success = self.calendar_client.authenticate()
            if not success:
                self._show_notification("Auth Error", "Google authentication failed.")
                return

        url = self.calendar_client.add_event(event)
        if url:
            self._show_notification(
                "Added",
                f"'{event.title}' added to calendar"
            )
            # Reset icon to green
            if self.icon:
                self.icon.icon = self._create_icon_image("green")
            # Open calendar in browser
            webbrowser.open(url)
        else:
            self._show_notification("Error", "Failed to add event.")

    def _add_detected_event(self, icon, item):
        """Add the last detected event with edit dialog."""
        if not self.last_parsed_event:
            self._show_notification("Error", "No event detected. Copy text with a date first.")
            return

        parsed = self.last_parsed_event

        def show_dialog():
            edited = show_edit_dialog(
                title=parsed.title,
                start_date=parsed.start_date,
                all_day=parsed.all_day,
                description=parsed.description
            )

            if edited and not edited.cancelled:
                event = ParsedEvent(
                    title=edited.title,
                    start_date=edited.start_date,
                    end_date=edited.end_date,
                    all_day=edited.all_day,
                    description=edited.description
                )
                self._do_add_to_calendar(event)
                self.last_parsed_event = None

        threading.Thread(target=show_dialog, daemon=True).start()

    def _show_status(self, icon, item):
        """Show current status."""
        if self.last_parsed_event:
            event = self.last_parsed_event
            msg = f"Detected: {event.title}\nDate: {event.start_date.strftime('%Y/%m/%d')}"
            if not event.all_day:
                msg += f" {event.start_date.strftime('%H:%M')}"
        else:
            msg = "Waiting...\nCopy text containing a date"

        self._show_notification("Status", msg)

    def _setup_google(self, icon, item):
        """Open file dialog to register credentials."""
        def do_setup():
            if select_credentials_file():
                self._show_notification(
                    "Setup Complete",
                    "認証情報を登録しました。"
                )
                # Update icon color
                if self.icon:
                    self.icon.icon = self._create_icon_image("yellow")

        threading.Thread(target=do_setup, daemon=True).start()

    def _show_notification(self, title: str, message: str):
        """Show notification."""
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception:
                print(f"[{title}] {message}")

    def _quit(self, icon, item):
        """Quit the application."""
        self.clipboard_monitor.stop()
        icon.stop()

    def _create_menu(self):
        """Create system tray menu."""
        return pystray.Menu(
            pystray.MenuItem(
                "Add Clipboard to Calendar...",
                self._add_to_calendar_with_edit,
                default=True
            ),
            pystray.MenuItem(
                "Add Detected Event...",
                self._add_detected_event
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Status",
                self._show_status
            ),
            pystray.MenuItem(
                "Register Credentials...",
                self._setup_google
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Quit",
                self._quit
            )
        )

    def run(self):
        """Run the tray application."""
        # Start clipboard monitoring
        self.clipboard_monitor.start()

        # Determine initial icon color based on auth status
        if self.calendar_client.is_authenticated():
            icon_color = "green"
        elif self.calendar_client.is_configured():
            icon_color = "yellow"
        else:
            icon_color = "gray"

        # Create and run system tray icon
        self.icon = pystray.Icon(
            "calendar-to-google",
            self._create_icon_image(icon_color),
            "Calendar to Google",
            menu=self._create_menu()
        )

        print("Calendar to Google started")
        print("Ctrl+C to copy text with date -> notification appears")
        print("Right-click tray icon -> Edit and add to Google Calendar")

        self.icon.run()


def main():
    """Entry point."""
    app = TrayApp()
    app.run()


if __name__ == '__main__':
    main()
