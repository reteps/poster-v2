from abc import ABC, abstractmethod
import logging
from image_sources.windows_image import CustomImage
from PIL import Image, ImageDraw, ImageFont
class Poster(ABC):
    def __init__(self, data, o_cover, minimum_size=2000):
        self.data = data
        # resize square:
        if o_cover.size[0] != o_cover.size[1]:
            logging.info(f'Resizing to be square ({o_cover.size}) -> ({[o_cover.size[0], o_cover.size[0]]})')
            o_cover = o_cover.resize((o_cover.size[0], o_cover.size[0]))
        if o_cover.size[0] < minimum_size:
            logging.info(f'Resizing to minimum size ({o_cover.size}) -> ({[minimum_size, minimum_size]})')
            o_cover = o_cover.resize((minimum_size, minimum_size))
        self.img = o_cover
        self.size = o_cover.size[0]
        for key in data:
            setattr(self, key, data[key])
        margin = self.margin_ratio() * 2
        self.width = int((1 + margin) * self.size)
        self.height = int(1.7 / 1.1 * self.width)
        self.poster = Image.new('RGB', (self.width, self.height), color='white')
        self.draw = ImageDraw.Draw(self.poster)
        logging.info('Creating new poster with dimensions {width}, {height}')
    @abstractmethod
    def create_poster(self):
        pass
    @abstractmethod
    def margin_ratio(self):
        return .5
    def get_poster(self):
        self.create_poster()
        return CustomImage(self.poster)


    @staticmethod
    def wrap_text(text, width, font):
        lines = []
        line = []
        words = text.split()
        for word in words:
            new_line = ' '.join(line + [word])
            size = font.getsize(new_line)
            text_height = size[1]
            if size[0] <= width:
                line.append(word)
            else:
                lines.append(line)
                line = [word]
        if line:
            lines.append(line)
        lines = [' '.join(line) for line in lines if line]
        return lines, text_height
    def justified_text_box(self, xy, text, box_width, font, color=(0, 0, 0), place='left',
                       justify_last_line=False):
        
        
        x, y = xy
        lines, text_height = self.wrap_text(text, box_width, font)
        height = y
        for index, line in enumerate(lines):
            words = line.split()
            # If it is the last line or only 1 word, do not justify
            if (index == len(lines) - 1 and not justify_last_line) or len(words) == 1:
                self.draw.text((x, height), line, font=font, fill=color)
                height += text_height
                continue
            line_without_spaces = ''.join(words)
            total_size = font.getsize(line_without_spaces)
            space_width = (box_width - total_size[0]) / (len(words) - 1.0)
            start_x = x
            for word in words[:-1]:
                self.draw.text((start_x, height), word, font=font, fill=color)
                word_size = font.getsize(word)

                start_x += word_size[0] + space_width
            last_word_width = font.getsize(words[-1])[0]
            last_word_x = x + box_width - last_word_width
            self.draw.text((last_word_x, height), words[-1], font=font, fill=color)
            height += text_height
        return height - y
    def font_percent(self, text, pixel_width, fontpath, direction=0):
        '''
        returns the font to have text fill that % width of image
        '''
        breakpoint = pixel_width
        jumpsize = 25
        fontsize = 25
        font = ImageFont.truetype(fontpath, fontsize)
        while True:
            size = self.draw.textsize(text, font)[direction]
            if size / breakpoint < 1 and size / breakpoint > .97:
                break
            if size < breakpoint:
                fontsize += jumpsize
            else:
                jumpsize = jumpsize // 2
                fontsize -= jumpsize
            font = ImageFont.truetype(fontpath, fontsize)
            if jumpsize <= 1:
                break
        return font