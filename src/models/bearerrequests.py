import os
import logging
import hashlib
import json
import models

from models.api_requests import API_Requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class BearerRequests(API_Requests):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_bearer_key(self):
        try:
            password = self.get_password(password=self.api_credentials["password"], salt=self.api_credentials["salt"])
            payload = json.dumps({"email": self.api_credentials['email'], "password": password})
            return self.get_bearer_key_by_api(payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)
            return False

    def get_password(self, password:str="", salt:str="")->str:
        try:
            if not password:
                raise Exception('Geen wachtwoord of salt?')

            # Adding salt at the last of the password
            salted_password = password+salt
            # Encoding the password
            hashed_password = hashlib.md5(salted_password.encode())

            return hashed_password.hexdigest()
        except Exception as e:
            log.critical(e, exc_info=True)
            return ""


    def get_bearer_key_by_api(self, payload:str):
        try:
            if(mjson := self.api_request(endpoint="/energy/api/v1.0/login", payload=payload, post_get="POST")):
                return mjson['access_token']
            return None
        except Exception as e:
            log.critical(e, exc_info=True)