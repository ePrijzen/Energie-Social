import os
import json
import logging
import hashlib
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class API_Requests(object):
    def __init__(self, api_credentials:dict, bearer_key:str = "") -> None:
        self.api_credentials = api_credentials
        self.bearer_key = bearer_key

    def api_request(self, endpoint:str, payload:str, post_get:str="GET")->dict:
        try:
            reqUrl = f"http://{self.api_credentials['ip']}:{self.api_credentials['port']}{endpoint}"
            if self.bearer_key is None:
                headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json"
                }
            else:
                headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.bearer_key}"
            }

            response = requests.request(post_get, reqUrl, data=payload, headers=headersList, timeout=5)

            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    def get_hashed_password(self)->str:
        try:
            if self.api_credentials['password'] is None or self.api_credentials['salt'] is None:
                raise Exception('Geen wachtwoord of salt?')

            # Adding salt at the last of the password
            salted_password = self.api_credentials['password']+self.api_credentials['salt']
            # Encoding the password
            hashed_password = hashlib.md5(salted_password.encode())

            return hashed_password.hexdigest()
        except Exception as e:
            log.critical(e, exc_info=True)
            return ""








