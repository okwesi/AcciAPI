from django.core.management.base import BaseCommand
import requests
from decouple import config as env

class Command(BaseCommand):
    help = 'Send a test SMS using MNotify'

    def handle(self, *args, **options):
        end_point = 'https://api.mnotify.com/api/sms/quick'
        api_key = env("MNOTIFY_API_KEY")
        data = {
            'recipient[]': ["233545865156"],
            'sender': 'ACCI',
            'message': "Message is working",
        }
        url = end_point + '?key=' + api_key
        response = requests.post(url, data)
        data = response.json()
        print(data)