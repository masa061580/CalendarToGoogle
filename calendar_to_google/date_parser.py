"""Date and event parsing from text."""

import re
from datetime import datetime, timedelta
from dateutil import parser as dateutil_parser
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParsedEvent:
    """Parsed event information."""
    title: str
    start_date: datetime
    end_date: Optional[datetime] = None
    all_day: bool = True
    description: str = ""


class DateParser:
    """Parse dates and events from text."""

    # 日本語の日付パターン
    JP_DATE_PATTERNS = [
        # 2024年12月25日
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        # 12月25日
        r'(\d{1,2})月(\d{1,2})日',
        # 2024/12/25 or 2024-12-25
        r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})',
        # 12/25 or 12-25
        r'(\d{1,2})[/\-](\d{1,2})',
    ]

    # 時間パターン
    TIME_PATTERNS = [
        # 14:30 or 14時30分
        r'(\d{1,2})[:\u6642](\d{2})(?:\u5206)?',
        # 14時
        r'(\d{1,2})\u6642(?!\d)',
    ]

    # 日本語の相対日付
    JP_RELATIVE_DATES = {
        '今日': 0,
        '本日': 0,
        '明日': 1,
        '明後日': 2,
        'あさって': 2,
        '昨日': -1,
        '一昨日': -2,
        'おととい': -2,
    }

    # 曜日
    JP_WEEKDAYS = {
        '月曜': 0, '月曜日': 0,
        '火曜': 1, '火曜日': 1,
        '水曜': 2, '水曜日': 2,
        '木曜': 3, '木曜日': 3,
        '金曜': 4, '金曜日': 4,
        '土曜': 5, '土曜日': 5,
        '日曜': 6, '日曜日': 6,
    }

    def parse(self, text: str) -> Optional[ParsedEvent]:
        """
        Parse text to extract event information.

        Args:
            text: Text containing date/event information

        Returns:
            ParsedEvent if date found, None otherwise
        """
        text = text.strip()
        if not text:
            return None

        # 日付を抽出
        date_info = self._extract_date(text)
        if not date_info:
            return None

        start_date, date_str = date_info

        # 時間を抽出
        time_info = self._extract_time(text)
        all_day = True
        if time_info:
            start_hour, start_minute = time_info
            start_date = start_date.replace(hour=start_hour, minute=start_minute)
            all_day = False

        # タイトルを抽出（日付部分を除いた残り）
        title = self._extract_title(text, date_str)

        return ParsedEvent(
            title=title if title else "新しい予定",
            start_date=start_date,
            all_day=all_day,
            description=text if title else "",
        )

    def _extract_date(self, text: str) -> Optional[tuple[datetime, str]]:
        """Extract date from text."""
        now = datetime.now()

        # 相対日付をチェック
        for jp_date, days_offset in self.JP_RELATIVE_DATES.items():
            if jp_date in text:
                date = now + timedelta(days=days_offset)
                return date.replace(hour=0, minute=0, second=0, microsecond=0), jp_date

        # 曜日をチェック
        for weekday_name, weekday_num in self.JP_WEEKDAYS.items():
            if weekday_name in text:
                days_ahead = weekday_num - now.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                date = now + timedelta(days=days_ahead)
                return date.replace(hour=0, minute=0, second=0, microsecond=0), weekday_name

        # 日本語日付パターン
        # 2024年12月25日
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', text)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            try:
                return datetime(year, month, day), match.group(0)
            except ValueError:
                pass

        # 12月25日 (年は現在年を使用)
        match = re.search(r'(\d{1,2})月(\d{1,2})日', text)
        if match:
            month, day = int(match.group(1)), int(match.group(2))
            year = now.year
            # 過去の日付なら来年
            try:
                date = datetime(year, month, day)
                if date < now:
                    date = datetime(year + 1, month, day)
                return date, match.group(0)
            except ValueError:
                pass

        # 2024/12/25 or 2024-12-25
        match = re.search(r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})', text)
        if match:
            year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
            try:
                return datetime(year, month, day), match.group(0)
            except ValueError:
                pass

        # 12/25 or 12-25
        match = re.search(r'(\d{1,2})[/\-](\d{1,2})', text)
        if match:
            month, day = int(match.group(1)), int(match.group(2))
            year = now.year
            try:
                date = datetime(year, month, day)
                if date < now:
                    date = datetime(year + 1, month, day)
                return date, match.group(0)
            except ValueError:
                pass

        # dateutilでパース
        try:
            parsed = dateutil_parser.parse(text, fuzzy=True)
            return parsed, ""
        except Exception:
            pass

        return None

    def _extract_time(self, text: str) -> Optional[tuple[int, int]]:
        """Extract time from text."""
        # 14:30 or 14時30分
        match = re.search(r'(\d{1,2})[:\u6642](\d{2})(?:\u5206)?', text)
        if match:
            hour, minute = int(match.group(1)), int(match.group(2))
            if 0 <= hour < 24 and 0 <= minute < 60:
                return hour, minute

        # 14時
        match = re.search(r'(\d{1,2})\u6642(?!\d)', text)
        if match:
            hour = int(match.group(1))
            if 0 <= hour < 24:
                return hour, 0

        return None

    def _extract_title(self, text: str, date_str: str) -> str:
        """Extract event title from text."""
        title = text

        # 日付文字列を除去
        if date_str:
            title = title.replace(date_str, '')

        # 時間を除去
        title = re.sub(r'\d{1,2}[:\u6642]\d{2}(?:\u5206)?', '', title)
        title = re.sub(r'\d{1,2}\u6642(?!\d)', '', title)

        # 相対日付を除去
        for jp_date in self.JP_RELATIVE_DATES:
            title = title.replace(jp_date, '')

        # 曜日を除去
        for weekday in self.JP_WEEKDAYS:
            title = title.replace(weekday, '')

        # 不要な記号を除去してトリム
        title = re.sub(r'[（）()\[\]【】\s]+', ' ', title)
        title = title.strip(' 　、。・')

        return title
