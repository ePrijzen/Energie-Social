import os
import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class PriceHelpers():

    @staticmethod
    def avg_data(data:dict={}, countries:dict={})->dict:
        try:
            if not data or not countries:
                raise Exception("geen data of landen")

            new_data_set = {}

            for d in data:
                country = countries[d['country']]
                new_data_set[country] = d['price']
                pass

            return new_data_set
        except (Exception, KeyError) as e:
            log.warning(e, exc_info=True)
            return {}

    @staticmethod
    def dutch_floats(price, f:str=':.3f')->str:
        if not price or price == "":
            return ""

        return ('€ {'+f+'}').format(price).replace('.',',')

    @staticmethod
    def prijs_instelling_tekst(kind="k")->str:
        match kind:
            case 'k':
                return "Inkoop"
            case 'o':
                return "Inkoop+opslag+BTW "
            case 'a':
                return "All-In "
            case _:
                return "Inkoop"

    @staticmethod
    def prijs_kind(kind="k")->str:
        match kind:
            case 'k':
                return"price"
            case 'o':
                return"opslag_price"
            case 'a':
                return"all_in_price"
            case _:
                return"price"

    def get_prices(self, prices:dict={})->dict:
        try:
            if not prices:
                return {}

            gas_price = None
            el_price = None
            gas_price_inkoop = None
            el_price_inkoop = None

            for p in prices['data']:
                if p['kind'] == 'g':
                    try:
                        gas_price = p['all_in_price']
                        gas_price_inkoop = p['price']
                    except Exception:
                        gas_price = None
                        gas_price_inkoop = None

                if p['kind'] == 'e':
                    try:
                        el_price = p['all_in_price']
                        el_price_inkoop = p['price']
                    except Exception:
                        el_price = None
                        el_price_inkoop = None

            return {'el_price_dutch' : self.dutch_floats(el_price),
                    'gas_price_dutch' : self.dutch_floats(gas_price),
                    'gas_inkoop_price_dutch' : self.dutch_floats(gas_price_inkoop),
                    'el_inkoop_price_dutch' : self.dutch_floats(el_price_inkoop),
                    'el_price': el_price,
                    'el_price_inkoop': el_price_inkoop
                    }

        except Exception as e:
            log.error(e, exc_info=True)
            return {}