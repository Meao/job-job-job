import requests

from config import BOT_TOKEN, CHAT_ID


def send_to_telegram(message):
    """
    Send a message to a Telegram bot.
    Args:
        message: The message to send.
    """
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}

    try:
        # Set a timeout of 5 seconds
        response = requests.post(url, data=payload, timeout=5)
        response.raise_for_status()  # Raise an error for bad responses
        print("Message sent to Telegram.")
    except requests.exceptions.Timeout:
        print("The request timed out.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
