from poster_sources.poster_base import Poster
from PIL import Image, ImageFont
import logging

class BopShopPoster(Poster):
    @property
    def margin_ratio(self):
        return .05
    def create_poster(self):
        self.poster.paste(self.img, box=(self.margin, self.margin))

class MusicPoster(Poster):
    @property
    def margin_ratio(self):
        return .05
    def create_poster(self):
        poster = self.poster
        margin = self.margin
        draw = self.draw
        # image
        poster.paste(self.img, box=(margin, margin))

        color_bar_height = self.size * 60 // 1000
        color_bar_spacing = self.size * 15 // 1000
        max_pixels = max(self.colors, key=lambda x:x['amount'])['amount']
        min_color_bar_width = color_bar_height
        start_color_y = self.size + margin * 2
        end_y = 0
        maximum_color_width = 360 * self.size // 1000
        for i, c in enumerate(self.colors):
            pixel_width = int(c['amount'] / max_pixels * (maximum_color_width - min_color_bar_width)) + min_color_bar_width
            base_y = start_color_y + (color_bar_height+color_bar_spacing)*i
            end_y = base_y + color_bar_height
            # draw.rectangle((margin, base_y, margin + pixel_width, end_y), fill='#'+c['color'])
            draw.rectangle((self.width - margin, base_y, self.width - margin - pixel_width, end_y), fill='#'+c['color'])

        # corner
        corner_font_size = self.size * 30 // 1000
        corner_font = ImageFont.truetype('fonts/Aku&Kamu.otf', corner_font_size)

        sec_sum = 0
        for i, song in enumerate(self.songs):
            sec_sum += song['time']
        m,s = divmod(sec_sum, 60)
        h,m = divmod(m,60)
        time_formatted = f"{m:02}:{s:02}"
        if h != 0:
            time_formatted = h + ':' + time_formatted
        corner_text = f'{time_formatted} / {self.release_date}'
        if self.label:
            corner_text += '\n' + self.label
        
        _, corner_h = draw.textsize(corner_text, corner_font)
        draw.text((margin, self.height - margin - corner_h), corner_text, fill='black', font=corner_font)

