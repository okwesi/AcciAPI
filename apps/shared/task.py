import requests
from decouple import config as env


def send_sms(phone_number, message, sender_id):
    end_point = 'https://api.mnotify.com/api/sms/quick'
    api_key = env("MNOTIFY_API_KEY")
    data = {
        'recipient[]': [phone_number],
        'sender': sender_id,
        'message': message,
    }
    url = end_point + '?key=' + api_key
    response = requests.post(url, data)
    data = response.json()

    if data["error"]:
        return ("We're experiencing a temporary issue. Our team is working to resolve it as quickly as"
                " possible. Please try again later. Thank you for your patience!")
