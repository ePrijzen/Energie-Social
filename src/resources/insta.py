import os
import requests
import logging

from helpers.dates_times import DatesTimes

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class Insta:
    @staticmethod
    def send_message(page_user_id:int, access_token:str="", msg:str="", images:list=[],
                     social_name:str="")->bool:
        try:
            img_url = ""

            if not msg:
                return False
            if not page_user_id:
                return False

            # check if image exists
            if isinstance(images, str):
                file_name = os.path.basename(images)
                img_url = f"https://images.eprijzen.nl/{file_name}"
            elif isinstance(images, list):
                for image in images:
                    file_name = os.path.basename(image)
                    img_url = f"https://images.eprijzen.nl/{file_name}"
            else:
                pass #no images

            if img_url:
                try:
                    post_url = f"https://graph.facebook.com/v10.0/{page_user_id}/media"
                    payload = {}
                    payload['image_url'] = img_url
                    payload['caption'] = msg
                    payload['access_token'] = access_token

                    r = requests.post(post_url, data=payload)
                    result = r.json()
                except Exception as e:
                    log.critical(f"Error creating instagram photo on {social_name} : {img_url} {e}", exc_info=True)
                    return False

                if 'id' in result:
                    creation_id = result['id']

                    second_url = f"https://graph.facebook.com/v10.0/{page_user_id}/media_publish"
                    second_payload = {}
                    second_payload['creation_id'] = creation_id,
                    second_payload['access_token'] = access_token
                    r = requests.post(second_url, data=second_payload)
                    if r.status_code == 200 or r.status_code == 201:
                        return True
                else:
                    raise Exception(f"Instagram post problem - {result}")

            return False

        except Exception as e:
            log.critical(f"Error creating Message on {social_name} : {e} {images}", exc_info=True)
            return False
