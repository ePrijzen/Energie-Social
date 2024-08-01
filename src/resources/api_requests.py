import os
import logging
import hashlib
import models

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class API_Requests(object):
    def __init__(self, api_credentials:dict={}) -> None:
        self.api_credentials = api_credentials
        self.ip = self.api_credentials['ip']
        self.port = self.api_credentials['port']
        self.http = self.api_credentials['http']
        self.email = self.api_credentials['email']
        self.password = self.api_credentials['password']
        self.salt = self.api_credentials['salt']
        pass

    def api_request(self, endpoint:str, payload:dict)->dict:
        try:
            reqUrl = f"http://{self.api_credentials['ip']}:{self.api_credentials['port']}{endpoint}"
            headersList = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_credentials['bearer_key']}"
            }
            response = models.request("GET", reqUrl, data=payload, headers=headersList, timeout=5) # type: ignore
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            log.error(e, exc_info=True)
            return {}

    def get_hashed_password(self)->str:
        try:
            if self.password is None or self.salt is None:
                raise Exception('Geen wachtwoord of salt?')

            # Adding salt at the last of the password
            salted_password = self.password+self.salt
            # Encoding the password
            hashed_password = hashlib.md5(salted_password.encode())

            return hashed_password.hexdigest()
        except Exception as e:
            log.critical(e, exc_info=True)
            return ""


