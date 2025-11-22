import gspread
from oauth2client.service_account import ServiceAccountCredentials
from PIL import Image, ImageDraw, ImageFont
import requests
import datetime
import io
import json
from telegram import Bot

print("=" * 50)
print("🎉 Birthday Bot Starting...")
print("=" * 50)

# LOAD CONFIGURATION
print("\n📋 Loading configuration...")
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    print("✅ Configuration loaded successfully!")
except FileNotFoundError:
    print("❌ ERROR: config.json not found!")
    exit(1)
except json.JSONDecodeError as e:
    print(f"❌ ERROR: Invalid JSON in config.json: {e}")
    exit(1)

# Extract configuration
SERVICE_ACCOUNT_JSON = config['google']['service_account_file']
SPREADSHEET_URL = config['google']['spreadsheet_url']
SHEET_NAME = config['google']['sheet_name']
TELEGRAM_BOT_TOKEN = config['telegram']['bot_token']
TELEGRAM_GROUP_CHAT_ID = config['telegram']['group_chat_id']
CLUB_NAME = config['customization']['club_name']
SEND_TO_GROUP = config['customization']['send_to_group']
SEND_PERSONAL_MESSAGES = config['customization']['send_personal_messages']
# Reminders removed as per user request
BACKGROUND_COLOR = tuple(config['poster_design']['background_color'])
TEXT_COLOR = tuple(config['poster_design']['text_color'])
POSTER_WIDTH = config['poster_design']['poster_width']
POSTER_HEIGHT = config['poster_design']['poster_height']
PHOTO_SIZE = config['poster_design']['photo_size']
RESERVED_COLUMNS = config['reserved_columns']['columns']
MESSAGE_TEMPLATES = config['event_message_templates']

# GOOGLE SHEETS AUTH
print("\n🔐 Authenticating with Google Sheets...")
try:
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_JSON, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url(SPREADSHEET_URL).worksheet(SHEET_NAME)
    data = sheet.get_all_records()
    print(f"✅ Connected to sheet '{SHEET_NAME}' - Found {len(data)} rows")
except FileNotFoundError:
    print(f"❌ ERROR: Service account file '{SERVICE_ACCOUNT_JSON}' not found!")
    exit(1)
except Exception as e:
    print(f"❌ ERROR: Failed to connect to Google Sheets: {e}")
    exit(1)

# GET TODAY'S DATE
today = datetime.datetime.today()

today_strs = [
    today.strftime('%d/%m'),  # DD/MM format
    today.strftime('%d-%m'),  # DD-MM format
]
print(f"\n📅 Today's date: {today.strftime('%B %d, %Y')} ({today_strs[0]})")

# IDENTIFY EVENT COLUMNS
all_columns = list(data[0].keys()) if data else []
event_columns = [col for col in all_columns if col not in RESERVED_COLUMNS]
print(f"\n📊 Event columns detected: {', '.join(event_columns)}")

# FIND TODAY'S EVENTS
print("\n🔍 Searching for today's events...")
events_today = []

for row in data:
    # Skip if Active column exists and is False
    if 'Active' in row:
        active_value = str(row['Active']).strip().upper()
        if active_value in ['FALSE', 'F', '0', 'NO']:
            continue

    name = row.get('Name', '').strip()
    photo_url = row.get('PhotoFile', '').strip()
    telegram_id = str(row.get('TelegramID', '')).strip()

    if not name or not photo_url:
        continue

    # Check each event column for today's date
    for event_col in event_columns:
        event_date = str(row.get(event_col, '')).strip()

        # Check for today's events
        if any(event_date.startswith(fmt) for fmt in today_strs):
            events_today.append({
                'name': name,
                'photo_url': photo_url,
                'telegram_id': telegram_id if telegram_id else None,
                'event_name': event_col
            })

print(f"✅ Found {len(events_today)} event(s) today!")
if events_today:
    for event in events_today:
        print(f"   • {event['name']} - {event['event_name']}")

if len(events_today) == 0:
    print("\n✨ No events today. Exiting.")
    exit(0)

# HELPER: Convert Google Drive URL to direct download link
def convert_drive_url(photo_url):
    if 'drive.google.com' in photo_url and '/d/' in photo_url:
        file_id = photo_url.split('/d/')[1].split('/')[0]
        return f'https://drive.google.com/uc?export=download&id={file_id}'
    return photo_url

# HELPER: Create poster
def create_poster(name, photo_url, event_name):
    # Convert Google Drive URL
    photo_url = convert_drive_url(photo_url)

    # Download photo
    response = requests.get(photo_url)
    if response.status_code != 200:
        raise Exception(f"Failed to download photo: HTTP {response.status_code}")

    img = Image.open(io.BytesIO(response.content)).resize((PHOTO_SIZE, PHOTO_SIZE))

    # Create base poster
    poster = Image.new('RGB', (POSTER_WIDTH, POSTER_HEIGHT), BACKGROUND_COLOR)
    poster.paste(img, (20, 60))

    # Draw text
    draw = ImageDraw.Draw(poster)

    # Try to load a larger font, fallback to default if not available
    try:
        # Try to use a TrueType font with larger size
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        font_medium = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()

    # Add event message with text wrapping
    message_line1 = f"Happy {event_name}"
    message_line2 = f"{name}!"

    # Right margin for text (leave 20px from right edge)
    max_text_width = POSTER_WIDTH - 220 - 20  # Starting at 220, 20px margin from right

    # Wrap text if too long
    from textwrap import wrap

    # Wrap first line if needed
    bbox1 = draw.textbbox((0, 0), message_line1, font=font_medium)
    if (bbox1[2] - bbox1[0]) > max_text_width:
        # Split "Happy {event_name}" into multiple lines
        words = message_line1.split()
        wrapped_lines = []
        current_line = words[0]
        for word in words[1:]:
            test_line = current_line + " " + word
            bbox = draw.textbbox((0, 0), test_line, font=font_medium)
            if (bbox[2] - bbox[0]) <= max_text_width:
                current_line = test_line
            else:
                wrapped_lines.append(current_line)
                current_line = word
        wrapped_lines.append(current_line)

        # Draw wrapped lines
        y_pos = 100
        for line in wrapped_lines:
            draw.text((220, y_pos), line, font=font_medium, fill=TEXT_COLOR)
            y_pos += 20
        draw.text((220, y_pos), message_line2, font=font_medium, fill=TEXT_COLOR)
    else:
        # Draw normally
        draw.text((220, 100), message_line1, font=font_medium, fill=TEXT_COLOR)
        draw.text((220, 120), message_line2, font=font_medium, fill=TEXT_COLOR)

    # Add club name at bottom center if configured
    if CLUB_NAME:
        # Calculate text width for centering
        bbox = draw.textbbox((0, 0), CLUB_NAME, font=font_large)
        text_width = bbox[2] - bbox[0]
        x_position = (POSTER_WIDTH - text_width) // 2
        y_position = POSTER_HEIGHT - 40  # 40 pixels from bottom

        draw.text((x_position, y_position), CLUB_NAME, font=font_large, fill=TEXT_COLOR)

    # Save poster to BytesIO
    output = io.BytesIO()
    poster.save(output, format='PNG')
    output.seek(0)
    return output

# INITIALIZE TELEGRAM BOT
print("\n🤖 Initializing Telegram bot...")
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# SEND POSTERS AND MESSAGES
print("\n📤 Sending messages...")

sent_count = 0
for event in events_today:
    try:
        print(f"\n  Processing: {event['name']} - {event['event_name']}")

        # Create poster
        poster = create_poster(event['name'], event['photo_url'], event['event_name'])

        # Format messages
        personal_msg = MESSAGE_TEMPLATES['personal'].format(
            name=event['name'],
            event_name=event['event_name']
        )
        group_msg = MESSAGE_TEMPLATES['group'].format(
            name=event['name'],
            event_name=event['event_name']
        )

        # Send personal message if enabled and TelegramID provided
        if SEND_PERSONAL_MESSAGES and event['telegram_id']:
            try:
                poster.seek(0)  # Reset stream position
                bot.send_photo(
                    chat_id=event['telegram_id'],
                    photo=poster,
                    caption=personal_msg
                )
                print(f"    ✅ Personal message sent to {event['name']}")
            except Exception as e:
                print(f"    ⚠️  Failed to send personal message: {e}")

        # Send to group if enabled
        if SEND_TO_GROUP:
            try:
                poster.seek(0)  # Reset stream position
                bot.send_photo(
                    chat_id=TELEGRAM_GROUP_CHAT_ID,
                    photo=poster,
                    caption=group_msg
                )
                print(f"    ✅ Group message sent")
            except Exception as e:
                print(f"    ⚠️  Failed to send group message: {e}")

        sent_count += 1

    except Exception as e:
        print(f"    ❌ Error processing {event['name']}: {e}")

print("\n" + "=" * 50)
print(f"✨ Finished! Processed {sent_count} event(s) successfully!")
print("=" * 50)
