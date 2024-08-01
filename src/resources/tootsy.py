import os
from mastodon import Mastodon
import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Tootsy:
    def __init__(self) -> None:
        pass

    def __tootsy_connect(self, access_token:str="", social_name:str=""):
        try:
            return Mastodon(
                access_token = access_token,
                api_base_url = 'https://botsin.space/'
            )
        except Exception as e:
            log.critical(f"Error creating {social_name} connection: {e}")
            return False

    def tootsie(self, msg:str="", access_token:str="", images:list=[], social_name:str="")->bool:
        try:
            if not msg:
                return False

            if not (mastodon := self.__tootsy_connect(access_token=access_token, social_name=social_name)):
                return False

            media = []
            # check if image exists
            if isinstance(images, str):
                try:
                    if images is not None and os.path.exists(images):
                        if(media_id := mastodon.media_post(images)):
                            media.append(media_id)
                except Exception as e:
                    log.error(f"Image upload problem on {social_name} : {images} {e}")
            elif isinstance(images, list):
                try:
                    for image in images:
                        if image is not None and os.path.exists(image):
                            if(media_id := mastodon.media_post(image)):
                                media.append(media_id)
                except Exception as e:
                    log.error(f"Image upload problem on {social_name} : {images} {e}")
            else:
                log.error(f"Image does not exists {social_name}: {images}")

            if len(media) > 0:
                return mastodon.status_post(msg, media_ids=media)

            return mastodon.status_post(msg)
        except Exception as e:
            log.critical(f"Error creating Message on {social_name} : {e} {images}", exc_info=True)
            return False