import requests
from django.conf import settings
from decouple import config as env


def initialize(email: str, amount: int, currency: str) -> dict:
    """Initializes a payment with Paystack and returns authorization URL and reference."""
    url = f"https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer sk_test_a119c12e9eccd6fc2dd290ed11e39bd6bc9213d2",
        "Content-Type": "application/json",
    }
    callback_url = f'https://backend.accihq.org/api/v1/complete-payment'

    payload = {
        "email": email,
        "amount": amount * 100,
        "currency": currency,
        "callback_url": callback_url,
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"Paystack Response: {response.status_code}, {response.text}")

    if response.status_code == 200:
        response_data = response.json()
        print(response_data)
        if response_data.get("status"):
            return {
                "payment_url": response_data["data"]["authorization_url"],
                "reference": response_data["data"]["reference"],
            }
    raise ValueError("Payment initialization failed")


def verify_payment(reference: str) -> dict:
    """ Verifies payment status with Paystack. """
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {"Authorization": f"Bearer sk_test_a119c12e9eccd6fc2dd290ed11e39bd6bc9213d2"}

    response = requests.get(url, headers=headers)
    response_data = response.json()
    print(response_data)
    if response.status_code == 200 and response_data.get("status"):
        return {"status": "success", "data": response_data["data"]}

    return {"status": "failure", "data": None}
