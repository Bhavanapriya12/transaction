import requests


devs = {
    'Bhavana': '1331794477',
    # 'teju_mam': '6089466878'
}
BOT_API_TOKEN = "6974807327:AAGaO_XzF4b8P3OWs5HBVzyJhPeYw9adtsw"
bot_token = BOT_API_TOKEN

def send_message(chat_id, message):
    try:
    
        base_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        url = f"{base_url}?chat_id={chat_id}&text={message}"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for non-200 responses
    except requests.exceptions.RequestException as err:
        print("Error in sending alert:", err)

def alert_dev(message):
    for chat_id in devs.values():
        send_message(chat_id, message)