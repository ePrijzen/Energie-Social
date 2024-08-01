import os
import sys
import logging
import logging.config
import toml

from helpers.folder_setters import FolderSetters
from helpers.price_helpers import PriceHelpers
from helpers.config import Config
from helpers.dates_times import DatesTimes
from helpers.hashtags import HashTags

from views.message_texts import MessageTexts

from models.bearerrequests import BearerRequests
from models.countryrequests import CountryRequests
from models.energierequests import EnergieRequests
from models.energievolumerequests import EnergieVolumeRequests

from resources.tweets import Tweets
from resources.tootsy import Tootsy
from resources.fb_posts import FbPosts
from resources.insta import Insta
from resources.reddit_praw import RedditPraw

from apscheduler.schedulers.blocking import BlockingScheduler

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
PY_ENV = os.getenv('PY_ENV', 'dev')

if(FS := FolderSetters.setFolders(dir_path=DIR_PATH, py_env=PY_ENV)):
    logging.config.fileConfig(os.path.join(FS['config_folder'], 'logging.conf'))
    log = logging.getLogger(PY_ENV)
    logger = logging.getLogger()
    match PY_ENV:
        case 'dev':
            logger.setLevel(logging.INFO)
        case 'prod':
            logger.setLevel(logging.ERROR)
        case _:
            pass
    GRAPHS_FOLDER = FS['graphs_folder']
else:
    sys.exit()

if (config_file := Config().check_config(config_filename=FS['config_filename'], config_folder=FS['config_folder'])):
    config = toml.load(config_file)
else:
    sys.exit()

class Messages():
    def __init__(self) -> None:
        pass

    @staticmethod
    def message_graph_back(hourly_message:str, long_message:str, day_part_message:str,
                           price_below_zero:bool, morning_message:str, country_message:str,
                           volume_message:str, price_kind:str, graphs:dict, hour:int, account_config:dict)->dict:
        message_graphs = []
        msg = ""
        title = ""

        if account_config['price_below_zero_message'] and price_below_zero:
            title = f"Energieprijs onder nul om {hour}:00!"
            msg = hourly_message
        elif account_config['day_part_message_time'] and hour in account_config['day_part_message_time'] and day_part_message:
            title = f"Energie prijzen {DatesTimes().get_nice_day(date='', weekday=True)}"
            msg = day_part_message
        elif account_config['morning_message_time'] == hour and morning_message:
            title = f"Energieprijzen in het kort {DatesTimes().get_nice_day(date='', weekday=True)}"
            if volume_message is not None:
                msg = morning_message+volume_message
            else:
                msg = morning_message
            try:
                message_graphs = graphs['morning']
            except(Exception,KeyError):
                pass
        elif account_config['long_message_time'] == hour and long_message:
            if hour <= 12:
                title = f"Energieprijzen voor {DatesTimes().get_nice_day(date=DatesTimes.vandaag(), weekday=True)}"
            else:
                title = f"Energieprijzen voor {DatesTimes().get_nice_day(date=DatesTimes.morgen(), weekday=True)}"

            msg = long_message
            try:
                message_graphs = graphs['tomorrow']
            except(Exception,KeyError):
                pass
        elif account_config['country_message_time'] == hour and country_message:
            title = "Stroomprijzen in Europa"
            msg = country_message
            try:
                message_graphs = graphs['country']
            except(Exception,KeyError):
                pass
        elif account_config['windsolar_message_time'] == hour:
            title = msg = "Zon en Wind energie opbrengst voor morgen!"
            try:
                message_graphs = graphs['wind_solar']
            except(Exception,KeyError):
                pass
        elif account_config['hourly_message'] and hourly_message:
            title = f"Energie prijs vanaf {hour}:00"
            msg = hourly_message
        else:
            return {'msg':'', 'graphs':'', 'title': ''}

        return {'msg':msg, 'graphs':message_graphs, 'title': title}

    def send(self, hourly_message:str, long_message:str, day_part_message:str,
             price_below_zero:bool, morning_message:str, country_message:str,
             volume_message:str, price_kind:str, graphs:dict, hour:int)->None:
        try:
            general_hashtags = list(config['hashtags']['general'])
            must_hashtags = list(config['hashtags']['must'])

            for social_platform, social_configs in config['socials'].items():
                for social_account, account_config in social_configs.items():
                    try:
                        if not account_config['activated']:
                            continue

                        if not account_config['price_kind'] or account_config['price_kind'] != price_kind: #['k', 'a']
                            continue

                        try:
                            social_graphs = graphs[price_kind]
                        except (Exception, KeyError):
                            social_graphs = {}

                        msg_graph = self.message_graph_back(hourly_message=hourly_message, long_message=long_message, day_part_message=day_part_message,
                                                            price_below_zero=price_below_zero, morning_message=morning_message, country_message=country_message,
                                                            volume_message=volume_message, price_kind=price_kind, graphs=social_graphs, hour=hour, account_config=account_config)
                        msg = msg_graph['msg']
                        use_graphs = msg_graph['graphs']
                        title = msg_graph['title']

                        if not msg and not title:
                            continue

                        social_name = f"{social_platform}-{social_account}"

                        match social_platform:
                            case "twitter":
                                msg = msg + HashTags().get_hash_tags(hashtags=account_config['hashtags'], general_hashtags=general_hashtags, must_hashtags=must_hashtags)
                                if PY_ENV == "prod":
                                    Tweets().tweettie(msg=msg, tokens=account_config['tokens'], images=use_graphs, social_name=social_name)
                                else:
                                    print(f"{social_platform} / {social_account}", f"\nmessage: {msg}", f"\nimages: {use_graphs}")
                                break
                            case "reddit":
                                if title:
                                    if PY_ENV == "prod":
                                        RedditPraw().reddit_message(title=title, msg=msg, creds=account_config, images=use_graphs, social_name=social_name)
                                    else:
                                        print(f"{social_platform} / {social_account}", f"\ntitle: {title}",f"\nmessage: {msg}", f"\nimages: {use_graphs}")
                                break
                            case "facebook":
                                msg = msg + HashTags().get_hash_tags(general_hashtags=general_hashtags, must_hashtags=must_hashtags)
                                if PY_ENV == "prod":
                                    FbPosts().send_message(msg=msg, access_token=account_config['token'], page_id=account_config['page_id'], images=use_graphs, social_name=social_name)
                                else:
                                    print(f"{social_platform} / {social_account}", f"\nmessage: {msg}", f"\nimages: {use_graphs}")
                                break
                            case "mastodon":
                                msg = msg + HashTags().get_hash_tags(general_hashtags=general_hashtags, must_hashtags=must_hashtags)
                                if PY_ENV == "prod":
                                    r =  Tootsy().tootsie(msg=msg, access_token=account_config['key'], images=use_graphs, social_name=social_name)
                                else:
                                    print(f"{social_platform} / {social_account}", f"\nmessage: {msg}", f"\nimages: {use_graphs}")
                                break
                            case "instagram":
                                msg = msg + HashTags().get_hash_tags(general_hashtags=general_hashtags, must_hashtags=must_hashtags)
                                if PY_ENV == "prod":
                                    Insta.send_message(page_user_id=account_config['page_user_id'], msg=msg, images=use_graphs, access_token=account_config['access_token'], social_name=social_name)
                                else:
                                    print(f"{social_platform} / {social_account}", f"\nmessage: {msg}", f"\nimages: {use_graphs}")
                                break
                            case _:
                                break

                    except (Exception, KeyError) as e:
                        log.critical(e, exc_info=True)

        except (Exception, KeyError) as e:
            log.critical(e, exc_info=True)

def remove_non_existing_images(graphs:dict={})->dict:
    new_dict = {}
    for k, v in graphs.items():
        if isinstance(v, dict):
            new_dict[k] = remove_non_existing_images(graphs=v)
        elif isinstance(v, list):
            new_dict[k] = [i for i in v if not isinstance(i, str) or os.path.isfile(i)]
        else:
            if not isinstance(v, str) or os.path.isfile(v):
                new_dict[k] = v
    return new_dict

def prepare_and_send_messages():
    try:
        if(bearer_key := BearerRequests(api_credentials=config['api']).get_bearer_key()):
            M = Messages()
            kinds = ['k', 'a']
            country = "NL"

            # Tijden
            if PY_ENV != 'prod':
                cur_time = 15
                print("########################################################")
                print("############### DEV het is ", cur_time, " uur  ####################")
                print("########################################################")
            else:
                cur_time = DatesTimes.korte_tijd()

            ER = EnergieRequests(api_credentials=config['api'], bearer_key=bearer_key)
            EV = EnergieVolumeRequests(api_credentials=config['api'], bearer_key=bearer_key)
            today_prices = ER.current_prices(datum=DatesTimes.vandaag(), tijd="", country=country)
            tomorrow_prices = ER.current_prices(datum=DatesTimes.morgen(), tijd="", country=country)
            curr_prices = ER.current_prices(datum=DatesTimes.vandaag(), tijd=DatesTimes.tijd(hour=cur_time), country=country)
            current_prices = PriceHelpers().get_prices(prices=curr_prices)

       # Country Message
            lowest_price = ER.cur_high_low_prices(kind='e', datum=DatesTimes.vandaag(), tijd=DatesTimes.tijd(), lowest=True)
            highest_price = ER.cur_high_low_prices(kind='e', datum=DatesTimes.vandaag(), tijd=DatesTimes.tijd(), highest=True)
            countries = CountryRequests(api_credentials=config['api'], bearer_key=bearer_key).get_countries()
            country_message = MessageTexts.country_message(lowest_price=lowest_price, highest_price=highest_price, countries=countries)

        # Todays's min max prices
            min_price_el = {}
            try:
                min_price_el = ER.min_el_price(datum=DatesTimes.vandaag())['data'][0]
                if min_price_el is None:
                    raise Exception("Geen min prijs? ")
            except Exception as e:
                log.warning(f"{e}, {min_price_el}", exc_info=True)

            max_price_el = {}
            try:
                max_price_el = ER.max_el_price(datum=DatesTimes.vandaag())['data'][0]
                if max_price_el is None:
                    raise Exception("Geen max prijs? ")
            except Exception as e:
                log.warning(f"{e}, {max_price_el}", exc_info=True)

        # volume Message
            volume_message = ""
            month_volume = None
            if DatesTimes.jaar() == 2023:
                day_volume = EV.day_volume(vandaag=DatesTimes.vandaag())
                month_volume = EV.month_volume(jaar_maand=DatesTimes.jaarmaand())
                current_volume = EV.current_volume(vandaag=DatesTimes.vandaag())
                volume_message = MessageTexts.volume_message(day=day_volume, month=month_volume, huidig=current_volume)

            graphs = {'a': {}, 'k':{}}

            graphs['a']['morning'] = []
            graphs['a']['morning'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "electra_daily_all_in_stacked_barchart_2.png"))
            graphs['a']['morning'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "gas_daily_all_in_stacked_barchart.png"))

            graphs['a']['wind_solar'] = os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "wind_and_solar_forecast_morgen.png")
            graphs['a']['tomorrow'] = os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "tomorrow_electra_daily_all_in_stacked_barchart.png")
            graphs['a']['country'] = os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "electra_avg_day_price_countries_barchart.png")

            graphs['k']['morning'] = []
            graphs['k']['morning'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "electra_inkoop_daily_barchart.png"))
            graphs['k']['morning'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "gas_7_days_inkoop_barchart.png"))
            graphs['k']['tomorrow'] = os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "tomorrow_electra_daily_all_in_stacked_barchart.png")
            graphs['k']['country'] = os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "electra_avg_day_price_countries_barchart.png")

            graphs['a']['insta'] = {}
            graphs['a']['insta']['country'] = os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "electra_avg_day_price_countries_barchart_square.jpg")
            graphs['a']['insta']['wind_solar'] = os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "wind_and_solar_forecast_morgen_square.jpg")
            graphs['a']['insta']['tomorrow'] = os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "tomorrow_electra_daily_all_in_stacked_barchart_square.jpg")

            graphs['a']['insta']['morning'] = []
            graphs['a']['insta']['morning'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "electra_daily_all_in_stacked_barchart_2_square.jpg"))
            graphs['a']['insta']['morning'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "gas_daily_all_in_stacked_barchart_square.jpg"))

            graphs['a']['day_part'] = []
            graphs['a']['day_part'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "electra_30_days_all_in_stacked_barchart.png"))
            graphs['a']['day_part'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "gas_30_days_all_in_stacked_barchart.png"))

            graphs['k']['day_part'] = []
            graphs['k']['day_part'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "electra_inkoop_daily_barchart.png"))
            graphs['k']['day_part'].append(os.path.join(GRAPHS_FOLDER, DatesTimes.vandaag_dir(), "gas_7_days_inkoop_barchart.png"))

            graphs = remove_non_existing_images(graphs=graphs)

            for kind in kinds:
                price_below_zero = False
                hourly_message = ""
                day_part_message = ""
                morning_message = ""
                price_below_zero = False
                day_part_tijden = []
                long_msg = ""

                if kind == 'k' and current_prices['el_price_inkoop'] < 0:
                    price_below_zero = True

                if kind == 'a' and current_prices['el_price'] < 0:
                    price_below_zero = True

                hourly_message = MessageTexts.hourly_mesage(prices=current_prices, kind=kind, hour=cur_time)

                morning_message = MessageTexts.daily_message(min_price_el=min_price_el, max_price_el=max_price_el, gas_prices=current_prices, kind=kind)

                if cur_time < 15:
                    day_part_tijden = DatesTimes.day_part(start=7, hours=9)
                elif 22 > cur_time >= 15 :
                    day_part_tijden = DatesTimes.day_part(start=15, hours=9)
                elif cur_time >= 22:
                    day_part_tijden = DatesTimes.day_part(start=0, hours=9)

                all_day_tijden =  DatesTimes.day_part(start=0, hours=23)

                # short messages
                if cur_time < 22: # todays prices
                    day_part_message = MessageTexts.long_message(data=today_prices, date=DatesTimes.vandaag(), kind=kind, tijden=day_part_tijden)
                elif cur_time >= 22: # tomorrow prices
                    day_part_message = MessageTexts.long_message(data=tomorrow_prices, date=DatesTimes.morgen(), kind=kind, tijden=day_part_tijden)

                # long messages
                if cur_time < 15: # todays prices
                    long_msg = MessageTexts.long_message(data=today_prices, date=DatesTimes.vandaag(), kind=kind, tijden=all_day_tijden)
                if cur_time >= 15: # tomorrow prices
                    long_msg = MessageTexts.long_message(data=tomorrow_prices, date=DatesTimes.morgen(), kind=kind, tijden=all_day_tijden)

                M.send(
                    hourly_message = hourly_message,
                    long_message = long_msg,
                    day_part_message = day_part_message,
                    price_below_zero = price_below_zero,
                    morning_message = morning_message,
                    country_message = country_message,
                    volume_message = volume_message,
                    price_kind=kind,
                    graphs=graphs,
                    hour = cur_time
                )

    except (Exception, KeyError) as e:
        log.critical(e, exc_info=True)

if __name__ == "__main__":
    if PY_ENV != 'prod':
        prepare_and_send_messages()
    else:
        scheduler = BlockingScheduler()
        scheduler.add_job(prepare_and_send_messages, trigger='cron', hour='*', timezone='Europe/Amsterdam')
        scheduler.start()