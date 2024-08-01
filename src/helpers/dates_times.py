
import os
import logging
from datetime import datetime, timedelta
from time import time

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class DatesTimes:
    def __init__(self) -> None:
        self.weekdays = ['Maandag', 'Dinsdag', 'Woensdag', 'Donderdag', 'Vrijdag', 'Zaterdag', 'Zondag']
        self.months = ['', 'Jan', 'Feb', 'Mrt', 'Apr', 'Mei', 'Juni', 'Juli', 'Aug', 'Sept', 'Okt', 'Nog', 'Dec']

        self.morgen_tijden = list(['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00'])
        self.middag_tijden = list(['12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00', '22:00', '23:00'])

    @staticmethod
    def vandaag()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%Y-%m-%d")

    @staticmethod
    def morgen()->str:
        vandaag_ts = datetime.now()
        morgen_ts = vandaag_ts + timedelta(days=+1)
        return morgen_ts.strftime("%Y-%m-%d")

    @staticmethod
    def vandaag_dir()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%Y%m%d")

    @staticmethod
    def maand()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%m")

    @staticmethod
    def jaarmaand()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%Y-%m")

    def maand_naam(self, maand:int)->str:
        if not maand:
            maand = int(self.maand())
        return self.months[maand]

    def leesbare_vandaag(self) -> str:
        vandaag_ts = datetime.now()
        day = vandaag_ts.day
        month_name = self.months[vandaag_ts.month]
        return f"{day} {month_name}"
    # def leesbare_vandaag()->str:
    #     vandaag_ts = datetime.now()
    #     return vandaag_ts.strftime("%d %B")

    @staticmethod
    def jaar()->str:
        vandaag_ts = datetime.now()
        return vandaag_ts.strftime("%Y")

    @staticmethod
    def dag()->int:
        vandaag_ts = datetime.now()
        return int(vandaag_ts.strftime("%d"))

    @staticmethod
    def tijd(hour: int = None) -> str: # type: ignore
        if hour is None:
            time_ts = datetime.now()
        elif 0 <= hour < 24:
            time_ts = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
        else:
            raise ValueError('Hour must be between 0 and 23.')
        return time_ts.strftime("%H:00")

    @staticmethod
    def unixtimestamp()->int:
        return int( time() )

    @staticmethod
    def korte_tijd(curr_time: str = "") -> int:
        if curr_time:
            hour = int(curr_time.split(':')[0])
        else:
            hour = datetime.now().hour
        return hour
    # def korte_tijd(curr_time:str="")->int:
    #     # curr_time = "14:00"
    #     if not curr_time:
    #         curr_time_ts = datetime.now()

    #     return int(curr_time_ts.strftime("%H"))

    @staticmethod
    def kort_dag()->int:
        vandaag_ts = datetime.now()
        return int(vandaag_ts.strftime("%d"))

    @staticmethod
    def day_part(start: int, hours: int) -> list:
        if not 0 <= start < 24:
            raise ValueError("Start hour must be between 0 and 23.")

        stop = (start + hours) % 24
        hours_range = list(range(start, stop if stop > start else stop + 24))
        formatted_hours = [f"{hour % 24:02d}:00" for hour in hours_range]

        mid = len(formatted_hours) // 2
        return [formatted_hours[:mid], formatted_hours[mid:]]

    # def day_part(start:int, hours:int)->list:
    #     try:
    #         stop = start+hours
    #         if ((stop-start) % 2) != 0:
    #             stop += 1
    #         if (stop > 24):
    #             start -= 1
    #             stop = 24

    #         part = []
    #         chunked_list = list()
    #         for i in range(start, stop):
    #             if i is not None:
    #                 if i == 24:
    #                     i = 0
    #                 part.append(f"{i:02d}:00")

    #         chunk_size = int(len(part)/2)
    #         for i in range(0, len(part), chunk_size):
    #             chunked_list.append(part [i:i+chunk_size])
    #         return chunked_list
    #     except Exception as e:
    #         log.error(e, exc_info=True)
    #         return []

    @staticmethod
    def next_hour(hour: int = None) -> str: # type: ignore
        if hour is None or not isinstance(hour, int) or not 0 <= hour < 24:
            raise ValueError('Invalid hour provided')

        next_hour = (hour + 1) % 24
        return f"{next_hour:02d}:00"
    # def next_hour(hour: str = "") -> str: # type: ignore
    #     if not hour or len(hour) < 2 or not hour[:2].isdigit() or not 0 <= int(hour[:2]) < 24:
    #         raise ValueError('Invalid hour provided')

    #     next_hour = (int(hour[:2]) + 1) % 24
    #     return f"{next_hour:02d}:00"


    # def next_hour(hour:str="")->str:
    #     try:
    #         if not hour:
    #             raise Exception('Geen uur mee gegeven')
    #         next_hour = int(hour[:2]) + 1
    #         return f"{next_hour:02d}:00"
    #     except Exception as e:
    #         log.error(e, exc_info=True)
    #         return ""


    def get_nice_day(self, date: str = "", weekday: bool = False) -> str:
        try:
            dt = datetime.strptime(date or datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d") + timedelta(hours=1, minutes=1, seconds=1)

            day, year = dt.day, dt.year
            weekday_name, month_name = self.weekdays[dt.weekday()], self.months[dt.month]

            return f"{weekday_name} {day} {month_name} {year}" if weekday else f"{day} {month_name} {year}"

        except Exception as e:
            log.error(e, exc_info=True)
            return ""

    # def get_nice_day(self, date:str="", weekday:bool=False)->str:
    #     try:
    #         if date is None:
    #             vandaag_ts = datetime.now()
    #             date = vandaag_ts.strftime("%Y-%m-%d")

    #         new_date = f"{date} 01:01:01"
    #         dt = datetime.strptime(new_date, "%Y-%m-%d %H:%M:%S")

    #         day = dt.strftime("%d")
    #         year = dt.strftime("%Y")
    #         weekday = self.weekdays[dt.weekday()] # type: ignore
    #         month_int = int(dt.strftime("%m"))
    #         month = self.months[month_int]

    #         if weekday:
    #             return f"{weekday} {day} {month} {year}"
    #         else:
    #             return f"{day} {month} {year}"

    #     except Exception as e:
    #         log.error(e, exc_info=True)
    #         return ""