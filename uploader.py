from PIL import Image, ImageDraw
from image_sources.windows_image import CustomImage, hide_file
import re, requests, json
from dotenv import load_dotenv
import os
load_dotenv()
def create_listing_img(file_path):
    w = 1224
    x_offset = -2
    y_offset = 0
    h = int(17/11 * w)
    img = Image.open(file_path).convert('RGBA').resize((w, h))

    base_img = Image.open('11x17_template.png').convert('RGBA')
    combined = Image.new('RGBA', base_img.size)
    combined.paste(img, (int((base_img.size[0] - w) / 2) + x_offset, int((base_img.size[1] - h) / 2) + y_offset))
    return Image.alpha_composite(combined, base_img)
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


BASE_URL = 'https://openapi.etsy.com/v2'
def create_listing(etsy, d):
    title = f"{d['title']} | {d['director']} | Minimalist {d['tv']} Poster, Vintage Retro Art Print, Printable Poster, Instant Download"
    all_tags = [d['title'], d['director'], d['title'] + ' Download', d['title'] + ' Poster', d['director'] + ' Poster',
        'Digital Download', 'Poster', 'Vintage', 'Wall Art', d['tv'], 'Print', d['title'].split(' ')[0]]
    if len(d['writers']) == 1:
        w_text = d['writers'][0]
    else:
        out = ", ".join(d['writers'][:-1])
        # Add the last element, separated by "and" and a final "."
        w_text = "{} and {}".format(out, d['writers'][-1])
    description = f'''"{d['title']}" {d['tv']} Poster

THIS IS A DIGITAL ITEM! NO PHYSICAL POSTER WILL BE SHIPPED :/

⋯⋯⋯ ITEM DETAILS ⋯⋯⋯

Item is sized to print at 11" x 17" (11:17 aspect ratio).
File size: {d['img_size'][0]}px x {d['img_size'][1]}px

You will receive 1 PNG file to download.
⋯⋯⋯ HOW TO DOWNLOAD ⋯⋯⋯

Ready to download on your computer once your payment is confirmed. No waiting, no shipping fees.
After checkout Etsy will redirect you to the downloads page where you’ll find your new printables ♡.
See your purchase anytime by logging into your Etsy account or through your email receipt.


⋯⋯⋯ HOW TO PRINT ⋯⋯⋯

➤ Upload to a print shop online + have your prints delivered!

➤ Print at home using good, quality card stock or art paper. I recommend a matte finish for the best results.

➤ Print at your local copy shop (Walgreens, Walmart, Costco, Target, FedEx). Note that the image is 11" x 17", which is not a standard size for Walgreens.

Please contact me if you have any questions, I’m happy to help!

⋯⋯⋯ ITEM TEXT ⋯⋯⋯

➤ TITLE: {d['title']}
➤ DIRECTOR: {d['director']}
➤ WRITERS: {w_text}
➤ GENRES: {', '.join(d['genres'])}
➤ RUNTIME: {d['runtime']}
➤ RELEASED: {d['released']}
➤ PLOT: {d['plot']}

{', '.join(all_tags)}

[{d['title_slug']}/{d['cover_id']}]'''
    bad_regex = re.compile(r"[^a-zA-Z0-9\s\-'™©®]")
    tags = list(set([i.lower() for i in filter(lambda x: (not bad_regex.search(x)) and len(x) <= 20, all_tags)]))
    data = {
        'quantity': 999,
        'price': 5.00,
        'description': description,
        'title': title,
        'taxonomy_id': 125,  # music & movie posters
        'state': 'active',
        'shipping_template_id': 118526562927,
        'processing_min': 0,
        'processing_max': 0,
        'tags': ','.join(tags),
        'is_supply': False,
        'who_made': 'i_did',
        'when_made': '2020_2020' #'made_to_order'
    }

    r = etsy.post(BASE_URL + '/listings', data=data)
    try:
        r = r.json()
    except Exception as e:
        print(e, r.text)
        exit()
    listing_id = r['results'][0]['listing_id']

    upload_listing_img(etsy, listing_id, d['img_path'])
    create_listing_img(d['img_path']).save('temp_cover.png')
    upload_listing_img(etsy, listing_id, 'temp_cover.png')
    file_name = d['title_slug'] + "-" + d['cover_id']
    upload_listing_file(etsy, listing_id, d['img_path'], file_name)
def upload_listing_img(etsy, listing_id, image_path):
    data = {
        'listing_id': listing_id
    }
    files = {
        'image': (image_path, open(image_path, 'rb'), 'image/png')
    }

    r = etsy.post(BASE_URL + f'/listings/{listing_id}/images', data=data, files=files)
    try:
        r = r.json()
    except Exception as e:
        print(e, r.text)
        exit()
    print(image_path, 'IMG UPLOADED')
def upload_listing_file(etsy, listing_id, file_path, file_name):
    data = {
        'listing_id': listing_id,
        'name': file_name + '.png'
    }
    files = {
        'file': (file_path, open(file_path, 'rb'), 'image/png')
    }

    r = etsy.post(BASE_URL + f'/listings/{listing_id}/files', data=data, files=files)
    try:
        r = r.json()
    except Exception as e:
        print(e, r.text)
        exit()
    print(file_name, 'FILE UPLOADED')
with open('posters/avatar-the-last-airbender-0417299/data/637079483.json') as f:

    example_data = json.load(f) 
