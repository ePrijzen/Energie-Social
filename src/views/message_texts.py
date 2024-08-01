import os
import logging

from helpers.price_helpers import PriceHelpers
from helpers.dates_times import DatesTimes

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class MessageTexts:

    @staticmethod
    def hourly_mesage(prices:dict, hour:int, kind:str="a")->str:
        try:
            tijd = None
            if not hour:
                tijd = DatesTimes.tijd()
                hour = DatesTimes.korte_tijd()
            else:
                tijd = DatesTimes.tijd(hour=hour)

            msg = f"{PriceHelpers.prijs_instelling_tekst(kind=kind)}prijs van {tijd} tot {DatesTimes.next_hour(hour=hour)} \n"
            match kind:
                case "a":
                    msg += f"""💡 {prices['el_price_dutch']} ({prices['el_inkoop_price_dutch']} inkoop) per kWh
"""
                    msg += f"🔥 {prices['gas_price_dutch']} ({prices['gas_inkoop_price_dutch']} inkoop) per m³"
                    pass
                case "k":
                    msg += f"""💡 {prices['el_inkoop_price_dutch']} per kWh
"""
                    msg += f"🔥 {prices['gas_inkoop_price_dutch']} per m³"
                    pass
                case _:
                    msg = ""

            return msg

        except KeyError:
            # Some prices not here, so return
            return ""
        except Exception as e:
            log.error(e, exc_info=True)
            return ""

    # for morning and afternoon
    @staticmethod
    def long_message(data:dict, date:str, kind:str, tijden:list=[])->str:
        try:
            morgen_tijden = tijden[0]
            middag_tijden = tijden[1]
            if morgen_tijden is None or middag_tijden is None:
                return ""

            md_soort = PriceHelpers.prijs_instelling_tekst(kind=kind)
            nice_day = DatesTimes().get_nice_day(date=date)
            msg_elect = f"""{nice_day}
{md_soort}prijzen 💡
"""
            msg_gas =  f"{md_soort}prijzen 🔥"
            gas_prijs = ""
            elec = ""
            electra = {}

            price_kind = PriceHelpers.prijs_kind(kind=kind)

            try:
                if data['data'] is None: # type: ignore
                    raise Exception
            except Exception as e:
                return "Er ging iets helemaal mis, probeer het later nog een keer"

            for v in data['data']: # type: ignore
                if v['kind'] == 'e':
                    electra[v['fromtime']] = PriceHelpers.dutch_floats(v[price_kind])
                if v['kind'] == 'g':
                    if int(v['fromtime'][:-3]) <= 5:
                        # gas_voor tot 06:00
                        gas_prijs = f"{PriceHelpers.dutch_floats(v[price_kind])}"
                    else:
                        # gas_na na 06:00
                        gas_prijs = f"{PriceHelpers.dutch_floats(v[price_kind])}"

            for index, item in enumerate(morgen_tijden):
                try:
                    morgen_tijd = morgen_tijden[index]
                except (Exception, KeyError):
                    morgen_tijd = "nvt"

                try:
                    middag_tijd = middag_tijden[index]
                except (Exception, KeyError):
                    middag_tijd = "nvt"

                try:
                    morgen_electra = electra[morgen_tijden[index]]
                except (Exception, KeyError):
                    morgen_electra = "nvt"

                try:
                    middag_electra = electra[middag_tijden[index]]
                except (Exception, KeyError):
                    middag_electra = "nvt"

                elec += f"""{morgen_tijd} {morgen_electra}  {middag_tijd} {middag_electra}
"""

            return f"""{msg_elect}
{elec}
{msg_gas}
{gas_prijs}"""

        except KeyError as e:
            # Some prices not here, so return
            log.error(e, exc_info=True)
            return ""
        except Exception as e:
            log.error(e, exc_info=True)
            return ""


    @staticmethod
    def daily_message(min_price_el:dict, max_price_el:dict, gas_prices:dict, kind="a")->str:
        try:
            gas_price = 0
            match kind:
                case "k":
                    gas_price = gas_prices['gas_inkoop_price_dutch']
                case "a":
                    gas_price = gas_prices['gas_price_dutch']
                case _:
                    gas_price = f"{gas_prices['gas_price_dutch']} ({gas_prices['gas_inkoop_price_dutch']} inkoop)"

            min_time = DatesTimes.korte_tijd(curr_time=min_price_el['fromtime'])
            max_time = DatesTimes.korte_tijd(curr_time=max_price_el['fromtime'])

            return f"""{PriceHelpers.prijs_instelling_tekst(kind)}prijs {DatesTimes().leesbare_vandaag()}
💡kWh laagste {min_price_el['fromtime']}-{DatesTimes.next_hour(hour=min_time)} {min_price_el[PriceHelpers.prijs_kind(kind)]}
💡kWh hoogste {max_price_el['fromtime']}-{DatesTimes.next_hour(hour=max_time)} {max_price_el[PriceHelpers.prijs_kind(kind)]}
🔥 m³ van 6:00 tot 6:00 {gas_price}
"""
        except (Exception, KeyError) as e:
            log.warning(e, exc_info=True)
            return ""

    @staticmethod
    def country_message(lowest_price:dict, highest_price:dict, countries:dict)->str:
        try:
            lowest_price_text = ""
            highest_price_text= ""
            try:
                for lp in lowest_price['data']:
                    price = PriceHelpers.dutch_floats(lp['price'])
                    country = countries[lp['country']]
                    if price == "":
                        lowest_price_text = """
Sorry geen laagste 💡 prijs op dit moment"""
                    else:
                        lowest_price_text = f"""
Laagste 💡 inkoop, {country} ({price})"""
            except Exception as e:
                lowest_price_text = ""
                log.warning(f"No lowest price? {e}")

            try:
                for lp in highest_price['data']:
                    price = PriceHelpers.dutch_floats(lp['price'])
                    country = countries[lp['country']]
                    if price == "":
                        highest_price_text = """
Sorry geen hoogste 💡 prijs op dit moment"""
                    else:
                        highest_price_text = f"""
Hoogste 💡 inkoop, {country} ({price})"""
            except Exception as e:
                highest_price_text = ""
                log.warning("No lowest price?")

            return f"\n{lowest_price_text} {highest_price_text}"

        except Exception as e:
            log.error(e, exc_info=True)
            return ""

    @staticmethod
    def volume_message(day:dict, month:dict={}, huidig:dict={})->str: # type: ignore
        try:
            msg = ""
            e = 0
            g = 0
            for dv in day['data']:
                e = round(dv['g'])
                g = round(dv['g'])

            msg += f"""Prijsplafond Volume vandaag
💡 {e} kWh
🔥 {g} m³"""

            if month is not None:
                for dv in month['data']:
                    e = round(dv['g'])
                    g = round(dv['g'])
                maand = DatesTimes().maand_naam() # type: ignore
                msg += f"""
Maand volume ({maand})
💡 {e} kWh
🔥 {g} m³"""

            if huidig is not None:
                for dv in huidig['data']:
                    e = round(dv['g'])
                    g = round(dv['g'])
                maand = DatesTimes().maand_naam() # type: ignore
                msg += f"""
Maand volume tot vandaag
💡 {e} kWh
🔥 {g} m³"""

            return msg
        except Exception as e:
            log.error(e, exc_info=True)
            return ""