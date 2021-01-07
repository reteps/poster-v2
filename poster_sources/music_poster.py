from poster_sources.poster_base import Poster
from PIL import Image, ImageFont
import logging

class AlbumArtEngineer(Poster):
    @property
    def margin_ratio(self):
        return .05
    def create_poster(self):
        poster = self.poster
        margin = self.margin
        draw = self.draw
        # image
        poster.paste(self.img, box=(margin, margin))

        # color bars
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
            time_formatted = str(h) + ':' + time_formatted
        corner_text = f'{time_formatted} / {self.release_date}'
        if self.label:
            corner_text += '\n' + self.label
        
        corner_w, corner_h = draw.textsize(corner_text, corner_font)
        draw.text((margin, self.height - margin - corner_h), corner_text, fill='black', font=corner_font)

        # subtitle

        subtitle_font_size = self.size * 45 // 1000
        subtitle_font = ImageFont.truetype('fonts/Aku&Kamu.otf', subtitle_font_size)
        subtitle_anchor = end_y + color_bar_spacing
        _, subtitle_h = draw.textsize(self.artist, subtitle_font)

        # title

        vertical_title_space = self.height - subtitle_anchor - subtitle_h - margin
        horizontal_title_space = self.width - margin - margin - corner_w
        title_font, title_limit_dir = self.font_fill_box(self.title, vertical_title_space, horizontal_title_space, 'fonts/Aku&Kamu.otf')
        title_font_w, title_font_h = draw.textsize(self.title, title_font)
        (_, _), (_, offset_y) = title_font.font.getsize(self.title)
        title_font_h -= offset_y
        if title_limit_dir == 0:
            vertical_subtitle_space = self.height - subtitle_anchor - title_font_h - margin
            subtitle_font, _ = self.font_fill_box(self.artist, vertical_subtitle_space, maximum_color_width, 'fonts/Aku&Kamu.otf')
        draw.text((self.width - margin, self.height - margin), self.title, anchor='rs', fill='black', font=title_font)
        draw.text((self.width - margin, self.height - margin - title_font_h - color_bar_spacing), self.artist, anchor='rb', fill='black', font=subtitle_font)

        # song list
        # OH FUCK OH SHIT

        vertical_song_space = self.height - start_color_y - corner_h - margin
        horizontal_song_space = self.width - maximum_color_width - margin * 2
        # self.debug_line_y(self.height - corner_h - margin)
        # self.debug_line_y(start_color_y)
        # self.debug_line_x(margin + horizontal_song_space)
        # self.debug_line_x(margin)
        song_bloc = '\n'.join(map(lambda s:s['name'], self.songs))
        min_song_font_size = self.size * 40 // 1000
        one_col_song_font_size = self.font_fill_area(song_bloc, vertical_song_space, 'fonts/Aku&Kamu.otf', direction=1, include_ascent=False).size + 1
        num_cols = 1
        if one_col_song_font_size < min_song_font_size:
            num_cols = 2
        else:
            min_song_font_size = one_col_song_font_size
        actually_draw = False
        shrink_font = False
        while True:
            if shrink_font:
                min_song_font_size -= 1
                shrink_font = False
            song_font = ImageFont.truetype('fonts/Aku&Kamu.otf', min_song_font_size)
            ascent, descent = song_font.getmetrics()
            current_col = 0
            current_y_pos = 0
            number_songs_wrapped = 0
            song_hits_title = False
            for i, song in enumerate(self.songs):
                song_wrapped, line_height = self.wrap_text(song['name'], horizontal_song_space//num_cols, song_font)
                if len(song_wrapped) > 1:
                    number_songs_wrapped += 1
                if num_cols == 1:
                    height = line_height * len(song_wrapped)
                else:
                    height = len(song_wrapped) * (ascent + descent)
                ''' check if the song hits the title'''
                vertical_overlap = start_color_y +current_y_pos + height > self.height - margin - title_font_h - color_bar_spacing
                if vertical_overlap:
                    song_end_pos = margin + draw.textsize(song['name'], song_font)[0] + current_col * horizontal_song_space//num_cols
                    horizontal_overlap = song_end_pos > self.width - title_font_w - margin
                    if horizontal_overlap:
                        # self.debug_line_x(song_end_pos)
                        # self.debug_line_x(self.width - title_font_w - margin, c='blue')
                        # print(song['name'], 'Overlapping Title')
                        song_hits_title = True
                ''' move to the next column if needed '''
                if current_y_pos + height > vertical_song_space or song_hits_title:
                    # print(current_y_pos + height, vertical_song_space)
                    # self.debug_line_y(start_color_y + current_y_pos, c='orange')
                    # self.debug_line_y(start_color_y + vertical_song_space, c='green')
                    if current_col >= num_cols - 1:
                        shrink_font = True
                        break
                    else:
                        current_col += 1
                        current_y_pos = 0
                        # We are now trying to draw on the third column, so shrink the font size
                
                if actually_draw:
                    current_x_offset = current_col * horizontal_song_space//num_cols
                    draw.text((margin + current_x_offset, start_color_y + current_y_pos), '\n'.join(song_wrapped), fill='black', font=song_font)
                current_y_pos += height
            if actually_draw:
                break
            # Add a column if all the songs are super short
            MANUAL_OVERRIDE = False
            if number_songs_wrapped <= 1 and num_cols > 1 and MANUAL_OVERRIDE:
                num_cols += 1
                min_song_font_size = self.size * 40 // 1000 # Go back up to biggest font
            elif not shrink_font:
                actually_draw = True
                
            # 2 Columns
        # else:
        #     draw.text((margin, start_color_y), song_bloc, fill='black', font=song_font)