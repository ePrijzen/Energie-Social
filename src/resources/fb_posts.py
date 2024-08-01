import os
import logging
import requests

PY_ENV = os.getenv('PY_ENV', 'dev')
log = logging.getLogger(PY_ENV)

class FbPosts:
    def __init__(self) -> None:
        pass

    @staticmethod
    def postImage(page_id:int, image:str, access_token:str, social_name:str=""):
        try:
            url = f"https://graph.facebook.com/{page_id}/photos?access_token=" + access_token

            files = {
                    'file': open(image, 'rb'),
                    }
            data = {
                "published" : False
            }
            r = requests.post(url, files=files, data=data).json()
            return r

        except Exception as e:
            log.critical(f"Error creating {social_name} image: {e}")
            return False

    def send_image(self, image:str="", page_id:int=int(), access_token:str="", social_name:str="")->str:
        try:
            if image is not None and os.path.exists(image):
                if(img_id := self.postImage(page_id=page_id, image=image, access_token=access_token, social_name=social_name)):
                    return img_id
            else:
                raise Exception(f"Image does not exists : {image}")

            return ""
        except Exception as e:
            log.critical(f"Error adding Image on {social_name} : {e}", exc_info=True)
            return ""

    def send_message(self, msg:str="", access_token:str="", page_id:int=int(), images:list=[], social_name:str="")->bool:
        try:
            if not page_id or page_id == 0:
                return False
            if not msg:
                return False

            post_url = f"https://graph.facebook.com/{page_id}/feed"

            imgs_id = []
            if isinstance(images, str):
                img_id = self.send_image(image=images, access_token=access_token, page_id=page_id, social_name=social_name)
                imgs_id.append(img_id)
            elif isinstance(images, list):
                for image in images:
                    img_id = self.send_image(image=image, access_token=access_token, page_id=page_id, social_name=social_name)
                    imgs_id.append(img_id)
            else:
                pass #no images

            payload=dict()
            payload["message"]=msg
            payload["access_token"]=access_token

            if len(imgs_id) > 0:
                for img_id in imgs_id:
                    key=f"attached_media[{imgs_id.index(img_id)}]"
                    payload[key]=f"{{'media_fbid': '{img_id['id']}'}}"

            r = requests.post(post_url, data=payload)
            if r.status_code == 200 or r.status_code == 201:
                return True

            return False

        except Exception as e:
            log.critical(f"Error creating Message on {social_name} : {e}", exc_info=True)
            return False