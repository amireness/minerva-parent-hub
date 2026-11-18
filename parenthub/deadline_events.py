"""Exact deadlines reviewed independently of published month/day tables."""

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

from flask import current_app


ADMISSIONS_URL = 'https://www.minerva.edu/undergraduate/admissions/'
EXACT_DEADLINES = json.loads(Path(__file__).with_name('content.json').read_text(encoding='utf-8'))['exact_deadlines']


@dataclass(frozen=True)
class DeadlineEvent:
    slug: str
    title: str
    at: datetime
    source: str
    verified_on: date
    round_slug: str | None

    @property
    def display_time(self):
        offset = self.at.strftime('%z')
        zone = 'UTC' if offset == '+0000' else f'UTC{offset[:3]}:{offset[3:]}'
        time_format = '%I:%M:%S %p' if self.at.second else '%I:%M %p'
        return f'{self.at:%B} {self.at.day}, {self.at.year} at {self.at.strftime(time_format).lstrip("0")} ({zone})'


def upcoming_events(now, rounds=()):
    events = []
    for row in current_app.config.get('EXACT_DEADLINES', EXACT_DEADLINES):
        try:
            at = datetime.fromisoformat(row['at'].replace('Z', '+00:00'))
            source = urlsplit(row['source'])
            verified = date.fromisoformat(row['verified_on'])
            round_slug = row.get('round_slug')
            if (at.utcoffset() is None or at <= now or verified > now.date()
                or source.scheme != 'https' or source.netloc != 'www.minerva.edu'
                or any(char.isspace() for char in row['source'])
                or not isinstance(row['title'], str) or not row['title'].strip()
                or not re.fullmatch(r'[a-z0-9-]+', row['slug'])):
                continue
            events.append(DeadlineEvent(row['slug'], row['title'], at, row['source'], verified, round_slug))
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    if rounds:
        events = [event for event in events if event.round_slug is None or event.round_slug in rounds]
    return sorted(events, key=lambda event: (event.at, event.slug))


def homepage_deadline(now, rounds=()):
    events = upcoming_events(now, rounds)
    return next((event for event in events if event.round_slug in rounds), events[0] if events else None)


def calendar_bytes(event, now):
    def escape(value):
        return (value.replace('\\', '\\\\').replace('\r\n', '\n').replace('\r', '\n')
                .replace('\n', '\\n').replace(',', '\\,').replace(';', '\\;'))

    def fold(line):
        chunk = b''
        for char in line:
            encoded = char.encode('utf-8')
            if len(chunk) + len(encoded) > 75:
                yield chunk
                chunk = b' '
            chunk += encoded
        yield chunk

    def timestamp(value):
        return value.astimezone(timezone.utc).strftime('%Y%m%dT%H%M%SZ')

    lines = (
        'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Parent Hub//Minerva deadline//EN',
        'BEGIN:VEVENT', f'UID:{event.slug}@minerva-parent-hub', f'DTSTAMP:{timestamp(now)}',
        f'DTSTART:{timestamp(event.at)}', f'SUMMARY:{escape(event.title)}',
        f'DESCRIPTION:Verified {event.verified_on}\\n{escape(event.source)}',
        f'URL:{event.source}', 'END:VEVENT', 'END:VCALENDAR',
    )
    return b'\r\n'.join(part for line in lines for part in fold(line)) + b'\r\n'
