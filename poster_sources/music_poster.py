from PIL import Image
import logging

class BopShopPoster(Poster):
    def create_poster(self):
        width = int(1.1 * self.size)
        height = int(1.7 * self.size)
        margin = int(.05 * self.size)

  
        poster = Image.new('RGB', (width, height), color='white')
        logging.info('Creating new poster with dimensions {width}, {height}')

        poster.paste(self.img, box=(margin, margin))

        print(self.colors)
        return poster
class MusicPoster(Poster):
    def create_poster(self):
        width = int(1.1 * self.size)
        height = int(1.7 * self.size)
        margin = int(.05 * self.size)

  
        poster = Image.new('RGB', (width, height), color='white')
        logging.info('Creating new poster with dimensions {width}, {height}')

        poster.paste(self.img, box=(margin, margin))

        print(self.colors)
        return poster
    

