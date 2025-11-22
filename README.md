# Birthday Bot

Automated Telegram bot that posts beautiful celebration posters for birthdays, anniversaries, work milestones, and any custom events. Runs daily on GitHub Actions - completely free!

## Features

- Automatically posts celebration posters to Telegram groups
- Supports multiple event types: Birthdays, Anniversaries, Work Anniversaries, and custom events
- Sends optional personal messages to individuals
- Customizable poster design (colors, sizes, club/organization name)
- Flexible date format (DD/MM or DD/MM/YYYY)
- Reads member data from Google Sheets
- Free automated daily execution via GitHub Actions
- No coding required - everything is configured through settings!

## Quick Start (5 Minutes!)

Want to use this bot for your organization? Here's what you'll do:

1. **Fork this repository** (creates your own copy)
2. **Create a Telegram bot** (via @BotFather) - Get your bot token
3. **Create a Google Sheet** with your members' data (names, photos, event dates)
4. **Create Google Cloud credentials** (service account) - Get the JSON file
5. **Configure your settings** in a `config.json` file (add YOUR club name, YOUR colors, YOUR bot token, etc.)
6. **Add secrets to GitHub** (paste your config.json and Google credentials as encrypted secrets)
7. **Enable GitHub Actions** - Your bot runs automatically every day at 9 AM!

**Each organization gets their own completely independent bot with their own branding, colors, and members!**

## Detailed Setup Guide

### Step 1: Create a Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot` and follow the instructions
3. Choose a name and username for your bot
4. Copy the **bot token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Add your bot to your Telegram group
6. Make the bot an **admin** in the group

### Step 2: Get Your Telegram Group Chat ID

1. Add the bot to your group
2. Send a message in the group
3. Visit this URL in your browser (replace `YOUR_BOT_TOKEN` with your actual token):
   ```
   https://api.telegram.org/botYOUR_BOT_TOKEN/getUpdates
   ```
4. Look for `"chat":{"id":-1234567890` - copy the negative number (e.g., `-1234567890`)

### Step 3: Set Up Google Sheets

1. Create a new Google Sheet with these columns:

   **Required columns:**
   - `Name` - Person's full name
   - `PhotoFile` - Google Drive link to their photo

   **Optional columns:**
   - `Active` - TRUE/FALSE to temporarily enable/disable people
   - `TelegramID` - Their Telegram ID for personal messages (optional)

   **Event columns** (you can add as many as you want and name them anything):
   - `Birthday` - Format: DD/MM or DD/MM/YYYY (e.g., 22/11 or 22/11/1990)
   - `Wedding Anniversary` - Format: DD/MM or DD/MM/YYYY
   - `Work Anniversary` - Format: DD/MM or DD/MM/YYYY
   - Add any custom event columns you want!

2. For photos, upload images to Google Drive and use "Get link" → "Anyone with the link can view"

### Step 4: Create Google Cloud Service Account

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing one)
3. Enable **Google Sheets API** and **Google Drive API**
4. Go to **Credentials** → **Create Credentials** → **Service Account**
5. Create a service account and download the JSON key file
6. Open your Google Sheet and click **Share**
7. Add the service account email (found in the JSON file) as an **Editor**

### Step 5: Fork This Repository

1. Click the **Fork** button at the top right of this page
2. This creates your own copy of the bot

### Step 6: Configure GitHub Secrets

1. Go to your forked repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add these secrets:

   **Secret name:** `CONFIG_JSON`
   **Value:** Your complete config.json (see template below)

   **Secret name:** `GOOGLE_CREDENTIALS`
   **Value:** Paste the entire contents of your Google service account JSON file

### Step 7: Create Your config.json

Create a file called `config.json` with this structure. **This is where you customize everything for YOUR organization:**

```json
{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN_HERE",
    "group_chat_id": "-YOUR_GROUP_CHAT_ID_HERE"
  },

  "google": {
    "service_account_file": "credentials.json",
    "spreadsheet_url": "YOUR_GOOGLE_SHEET_URL_HERE",
    "sheet_name": "Sheet1"
  },

  "customization": {
    "club_name": "Your Club Name Here",  ← CHANGE THIS to your organization name!
    "send_to_group": true,
    "send_personal_messages": true
  },

  "poster_design": {
    "background_color": [255, 228, 196],  ← CHANGE THESE to your preferred colors!
    "text_color": [80, 40, 100],          ← RGB format: [Red, Green, Blue]
    "poster_width": 400,
    "poster_height": 300,
    "photo_size": 180
  },

  "event_message_templates": {
    "personal": "🎉 Happy {event_name}, {name}! Wishing you all the best! 💫",  ← Customize messages!
    "group": "🎉 It's {name}'s {event_name} today! 🎊"
  },

  "reserved_columns": {
    "columns": ["Name", "PhotoFile", "TelegramID", "Active"]
  }
}
```

**Important - Replace These Values:**
- `YOUR_BOT_TOKEN_HERE` → Your Telegram bot token from @BotFather
- `-YOUR_GROUP_CHAT_ID_HERE` → Your group chat ID (must be negative, e.g., -1234567890)
- `YOUR_GOOGLE_SHEET_URL_HERE` → Your Google Sheet URL
- `"Your Club Name Here"` → **YOUR organization name** (e.g., "Mumbai Toastmasters", "Tech Team", etc.)
- `background_color` and `text_color` → **YOUR preferred colors** (RGB format)
- Message templates → **YOUR custom messages**

**Keep This As-Is:**
- `"service_account_file": "credentials.json"` (GitHub Actions handles this automatically)

### Step 8: Enable GitHub Actions

1. Go to your repository's **Actions** tab
2. Click **I understand my workflows, go ahead and enable them**
3. The bot will now run automatically every day at 9:00 AM UTC

### Step 9: Test Manually (Optional)

1. Go to **Actions** tab
2. Click **Birthday Bot Daily Check**
3. Click **Run workflow** → **Run workflow**
4. Wait a few seconds and check your Telegram group!

## Customization Options

### Poster Design

Edit the `poster_design` section in config.json:

- `background_color`: RGB color (0-255 for each: Red, Green, Blue)
- `text_color`: RGB color for text
- `poster_width`: Width in pixels
- `poster_height`: Height in pixels
- `photo_size`: Size of the member's photo in pixels

### Message Templates

Edit the `event_message_templates` section:

- Use `{name}` for the person's name
- Use `{event_name}` for the event type (Birthday, Anniversary, etc.)

### Club Name

Set `club_name` to your organization's name - it will appear centered at the bottom of posters in large font.

## Date Format

- Use **DD/MM** format (e.g., 22/11 for November 22)
- Or **DD/MM/YYYY** if you want to include the year (e.g., 22/11/1990)
- If year is unknown, you can use DD/MM, DD/MM/0000, or leave it blank

## Renaming Event Columns

You can rename event columns in your Google Sheet to anything you want! The bot will automatically detect them and use the column name in messages.

For example:
- Rename "Birthday" to "Special Day"
- Rename "Anniversary" to "Wedding Anniversary"
- Add custom columns like "Joining Day", "Graduation Day", etc.

Just make sure the column name is NOT in the reserved columns list (Name, PhotoFile, TelegramID, Active).

## Troubleshooting

### Bot not posting to group
- Check that bot is added to the group and is an admin
- Verify the chat ID is negative (e.g., -1234567890)

### "Chat not found" error
- Make sure the chat ID is in negative format
- Verify the bot is still in the group

### Photos not loading
- Ensure Google Drive links are set to "Anyone with the link can view"
- Check that the service account email has access to the Google Sheet

### No events detected
- Verify date format is DD/MM or DD/MM/YYYY
- Check that the date column is not in reserved columns
- Ensure Active column is TRUE (or remove the Active column entirely)

## Support

If you encounter issues:
1. Check the **Actions** tab for error logs
2. Verify all secrets are correctly configured
3. Ensure Google Sheet permissions are set correctly

## License

Free to use and modify for your organization!

## Credits

Built for communities to celebrate their members automatically.
