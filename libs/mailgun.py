import os
import requests


def send_message(to, subject, text):
    response = requests.post(
        "https://api.mailgun.net/v3/mg.clic.so/messages",
        auth=("api", os.environ['MAILGUN_TOKEN']),
        data={"from": "Breakroom <hello@breakroom.show>",
              "to": [to],
              "subject": subject,
              "text": text})

    return response.json()
