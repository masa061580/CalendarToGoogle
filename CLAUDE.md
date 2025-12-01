# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Calendar to Google is a Windows system tray application that monitors the clipboard for date/event text and allows adding events to Google Calendar. It supports Japanese date formats and provides a GUI dialog for editing events before submission.

## Development Commands

```bash
# Install dependencies
uv sync

# Run the application
uv run calendar-to-google

# Or run directly
python -m calendar_to_google
```

## Architecture

### Module Structure

- `calendar_to_google/tray_app.py` - Main entry point. System tray icon using pystray, coordinates all components
- `calendar_to_google/date_parser.py` - Date/time extraction from text. Handles Japanese formats (年月日, 時分), relative dates (今日, 明日), weekdays (月曜日-日曜日)
- `calendar_to_google/clipboard_monitor.py` - Monitors Ctrl+C keypress using `keyboard` library, triggers date parsing
- `calendar_to_google/google_calendar.py` - Google Calendar API client with OAuth2 flow
- `calendar_to_google/edit_dialog.py` - tkinter dialog for editing event details before submission

### Data Flow

1. User copies text (Ctrl+C) → `ClipboardMonitor` detects via hotkey
2. `DateParser.parse()` extracts date/time/title → returns `ParsedEvent` dataclass
3. Tray icon turns yellow, notification shown
4. User right-clicks → `EventEditDialog` opens for editing
5. `GoogleCalendarClient.add_event()` sends to Google Calendar API

### Configuration

Credentials stored in `~/.calendar-to-google/`:
- `credentials.json` - OAuth client credentials (user provides)
- `token.json` - Cached auth token (auto-generated)

## Key Dependencies

- `pystray` - System tray icon
- `pyperclip` + `keyboard` - Clipboard monitoring
- `google-api-python-client` + `google-auth-oauthlib` - Google Calendar API
- `python-dateutil` - Date parsing fallback
- `pillow` - Icon image generation
- `tkinter` - Edit dialog (bundled with Python)
