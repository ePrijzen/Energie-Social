import os
import praw
import logging

from helpers.dates_times import DatesTimes

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class RedditPraw:
    def __init__(self) -> None:
        pass

    @staticmethod
    def double_enter(msg:str=""):
        if not msg:
            return msg
        msg = msg.replace('\n', '\n\n')
        return msg.replace('\r', '\r\n')

    def reddit_message(self, title:str="", msg:str="", creds:dict={}, images:list=[], social_name:str="")->bool:
        try:
            if not title:
                raise Exception('There is no title!')

            if not (reddit := praw.Reddit(client_id=creds['client_id'],
                     client_secret=creds['client_secret'],
                     user_agent=creds['user_agent'],
                     redirect_uri=creds['redirect_uri'],
                     refresh_token=creds['refresh_token'])):
                raise Exception(f"Reddit connection problem {reddit}")

            if not (subreddit := reddit.subreddit(creds['subr'])):
                raise Exception(f"Reddit connection problem {reddit}")

            image_url = ""

            # check if image exists
            if isinstance(images, str):
                file_name = os.path.basename(images)
                image_url = f"https://images.eprijzen.nl/{file_name}?{DatesTimes.unixtimestamp()}"
            elif isinstance(images, list):
                for image in images:
                    file_name = os.path.basename(image)
                    image_url = f"https://images.eprijzen.nl/{file_name}?{DatesTimes.unixtimestamp()}"
                    break
            else:
                pass #no images

            r = None

            if image_url and not msg:
                r = subreddit.submit(title, url=image_url)
            elif not image_url and msg:
                msg = self.double_enter(msg=msg)
                r = subreddit.submit(title, selftext=msg)
            elif image_url and msg:
                msg = self.double_enter(msg=msg)
                msg = msg + "\n\n"+image_url
                r = subreddit.submit(title, selftext=msg)

                # msg = self.double_enter(msg=msg)
                # r = subreddit.submit(title, url=image_url)

                # msg = self.double_enter(msg=msg)
                # r = subreddit.submit(title, selftext=msg)

            if not r:
                raise Exception("No message or URL? Error submitting message")
            else:
                return True

        except (Exception, TypeError) as e:
            log.critical(f"Error creating Message on {social_name}, title: {title}, message: {msg}, image:{image_url} images: {images} error: {e}", exc_info=True) # type: ignore
            return False
