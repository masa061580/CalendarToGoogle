"""Google Calendar API integration."""

import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from datetime import datetime
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .date_parser import ParsedEvent

# Google Calendar API scope
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Config directory
CONFIG_DIR = Path.home() / '.calendar-to-google'
CREDENTIALS_FILE = CONFIG_DIR / 'credentials.json'
TOKEN_FILE = CONFIG_DIR / 'token.json'


class GoogleCalendarClient:
    """Google Calendar API client."""

    def __init__(self):
        """Initialize the client."""
        self._service = None
        self._creds = None

    def is_configured(self) -> bool:
        """Check if credentials are configured."""
        exists = CREDENTIALS_FILE.exists()
        print(f"[Debug] Credentials path: {CREDENTIALS_FILE}")
        print(f"[Debug] Credentials exists: {exists}")
        return exists

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        if not self.is_configured():
            return False

        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
                return creds.valid or creds.refresh_token
            except Exception:
                return False
        return False

    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API."""
        if not self.is_configured():
            return False

        creds = None

        # Load existing token
        if TOKEN_FILE.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
            except Exception:
                pass

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception:
                    creds = None

            if not creds:
                try:
                    print(f"[Debug] Starting OAuth flow with: {CREDENTIALS_FILE}")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(CREDENTIALS_FILE), SCOPES
                    )
                    print("[Debug] Opening browser for authentication...")
                    creds = flow.run_local_server(port=0)
                    print("[Debug] Authentication successful!")
                except Exception as e:
                    print(f"Authentication failed: {e}")
                    import traceback
                    traceback.print_exc()
                    return False

            # Save credentials
            TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_FILE, 'w') as f:
                f.write(creds.to_json())

        self._creds = creds
        return True

    def _get_service(self):
        """Get or create Calendar service."""
        if self._service is None:
            if not self._creds:
                if not self.authenticate():
                    raise RuntimeError("Not authenticated")
            self._service = build('calendar', 'v3', credentials=self._creds)
        return self._service

    def add_event(self, event: ParsedEvent, calendar_id: str = 'primary') -> Optional[str]:
        """
        Add event to Google Calendar.

        Args:
            event: ParsedEvent to add
            calendar_id: Calendar ID (default: primary)

        Returns:
            Event URL if successful, None otherwise
        """
        try:
            service = self._get_service()

            if event.all_day:
                event_body = {
                    'summary': event.title,
                    'start': {
                        'date': event.start_date.strftime('%Y-%m-%d'),
                        'timeZone': 'Asia/Tokyo',
                    },
                    'end': {
                        'date': (event.end_date or event.start_date).strftime('%Y-%m-%d'),
                        'timeZone': 'Asia/Tokyo',
                    },
                }
            else:
                # 時間指定イベント（デフォルト1時間）
                end_date = event.end_date
                if not end_date:
                    from datetime import timedelta
                    end_date = event.start_date + timedelta(hours=1)

                event_body = {
                    'summary': event.title,
                    'start': {
                        'dateTime': event.start_date.isoformat(),
                        'timeZone': 'Asia/Tokyo',
                    },
                    'end': {
                        'dateTime': end_date.isoformat(),
                        'timeZone': 'Asia/Tokyo',
                    },
                }

            if event.description:
                event_body['description'] = event.description

            result = service.events().insert(
                calendarId=calendar_id,
                body=event_body
            ).execute()

            return result.get('htmlLink')

        except HttpError as e:
            print(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            print(f"Error adding event: {e}")
            return None

    def list_calendars(self) -> list:
        """List available calendars."""
        try:
            service = self._get_service()
            result = service.calendarList().list().execute()
            return result.get('items', [])
        except Exception as e:
            print(f"Error listing calendars: {e}")
            return []


def setup_credentials():
    """Set up Google Calendar API credentials."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Google Calendar API セットアップ")
    print("=" * 60)
    print()
    print("1. Google Cloud Console (https://console.cloud.google.com/) にアクセス")
    print("2. 新しいプロジェクトを作成するか、既存のプロジェクトを選択")
    print("3. 「APIとサービス」→「ライブラリ」で Google Calendar API を有効化")
    print("4. 「APIとサービス」→「認証情報」で OAuth 2.0 クライアント ID を作成")
    print("   - アプリケーションの種類: デスクトップアプリ")
    print("5. 作成した認証情報をダウンロード（credentials.json）")
    print()
    print(f"credentials.json を以下に配置してください:")
    print(f"  {CREDENTIALS_FILE}")
    print()

    return CREDENTIALS_FILE.exists()


def select_credentials_file() -> bool:
    """
    Open file dialog to select credentials.json and copy it to config directory.

    Returns:
        True if credentials were successfully registered, False otherwise
    """
    # Create a hidden root window
    root = ctk.CTk()
    root.withdraw()
    root.attributes('-topmost', True)

    # Show file selection dialog
    file_path = filedialog.askopenfilename(
        title="Google Calendar API credentials.json を選択",
        filetypes=[
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ],
        initialdir=str(Path.home() / "Downloads")
    )

    if not file_path:
        root.destroy()
        return False

    source_path = Path(file_path)

    # Validate the JSON file
    try:
        with open(source_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Check if it looks like a Google OAuth credentials file
        if 'installed' not in data and 'web' not in data:
            messagebox.showerror(
                "Invalid File",
                "選択されたファイルはGoogle OAuth認証情報ファイルではないようです。\n"
                "Google Cloud Consoleからダウンロードした正しいcredentials.jsonを選択してください。"
            )
            root.destroy()
            return False

    except json.JSONDecodeError:
        messagebox.showerror(
            "Invalid JSON",
            "選択されたファイルは有効なJSONファイルではありません。"
        )
        root.destroy()
        return False
    except Exception as e:
        messagebox.showerror(
            "Error",
            f"ファイルの読み込みに失敗しました: {e}"
        )
        root.destroy()
        return False

    # Create config directory and copy the file
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, CREDENTIALS_FILE)

        messagebox.showinfo(
            "Success",
            f"認証情報を登録しました。\n\n保存先: {CREDENTIALS_FILE}\n\n"
            "次回イベント追加時にGoogleアカウントでの認証が必要です。"
        )
        root.destroy()
        return True

    except Exception as e:
        messagebox.showerror(
            "Error",
            f"ファイルのコピーに失敗しました: {e}"
        )
        root.destroy()
        return False


def prompt_credentials_setup() -> bool:
    """
    Show a dialog prompting the user to set up credentials.

    Returns:
        True if user chose to select a file and succeeded, False otherwise
    """
    root = ctk.CTk()
    root.withdraw()
    root.attributes('-topmost', True)

    result = messagebox.askyesno(
        "Setup Required",
        "Google Calendar APIの認証情報が見つかりません。\n\n"
        "Google Cloud Consoleからダウンロードした\n"
        "credentials.jsonファイルを登録しますか？\n\n"
        "【セットアップ手順】\n"
        "1. Google Cloud Console にアクセス\n"
        "2. プロジェクトを作成/選択\n"
        "3. Google Calendar API を有効化\n"
        "4. OAuth 2.0 クライアントIDを作成\n"
        "   (デスクトップアプリ)\n"
        "5. 認証情報をダウンロード",
        icon='question'
    )

    root.destroy()

    if result:
        return select_credentials_file()
    return False
