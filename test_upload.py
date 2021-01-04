from dotenv import load_dotenv
import os
load_dotenv()
import json
from uploader import create_listing
load_dotenv()
def etsy_instance():
    from requests_oauthlib import OAuth1Session
    CLIENT_KEY = os.getenv('CLIENT_KEY')
    CLIENT_SECRET = os.getenv('CLIENT_SECRET')
    RESOURCE_OWNER_KEY = os.getenv('RESOURCE_OWNER_KEY')
    RESOURCE_OWNER_SECRET = os.getenv('RESOURCE_OWNER_SECRET')
    return OAuth1Session(CLIENT_KEY,
                         client_secret=CLIENT_SECRET,
                         resource_owner_key=RESOURCE_OWNER_KEY,
                         resource_owner_secret=RESOURCE_OWNER_SECRET)
with open('posters/pulp-fiction-0110912/data/097946569.json') as f:
    full_data = json.load(f)
    e=etsy_instance()
    create_listing(e, full_data)