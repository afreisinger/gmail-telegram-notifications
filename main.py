"""
This script handles the automation of email management in Gmail and sends
notifications to Telegram about deleted or important emails.
"""

import email
import imaplib
import json
import logging
from email.header import decode_header

import pandas as pd
import requests
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Configure left justification and maximum column width for pandas display
pd.set_option("display.colheader_justify", "left")
pd.set_option("display.max_colwidth", None)  # Avoid text truncation in columns


def load_credentials(filepath):
    """Load user, password, Telegram token, and chat ID from a YAML file."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            credentials = yaml.safe_load(file)
            user = credentials["user"]
            password = credentials["password"]
            telegram_token = credentials["telegram_token"]
            telegram_chat_id = credentials["telegram_chat_id"]
            return user, password, telegram_token, telegram_chat_id
    except Exception as e:
        logging.error("Failed to load credentials: {}".format(e))
        raise


def connect_to_gmail_imap(user, password):
    """Establish an IMAP connection to Gmail."""
    imap_url = "imap.gmail.com"
    try:
        mail = imaplib.IMAP4_SSL(imap_url)
        mail.login(user, password)
        mail.select("inbox")  # Connect to the inbox.
        return mail
    except Exception as e:
        logging.error("Connection failed: {}".format(e))
        raise


def get_emails_to_delete(mail, filepath):
    """Fetch and delete emails based on a list in JSON, and create a summary."""
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
            emails_to_delete = data["emails"]

        summary = pd.DataFrame(columns=["Email", "Count"])
        for email_addr in emails_to_delete:
            status, messages = mail.search(None, f'FROM "{email_addr}"')
            message_ids = messages[0].split()
            count = len(message_ids)

            # Mark emails as deleted
            for msg_id in message_ids:
                mail.store(msg_id, "+FLAGS", "\\Deleted")

            # Append to summary
            summary = pd.concat([summary, pd.DataFrame({"Email": [email_addr], "Count": [count]})], ignore_index=True)

        # Expunge (delete permanently) marked emails
        mail.expunge()
        return summary
    except Exception as e:
        logging.error("Failed to delete emails: {}".format(e))
        raise


def get_emails_to_notify(mail, filepath):
    """Fetch emails to notify from the inbox and create a notification summary."""
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
            emails_to_notify = data["emails"]

        summary = pd.DataFrame(columns=["From", "Subject"])
        for email_addr in emails_to_notify:
            status, messages = mail.search(None, f'(FROM "{email_addr}" UNSEEN)')
            message_ids = messages[0].split()

            for msg_id in message_ids:
                status, msg_data = mail.fetch(msg_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])

                # Decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding if encoding else "utf-8")

                # Get the email sender
                from_ = msg.get("From")

                mail.store(msg_id, "+FLAGS", "\\Seen")

                summary = pd.concat([summary, pd.DataFrame({"From": [from_], "Subject": [subject]})], ignore_index=True)

        summary["From"] = summary["From"].str.ljust(30)
        summary["Subject"] = summary["Subject"].str.ljust(50)
        return summary

    except Exception as e:
        logging.error("Failed to notify emails: {}".format(e))
        raise


def send_to_telegram(token, chat_id, message):
    """Send a notification message to a Telegram chat."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        logging.info("Notification sent to Telegram successfully.")
    except requests.exceptions.RequestException as e:
        logging.error("Failed to send message to Telegram: {}".format(e))


def main():
    """Main function to load credentials, connect to Gmail, and send notifications."""
    user, password, telegram_token, telegram_chat_id = load_credentials("credentials.yaml")
    mail = connect_to_gmail_imap(user, password)

    # Fetch and delete emails based on a list in JSON
    summary = get_emails_to_delete(mail, "delete_email_list.json")
    print(summary.to_markdown(index=False))
    summary.drop(summary.index, inplace=True)

    # Fetch emails to notify
    summary = get_emails_to_notify(mail, "notify_email_list.json")

    if summary.empty:
        message = "No new emails matching the criteria."
    else:
        message = "New email(s):\n" + summary.to_string(index=False)

    send_to_telegram(telegram_token, telegram_chat_id, message)
    print(summary.to_markdown(index=False))
    mail.logout()


if __name__ == "__main__":
    main()
