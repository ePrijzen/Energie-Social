# Get longlive token for facebook and Instagram
# https://levelup.gitconnected.com/automating-instagram-posts-with-python-and-instagram-graph-api-374f084b9f2b
# https://medium.com/nerd-for-tech/automate-facebook-posts-with-python-and-facebook-graph-api-858a03d2b142

# go to https://developers.facebook.com/tools/explorer/ and get a short live token



import sys
import os
import toml
import requests
import webbrowser

from src.helpers.config import Config


DIR_PATH = os.path.dirname(os.path.realpath(__file__))

config_folder =  os.path.join(DIR_PATH, "config")

if (config_file := Config().check_config(config_filename="development.toml", config_folder=config_folder)):
    config = toml.load(config_file)
else:
    sys.exit()

url = "https://developers.facebook.com/tools/explorer/"
safari = webbrowser.get('safari')
safari.open(url, new=2)

fb_exchange_token = input('Give me the FaceBook exchange token (enter voor overslaan): ')

if fb_exchange_token != "":
    client_id = config['facebook']['eprijzen']['app_id']

    client_id = config['facebook']['eprijzen']['app_id']
    client_secret = config['facebook']['eprijzen']['app_secret']
    fb_url = f"https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={client_id}&client_secret={client_secret}&fb_exchange_token={fb_exchange_token}"
    print(fb_url)
    r = requests.get(fb_url)
    fb_data = r.json()
    access_token = fb_data['access_token']

    page_id = config['facebook']['eprijzen']['page_id']
    fb_url = f"https://graph.facebook.com/{page_id}?fields=access_token&access_token={access_token}"
    r = requests.get(fb_url)
    fb_data = r.json()
    access_token = fb_data['access_token']
    print(f"FaceBook Token: {access_token}")

insta_exchange_token = input('Give me the InstaGram exchange token: ')
if insta_exchange_token != "":
    client_id = config['instagram']['eprijzen']['app_id']
    client_secret = config['instagram']['eprijzen']['app_secret']
    fb_page_id = config['instagram']['eprijzen']['fb_page_id']
    fb_url = f"https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={client_id}&client_secret={client_secret}&fb_exchange_token={insta_exchange_token}"
    r = requests.get(fb_url)
    insta_data = r.json()
    access_token = insta_data['access_token']
    print(f"InstaGram LongLive Token {access_token}")
    fb_url = f"https://graph.facebook.com/v10.0/{fb_page_id}?fields=instagram_business_account&access_token={access_token}"
    r = requests.get(fb_url)
    insta_data = r.json()
    print(f"InstaGram ID: {insta_data['instagram_business_account']['id']}")

