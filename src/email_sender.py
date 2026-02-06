import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
from datetime import datetime
from collections import defaultdict
from scrapers.base_scraper import Event


class EmailSender:
    """Handles email notifications for music events."""

    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str,
                 sender_password: str, recipients: List[str], subject: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipients = recipients
        self.subject = subject

    def group_events_by_date_and_venue(self, events: List[Event]) -> Dict[str, Dict[str, List[Event]]]:
        """Group events by date, then by venue."""
        grouped = defaultdict(lambda: defaultdict(list))
        for event in events:
            date_str = event.date.strftime('%A, %B %d, %Y')
            grouped[date_str][event.venue].append(event)
        return grouped

    def format_events_html(self, events: List[Event]) -> str:
        """Format events as HTML email body with consolidated venue listings."""
        if not events:
            return """
            <html>
                <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px;">
                    <h1 style="color: #2c3e50;">Boston Live Music</h1>
                    <p style="color: #7f8c8d;">No events found for the upcoming days.</p>
                </body>
            </html>
            """

        # Sort events and group by date and venue
        sorted_events = sorted(events, key=lambda e: (e.date, e.venue))
        grouped = self.group_events_by_date_and_venue(sorted_events)

        html = """
        <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        max-width: 800px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f5f5f5;
                    }
                    h1 {
                        color: #2c3e50;
                        border-bottom: 3px solid #3498db;
                        padding-bottom: 10px;
                    }
                    h2 {
                        color: #34495e;
                        margin-top: 30px;
                        margin-bottom: 15px;
                        border-left: 4px solid #3498db;
                        padding-left: 10px;
                    }
                    .venue-block {
                        background-color: white;
                        padding: 15px;
                        margin-bottom: 15px;
                        border-radius: 5px;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }
                    .venue {
                        font-weight: bold;
                        color: #2980b9;
                        font-size: 16px;
                        margin-bottom: 10px;
                    }
                    .event-item {
                        margin-left: 15px;
                        margin-bottom: 8px;
                        padding-bottom: 8px;
                        border-bottom: 1px solid #ecf0f1;
                    }
                    .event-item:last-child {
                        border-bottom: none;
                        margin-bottom: 0;
                        padding-bottom: 0;
                    }
                    .title {
                        font-size: 15px;
                        color: #2c3e50;
                        margin: 3px 0;
                    }
                    .time {
                        color: #7f8c8d;
                        font-size: 14px;
                        margin: 2px 0;
                    }
                    .genre {
                        color: #27ae60;
                        font-size: 13px;
                        font-style: italic;
                        margin: 2px 0;
                    }
                    .link {
                        color: #3498db;
                        text-decoration: none;
                        font-size: 13px;
                    }
                    .link:hover {
                        text-decoration: underline;
                    }
                    .footer {
                        margin-top: 40px;
                        padding-top: 20px;
                        border-top: 2px solid #bdc3c7;
                        color: #7f8c8d;
                        font-size: 12px;
                        text-align: center;
                    }
                </style>
            </head>
            <body>
                <h1>🎵 Boston Live Music</h1>
        """

        # Process each date
        for date_str in sorted(grouped.keys(), key=lambda d: datetime.strptime(d, '%A, %B %d, %Y')):
            html += f'<h2>{date_str}</h2>\n'

            # Process each venue on this date
            for venue in sorted(grouped[date_str].keys()):
                venue_events = grouped[date_str][venue]
                html += '<div class="venue-block">\n'
                html += f'  <div class="venue">{venue}</div>\n'

                # Add all events for this venue
                for event in venue_events:
                    html += '  <div class="event-item">\n'
                    html += f'    <div class="title">{event.title}</div>\n'

                    if event.time:
                        html += f'    <div class="time">⏰ {event.time}</div>\n'

                    if event.genre:
                        html += f'    <div class="genre">🎸 {event.genre}</div>\n'

                    if event.url:
                        html += f'    <div><a class="link" href="{event.url}" target="_blank">More info</a></div>\n'

                    html += '  </div>\n'

                html += '</div>\n'

        html += """
                <div class="footer">
                    This email was automatically generated by Music Finder.<br>
                    Enjoy the shows!
                </div>
            </body>
        </html>
        """

        return html

    def format_events_plain(self, events: List[Event]) -> str:
        """Format events as plain text email body with consolidated venue listings."""
        if not events:
            return "No events found for the upcoming days."

        # Sort events and group by date and venue
        sorted_events = sorted(events, key=lambda e: (e.date, e.venue))
        grouped = self.group_events_by_date_and_venue(sorted_events)

        text = "BOSTON LIVE MUSIC\n"
        text += "=" * 60 + "\n\n"

        for date_str in sorted(grouped.keys(), key=lambda d: datetime.strptime(d, '%A, %B %d, %Y')):
            text += f"\n{date_str}\n"
            text += "-" * 60 + "\n\n"

            for venue in sorted(grouped[date_str].keys()):
                venue_events = grouped[date_str][venue]

                if len(venue_events) == 1:
                    # Single event - simple format
                    event = venue_events[0]
                    text += f"{venue}: {event.title}\n"
                    if event.time:
                        text += f"  Time: {event.time}\n"
                    if event.genre:
                        text += f"  Genre: {event.genre}\n"
                    if event.url:
                        text += f"  More info: {event.url}\n"
                else:
                    # Multiple events - consolidated format
                    text += f"{venue}:\n"
                    for event in venue_events:
                        text += f"  • {event.title}\n"
                        if event.time:
                            text += f"    Time: {event.time}\n"
                        if event.genre:
                            text += f"    Genre: {event.genre}\n"
                        if event.url:
                            text += f"    More info: {event.url}\n"

                text += "\n"

        text += "=" * 60 + "\n"
        text += "This email was automatically generated by Music Finder.\n"
        text += "Enjoy the shows!\n"

        return text

    def send_email(self, events: List[Event]) -> bool:
        """Send email with event information."""
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = self.subject
            message['From'] = self.sender_email
            message['To'] = ', '.join(self.recipients)

            # Create plain text and HTML versions
            text_content = self.format_events_plain(events)
            html_content = self.format_events_html(events)

            # Attach both versions
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')

            message.attach(part1)
            message.attach(part2)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            print(f"Email sent successfully to {', '.join(self.recipients)}")
            print(f"Total events: {len(events)}")
            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False
