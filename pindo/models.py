
from django.db import models
from ticket_app import settings
import environ
env=environ.Env()


import requests


# Create your models here.
from ticket_app.settings import env

token_url = settings.PINDO_TOKEN_URL


class PindoSMS():
    @staticmethod
    def get_pindo_token():

        # authorization=HTTPBasicAuth(settings.API_USER, settings.API_KEY)
        authorization = (settings.PINDO_USERNAME, settings.PINDO_PASSWORD)
        try:
            #
            r = requests.get(token_url,
                             auth=authorization,)
            #print("This is the tocken")
            print(r.json)
            return r.json()
        except Exception as e:
            print(e)
        return None

    @staticmethod
    def sendSMS(to, text):
        token = PindoSMS.get_pindo_token()
        if not token is None:
            access_token = token['token']

            # print(authorization)
            try:
                headers = {'Authorization': 'Bearer ' + access_token}
                data = {'to': to, 'text': text, 'sender': settings.PINDO_SENDER}
                url = settings.PINDO_SEND_URL
                response = requests.post(url, json=data, headers=headers)
                print(response)
                print(response.json())

                return response.json()

            except ValueError as e:
                print(e)
                return None

        else:
            return None
