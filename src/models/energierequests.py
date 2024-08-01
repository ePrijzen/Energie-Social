import os
import logging
import json

from models.api_requests import API_Requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class EnergieRequests(API_Requests):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def cur_high_low_prices(self, datum:str="", tijd:str="", kind:str="e", lowest:bool=False, highest:bool=False ):
        try:
            payload = json.dumps({"fromdate": datum, "fromtime": tijd, "dutch_floats": False, "lowest": lowest, "highest":highest,"kind":kind})
            return self.api_request(endpoint="/energy/api/v1.0/prices", payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}

    def avg_prices(self, datum:str="", tijd:str="", kind:str="e"):
        try:
            payload = json.dumps({"fromdate": datum, "fromtime": tijd, "dutch_floats": False, "average": True, "kind": kind})
            return self.api_request(endpoint="/energy/api/v1.0/prices", payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}

    def current_prices(self, datum:str="", tijd:str=None, country:str="NL"): # type: ignore
        try:

            payload = json.dumps({"fromdate": datum, "fromtime": tijd, "dutch_floats": False, "country": country})
            return self.api_request(endpoint="/energy/api/v1.0/prices", payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}

    def min_el_price(self, datum:str=""):
        try:
            payload = json.dumps({"fromdate": datum, "dutch_floats": True, "lowest": True, "kind":"e", "country": "NL"})
            return self.api_request(endpoint="/energy/api/v1.0/prices", payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}

    def max_el_price(self, datum:str=""):
        try:
            payload = json.dumps({"fromdate": datum, "dutch_floats": True, "highest": True, "kind":"e", "country": "NL"})
            return self.api_request(endpoint="/energy/api/v1.0/prices", payload=payload)
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}
