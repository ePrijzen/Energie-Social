import os
import logging
import models

from models.api_requests import API_Requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class CountryRequests(API_Requests):
    def __init__(self,*args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def get_countries(self)->dict:
        try:
            if(country_data := self.api_request(endpoint="/energy/api/v1.0/countries", payload="")):
                countries = {}
                for country in country_data['data']:
                    countries[country['country_id']] = country['country']
                return countries

            return {}
        except Exception as e:
            log.critical(e, exc_info=True)
            return {}