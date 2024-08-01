import os
import logging
import json

from models.api_requests import API_Requests
from helpers.dates_times import DatesTimes

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class EnergieVolumeRequests(API_Requests):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def day_volume(self, vandaag:str="")->dict:
        try:
            if not vandaag:
                vandaag = DatesTimes.vandaag()
            payload = json.dumps({"datum": vandaag})
            return self.api_request(endpoint="/energy/api/v1.0/volume", payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}

    def month_volume(self, jaar_maand:str="")->dict:
        try:
            if not jaar_maand:
                jaar_maand = DatesTimes.jaarmaand()
            payload = json.dumps({"jaar_maand": jaar_maand})
            return self.api_request(endpoint="/energy/api/v1.0/volume", payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}

    def current_volume(self, vandaag:str="")->dict:
        try:
            if not vandaag:
                vandaag = DatesTimes.vandaag()
            payload = json.dumps({"huidig": vandaag})
            return self.api_request(endpoint="/energy/api/v1.0/volume", payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}