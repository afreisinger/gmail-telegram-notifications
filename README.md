# Accessing Gmail with Python

This project provides a Python script to manage your Gmail account programmatically using the IMAP protocol. It demonstrates how to load credentials securely, connect to Gmail's IMAP server, delete emails based on specific criteria (e.g., sender), and send notifications to a Telegram chat.

This script will:

- Delete emails from `delete_email_list.json` from your Gmail account.
- Send a Telegram notification summarizing emails from `notify_email_list.json`.

## Table of Contents
- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
- [Output](#output)

## Requirements

1. **Python 3.x**: Ensure that Python 3.x is installed.
2. **Required Libraries**: The following libraries are needed:
   - `imaplib` (built-in) for handling IMAP connections
   - `yaml` for loading credentials
   - `logging` for error and info logging
   - `json` for reading email criteria from a JSON file
   - `pandas` for managing and displaying summary data
   - `requests` for sending notifications to Telegram
   - `email` (built-in) for handling email content and headers

## Setup

1. **Create a Virtual Environment**:
   - Run the following command to create a virtual environment:
     ```bash
     python3 -m venv .venv
     ```
   - Activate the virtual environment:
     - On **Linux/macOS**:
       ```bash
       source .venv/bin/activate
       ```
     - On **Windows**:
       ```bash
       .venv\Scripts\activate
       ```
2. **Install Dependencies**:
   - After activating the virtual environment, install external dependencies by running:
     ```bash
     pip install -r requirements.txt
     ```
3. **Create an App Password for Google IMAP**
   - If you have two-factor authentication enabled on your Gmail account, you’ll need to use an app password instead of your regular password to access Gmail via IMAP.
     - Sign into your Google Account.
     - Navigate to the Security section.
     - Under “Signing in to Google,” find and click on “App Passwords.
     - You might need to sign in again. If you don’t see “App Passwords,” ensure that 2FA is enabled.
     - At the bottom, select ‘Mail’ under ‘Select app’ and choose the device you’re using under ‘Select device’.
     - Click on ‘Generate’. Your app password will appear.

4. **Create a Bot on Telegram and Obtain the Access Token**
   - Open Telegram and search for the user **BotFather** (the official Telegram bot for managing other bots).
   - Start a chat with **BotFather** and send the command `/newbot` to create a new bot.
   - BotFather will ask you to choose a name for the bot. This can be anything, like `MyEmailNotifier`.
   - Next, you will need to choose a username for the bot, which must end in "bot" (e.g., `MyEmailNotifierBot`).
   - Once the bot is created, BotFather will give you an access token that you need to connect your bot to the script. This token will be in the format `123456789:ABCDEF123456abcdef123456789ABCDEF`.
   - Save this token in a secure place, as you will need it in the `credentials.yaml` configuration file for your script.

5. **Obtain Your Chat ID on Telegram**
   - To send messages to your account or group, you need the `chat_id`, which identifies the person or group where the bot should send messages. Here's how to obtain it:
      - **Send a message to your bot**: Open a conversation with your newly created bot in Telegram (search for its username in the Telegram search bar) and send any message, such as "Hello".
      - **Use the Telegram API to get the chat ID**: Open your browser and go to the following URL, replacing `<your_bot_token>` with your bot's token:
      ```html
      https://api.telegram.org/bot<your_bot_token>/getUpdates
      ```
      - This will open a page with information in JSON format. Look for the `chat` field, and inside it, you'll find the `id` of the chat. This number is your `chat_id`.
      - Example structure:
      ```json
      {
      "update_id": 12345678,
      "message": {
      "message_id": 34,
      "from": {
        "id": 123456789,
        "is_bot": false,
        "first_name": "YourName",
        "username": "YourUsername",
        "language_code": "en"
      },
      "chat": {
        "id": 123456789,   // <-- This is the chat ID
        "first_name": "YourName",
        "username": "YourUsername",
        "type": "private"
      },
      "date": 1620034567,
      "text": "Hello"
      }
      }
      ```
      - This chat_id is used in the credentials.yaml file so that the bot knows where to send notifications.

6. **Create a YAML Credentials File**:
   - Create a file named `credentials.yaml` with your Gmail and Telegram credentials in the following format:
     ```yaml
     user: "your_email@gmail.com"
     password: "your_app_password"
     telegram_token: "your_telegram_bot_token"
     telegram_chat_id: "your_telegram_chat_id"
     ```
7. **Define Emails to Delete or Notify**:
   - **Emails to Delete**:
     - Create a file named `delete_email_list.json` with the email addresses to delete, structured like this:
       ```json
       {
         "emails": [
           "example1@example.com",
           "example2@example.com"
         ]
       }
       ```
   - **Emails to Notify**:
     - Create a file named `notify_email_list.json` with the email addresses to notify, structured like this:
       ```json
       {
         "emails": [
           "example3@example.com",
           "example4@example.com"
         ]
       }
       ```
    - **Emails to download attachments**:
      - Create a file named `attachment_senders.json` with the email addresses to download attachment, structured like this:
       ```json
       {
         "emails": [
           "example3@example.com",
           "example4@example.com"
         ]
       }
       ```

## Usage

1. Clone the repository and navigate to the project directory.
2. **Activate the virtual environment**:
   - On **Linux/macOS**:
     ```bash
     source .venv/bin/activate
     ```
   - On **Windows**:
     ```bash
     .venv\Scripts\activate
     ```
3. Run the main script by executing:
   ```bash
   python main.py
   ```

## Output:
- The script will print a summary of deleted and notified emails to the terminal.
- A Telegram message will be sent with a list of new emails matching the criteria in `notify_email_list.json`.
- Downloads attachments into `./attachments` folder.


