import os
import tweepy
import logging

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Tweets:
    def __init__(self) -> None:
        pass

    def __tweet_connect(self, tokens:dict={}, social_name:str="")->bool:
        try:
            self.__client =  tweepy.Client(bearer_token=tokens['bearer_token'],
                                           consumer_key=tokens['api_key'],
                                           consumer_secret=tokens['api_key_secret'],
                                           access_token=tokens['access_token'],
                                           access_token_secret=tokens['access_token_secret']
                                            )
            # authorization of consumer key and consumer secret
            auth = tweepy.OAuthHandler(tokens['api_key'], tokens['api_key_secret'])

            # set access to user's access key and access secret
            auth.set_access_token(tokens['access_token'], tokens['access_token_secret'])

            # calling the api
            self.__api = tweepy.API(auth)

            return True
        except Exception as e:
            log.critical(f"Error creating {social_name} connection: {e}")
            return False

    def tweettie(self, msg:str ="", tokens:dict={}, images:list=[], social_name:str="")->bool:
        try:
            if not msg:
                return False

            if not self.__tweet_connect(tokens=tokens):
                return False

            # check if image exists
            media = []
            # check if image exists
            if isinstance(images, str):
                if images is not None and os.path.exists(images):
                    if(media_id := self.__api.media_upload(images)):
                        media.append(media_id.media_id_string)
                else:
                    log.error(f"Image does not exists : {images}")
            elif isinstance(images, list):
                for image in images:
                    if image is not None and os.path.exists(image):
                        if(media_id := self.__api.media_upload(image)):
                            media.append(media_id.media_id_string)
                    else:
                        log.error(f"Image does not exists : {image}")
            else:
                pass #no images

            if len(media) > 0:
                response = self.__client.create_tweet(text=msg, user_auth=True, media_ids=media)
                log.error(response)
                return True

            response = self.__client.create_tweet(text=msg, user_auth=True)

            try:
                tweet = response.data # type: ignore
                tweet['id']
                return True
            except Exception:
                return False
        except Exception as e:
            log.critical(f"Error creating Message on {social_name} : {e}", exc_info=True)
            return False
