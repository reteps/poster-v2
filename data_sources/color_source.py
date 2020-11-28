import math
from colorthief import ColorThief
from PIL import ImageShow, ImageFile, ImageFont, ImageDraw, Image
from image_sources.windows_image import CustomImage
import math
# import pyautogui._pyautogui_win as platformModule
class MyColorThief(ColorThief):
    def __init__(self, pil):
        self.image = pil
def thief_color_palette(pil_img, count=5):
    colors = MyColorThief(pil_img).get_palette(color_count=count)
    return [{'color': to_hex(c), 'amount': 0} for c in colors]
def distance_from(color, compare_to=(255,255,255)):
    r,g,b = color
    r2,g2,b2=compare_to
    return math.sqrt((r2-r)**2 + (g2-g)**2 + (b2-b)**2) / math.sqrt((255)**2+(255)**2+(255)**2)
def ext_color_palette(pil_img):
    import extcolors
    colors, pixel_count = extcolors.extract_from_image(pil_img)
    for c in colors:
        pass
        #print(distance_from(c[0]))
    colors = list(filter(lambda x: distance_from(x[0]) > 0.08, colors))
    return [{'color': to_hex(c[0]), 'amount': c[1]} for c in colors]
def combo_color_palette(pil_img):
    return ext_color_palette(pil_img) + thief_color_palette(pil_img)
def to_hex(tuple):
    import binascii
    return binascii.hexlify(bytearray(int(c) for c in tuple)).decode('ascii')
def scipy_color_palette(pil_img, count=10, quality=(200,200)):
    import numpy as np
    import scipy
    import scipy.misc
    import scipy.cluster
    pil_img = pil_img.resize(quality)
    ar = np.asarray(pil_img)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)
    # Find clusters
    codes, dist = scipy.cluster.vq.kmeans(ar, count)
    # Assign Codes
    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences
    index_max = scipy.argsort(counts)[::-1]
    peak = codes[index_max]
    colors = [to_hex(rgb) for rgb in codes[index_max]]
    return colors
def retrieve_user_colors(img, colors,n=5):
    color_height = round(img.size[1] * .1)
    color_width = math.floor(img.size[0] / len(colors))
    new_img = Image.new("RGB", (img.size[0], img.size[1] + color_height))
    new_img.paste(img, (0,0))
    draw = ImageDraw.Draw(new_img)
    font = ImageFont.truetype("/mnt/c/Windows/Fonts/micross.ttf", 50)
    for i, color in enumerate(colors):
        draw.rectangle(
            (color_width*i, img.size[1], color_width*(i+1), img.size[1] + color_height), fill='#'+color['color']
        )
        text = f"{i+1}"
        w, h = font.getsize(text)
        draw.rectangle((color_width*i, img.size[1], color_width*i + w, img.size[1] + h), fill="white")
        draw.text((color_width*i, img.size[1]), text, (0, 0, 0), font=font)
    
    selected = []
    img = CustomImage(new_img)
    img.show()
    while len(selected) != n:
        selection = int(input(f'Select color #{len(selected)+1}/{n}>'))-1
        selected.append(colors[selection])
    img.hide()
    return selected