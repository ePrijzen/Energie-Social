import os
import random
import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class HashTags:
    def __init__(self) -> None:
        pass

    def get_hash_tags(self, hashtags: list = [], general_hashtags: list = [], must_hashtags: list = []) -> str:
        try:
            selected_tags = []

            if general_hashtags:
                selected_tags += self.select_hashtags(tags=general_hashtags, aantal=1)
            if must_hashtags:
                selected_tags += self.select_hashtags(tags=must_hashtags, aantal=1)
            if hashtags:
                selected_tags += self.select_hashtags(tags=hashtags, aantal=1)

            return self.create_hashtag_string(tags=selected_tags)

        except Exception as e:
            log.error(e, exc_info=True)
            return ""

    # def get_hash_tags(self, hashtags:list=[], general_hashtags:list=[], must_hashtags:list=[])->str:
    #     try:
    #         selected_tags = []
    #         if not general_hashtags:
    #             selected_tags += self.select_hashtags(tags=general_hashtags,aantal=1)
    #         if not must_hashtags:
    #             selected_tags += self.select_hashtags(tags=must_hashtags,aantal=1)
    #         if not hashtags:
    #             selected_tags += self.select_hashtags(tags=hashtags,aantal=1)

    #         return self.create_hastag_string(tags=selected_tags)
    #     except Exception as e:
    #         log.error(e, exc_info=True)
    #         return ""

    @staticmethod
    def select_hashtags(tags:list=[], aantal:int=2)->list:
        return random.sample(tags, k=aantal)

    @staticmethod
    def create_hashtag_string(tags:list=[])->str:
        tag_string = ""
        random.shuffle(tags)
        for t in tags:
            tag_string += f"#{t} "
        return f"\n\n{tag_string}"



