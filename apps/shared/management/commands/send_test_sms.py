from django.core.management.base import BaseCommand
import requests
from decouple import config as env

class Command(BaseCommand):
    help = 'Send a test SMS using MNotify'

    def handle(self, *args, **options):
        # endPoint = 'https://api.mnotify.com/api/sms/quick'
        # apiKey = '20C9ZcV74Wmj3Dude5ZjIwdHn'
        # data = {
        #     'recipient[]': ['0545865156'],
        #     'sender': 'ACCI',
        #     'message': 'API messaging is fun!',
        #     'is_schedule': False,
        #     'schedule_date': ''
        # }
        # url = endPoint + '?key=' + apiKey
        # response = requests.post(url, data)
        # data = response.json()
        # print(data)

        endPoint = 'https://api.mnotify.com/api/balance/sms'
        apiKey = env("MNOTIFY_API_KEY")
        print(apiKey)
        url = endPoint + '?key=' + apiKey
        response = requests.get(url)
        data = response.json()
        print(data)
        # if data.status_code == 200:
        #     response_data = response.json()
        #     if response_data['status'] == 'success':
        #         self.stdout.write(self.style.SUCCESS(f'Successfully sent SMS! Response: {response_data}'))
        #     else:
        #         self.stdout.write(self.style.ERROR(f'SMS sending failed. Error: {response_data["error"]}'))
        # else:
        #     self.stdout.write(self.style.ERROR(f'Request failed. Status code: {response.status_code}'))

        #  20C9ZcV74Wmj3Dude5ZjIwdHn