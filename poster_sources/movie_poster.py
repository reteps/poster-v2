from poster_sources.poster_base import Poster
from PIL import Image, ImageFont, ImageDraw
import logging
import pathlib
import datetime
import textwrap


class AlbumStylePoster(Poster):
    def margin_ratio(self):
        return .05
    def create_poster(self):
        draw = self.draw
        poster = self.poster
        margin = int(self.margin_ratio() * self.size)

        # image
        poster.paste(self.img, box=(margin, margin))

        # corner text 2h 51min / October 28, 2004

        # give space for a rating

        # give space for color bars

        color_y = self.size + margin * 2
        color_bar_spacing = 15 * self.size // 1000
        # x / 1.7
        color_bar_height = ((self.height - self.size - margin * 3) * 3/5 - (len(self.colors) - 1) * color_bar_spacing) / len(self.colors)
        end_y = self.size + margin * 2 +(color_bar_height+color_bar_spacing)*len(self.colors)


        
        '''
        1) initial rating, initial color bar, initial director
        2) title size is calculated, bounded by
        WIDTH of RATING
        HEIGHT of COLORS + DIRECTOR
        3) rating size is calculated, bounded by
        HEIGHT of TITLE
        4) director size is calculated, bounded by
        HEIGHT of TITLE + DIRECTOR
        5) color width is calculated, bounded by
        WIDTH of DIRECTOR
        6) plot width is calculated, bounded by
        WIDTH of COLORS

        instead, title width should be maximized as long as after the rating is shrunk, the rating & title have space.

        1) ALIEN - bounded by HEIGHT first
        
        2) THE GRAND BUDAPEST HOTEL - bounded by WIDTH first
        if bounded by WIDTH
        '''

        # get director text size
        d_text = f'{self.director.upper()}'
        director_font_size = 50 * self.size // 1000
        director_font = ImageFont.truetype('fonts/Aku&Kamu.otf', director_font_size)
        _, director_h = draw.textsize(d_text, director_font)

        # Calculate initial title size
        vertical_title_space = self.height - end_y - director_h - margin
        horizontal_title_space = self.size

        vertical_title_font = self.font_percent(self.title.upper(), vertical_title_space, 'fonts/Aku&Kamu.otf', direction=1)
        '''
        horizontal_title_font_size = 50 * self.size // 1000
        corner_text = f'{self.runtime} / {self.released}'
        rating_img = Image.open(pathlib.Path().absolute() / 'ratings' / f'{self.rated}.png')
        r_w, r_h = rating_img.size
        ratio = 1
        rating_w = 1
        rating_h = 0 # r_h
        corner_font = self.font_percent(corner_text, rating_w, 'fonts/Aku&Kamu.otf')
        _, corner_h = (0,0) # draw.textsize(corner_text, corner_font)
        corner_font = self.font_percent(corner_text, r_w, 'fonts/Aku&Kamu.otf')
        while horizontal_title_space >= 0 and horizontal_title_font_size < vertical_title_font.size:
            if horizontal_title_space > 300:
                horizontal_title_font_size += 10
            elif horizontal_title_space > 150:
                horizontal_title_font_size += 3
            else:
                horizontal_title_font_size += 1
            temp_horizontal_title_font = ImageFont.truetype('fonts/Aku&Kamu.otf', horizontal_title_font_size)
            title_font_w, title_font_h = draw.textsize(self.title.upper(), temp_horizontal_title_font)
            specific_title_font_h = draw.textbbox((0,0),self.title.upper(), font=temp_horizontal_title_font, anchor='lt')[3]
            # Init Defaults

            while (corner_h + rating_h) < specific_title_font_h:
                ratio = rating_w / r_w
                rating_h = int(r_h * ratio)
                corner_font = self.font_percent(corner_text, rating_w, 'fonts/Aku&Kamu.otf')
                _, corner_h = draw.textsize(corner_text, corner_font)
                rating_w += 1 * self.size // 1000
            horizontal_title_space = self.size - rating_w - title_font_w - margin / 4
            print(horizontal_title_space)
        horizontal_title_font = temp_horizontal_title_font
        '''


        '''
        rating_img = rating_img.resize((rating_w, rating_h))
        poster.paste(rating_img, box=(margin, self.height - margin - rating_h))
        draw.text((margin, self.height - margin - rating_h), corner_text, font=corner_font, anchor='ld', fill='black')
        '''
        # MODIFIED
        horizontal_title_space = self.size
        horizontal_title_font = self.font_percent(self.title.upper(), horizontal_title_space, 'fonts/Aku&Kamu.otf')
        # END MODIFIED
        best_title_font = min(horizontal_title_font, vertical_title_font, key=lambda font:font.size)
        _, best_title_font_h = draw.textsize(self.title.upper(), best_title_font)
        # draw.text((self.width - margin, self.height - margin), self.title.upper(), anchor='rs', fill='black', font=best_title_font)
        draw.text((margin, self.height - margin), self.title.upper(), anchor='ls', fill='black', font=best_title_font)
        # now actually put down director

        d_text = f'{self.director.upper()}'
        vertical_director_space = vertical_title_space - best_title_font_h + director_h
        print(vertical_director_space)
        director_font = self.font_percent(self.title.upper(), vertical_director_space, 'fonts/Aku&Kamu.otf', direction=1)
        director_font_w, _ = draw.textsize(d_text, director_font)
        draw.text((self.width - margin, end_y), d_text, anchor='ra',fill='black',font=director_font)
        # draw.text((margin, end_y), d_text, anchor='la',fill='black',font=director_font)

        # now actually draw color bars
        maximum_color_width = max(director_font_w, int(self.size / 2.8))
        max_pixels = max(self.colors, key=lambda x:x['amount'])['amount']
        min_color_bar_width = color_bar_height
        end_y = 0
        for i, c in enumerate(self.colors):
            pixel_width = int(c['amount'] / max_pixels * (maximum_color_width - min_color_bar_width)) + min_color_bar_width
            base_y = color_y+(color_bar_height+color_bar_spacing)*i
            end_y = base_y + color_bar_height
            # draw.rectangle((margin, base_y, margin + pixel_width, end_y), fill='#'+c['color'])
            draw.rectangle((self.width - margin, base_y, self.width - margin - pixel_width, end_y), fill='#'+c['color'])

        # now plot?
        plot_font_size = 25 * self.size // 1000
        plot_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', plot_font_size)
        plot_y = self.size + margin * 2
        plot_horizontal_space = self.size - margin - maximum_color_width
        right_side_x = margin * 2 + maximum_color_width
        plot_height = self.justified_text_box((margin, plot_y), self.plot, plot_horizontal_space, plot_font)
        # plot_height = self.justified_text_box((right_side_x, plot_y), self.plot, plot_horizontal_space, plot_font)

        def debug_line(y):
            draw.rectangle((0, y, self.width, y+5), fill='red')


        # now cast
        '''
        cast_y = self.height - margin - rating_h - corner_h
        cast_text = '\n'.join(['Starring'] + self.cast)
        _, cast_text_h = draw.textsize(cast_text, plot_font)
        draw.text((margin, cast_y - cast_text_h), cast_text, fill='black', font=plot_font)
        '''
        bottom_font_size = 25 * self.size // 1000
        bottom_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', bottom_font_size)
        genres = ', '.join(self.genres[:4])
        time_w, _ = draw.textsize(self.runtime, bottom_font)
        release_w, release_h = draw.textsize(self.released, bottom_font)
        available_space = self.size - maximum_color_width - margin - time_w - release_w

        genre_x = available_space // 2 + time_w + margin
        # genre_x = right_side_x + available_space // 2 + time_w
        # draw.text((right_side_x, self.height - margin - best_title_font_h), self.runtime,anchor='ls',fill='black',font=bottom_font)
        # draw.text((self.width - margin, self.height - margin - best_title_font_h), self.released,anchor='rs',fill='black',font=bottom_font)
        # draw.text((genre_x, self.height - margin - best_title_font_h), genres,anchor='ms',fill='black',font=bottom_font)
        draw.text((margin, self.height - margin - best_title_font_h), self.runtime,anchor='ls',fill='black',font=bottom_font)
        draw.text((self.size - maximum_color_width, self.height - margin - best_title_font_h), self.released,anchor='rs',fill='black',font=bottom_font)
        draw.text((genre_x, self.height - margin - best_title_font_h), genres,anchor='ms',fill='black',font=bottom_font)


class ClassicultPoster(Poster):
    def margin_ratio(self):
        return .05 # .1/1.2
    def create_poster(self):
        def debug_line(y):
            draw.rectangle((0, y, self.width, y+5), fill='red')
        def x_debug_line(x):
            draw.rectangle((x, 0, x+5, self.height), fill='red')
        draw = self.draw
        poster = self.poster
        margin = int(self.margin_ratio() * self.size)
        # year init
        year_font_size = 40 * self.size // 1000
        year_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', year_font_size)
        year_font_w, _ = draw.textsize(self.year, year_font)

        # title
        font_size = 80 * self.size // 1000

        while True:
            font = ImageFont.truetype('fonts/Sequel/Sequel100Black-85.ttf', font_size)

            title_wrap, title_h = self.wrap_text(self.title.upper(), self.size - margin - year_font_w, font)
            if len(title_wrap) <= 2:
                break
            font_size -= 1
        total_title_height = title_h*len(title_wrap)
        additional_title_height = title_h*(len(title_wrap) - 1)
        title_y = margin * 1.5
        adjusted_title_y = int(title_y - additional_title_height)
        for i, line in enumerate(title_wrap):
            draw.text((margin, title_y + i * title_h), line, fill='black', anchor='lt', font=font)
        
        # img
        img_y = int(margin * 0.5 + title_y + total_title_height)
        poster.paste(self.img, box=(margin, img_y))

        # title
        # line
        bar_height = 4 * self.size // 1000
        draw.rectangle((margin, margin, margin+self.size, margin+bar_height), fill='black')

        # year con't

        draw.text((margin+self.size, title_y), self.year, anchor='rt',fill='black',font=year_font)

        right_side_width = int(self.size * .36)
        right_side_x = self.size - right_side_width + margin
        left_side_width = self.size - right_side_width - margin
        # colors
        color_y = int(img_y + margin + self.size)
        color_bar_spacing = 20 * self.size // 1000

        # rating
        rating_height = 0
        rating_at_top = False
        color_largest_at_top = True
        if self.rated != '':
            rating_img = Image.open(pathlib.Path().absolute() / 'ratings' / f'{self.rated}.png')
            r_w, r_h = rating_img.size
            if 'tv' in self.rated:
                rating_height = int((self.height - color_y - margin - color_bar_spacing * (len(self.colors))) / (len(self.colors)+1))
                line_width = 3 * self.size // 1000
                rating_img_with_border = rating_height - line_width*2
                rating_img = rating_img.resize((rating_img_with_border, rating_img_with_border))
                if rating_at_top:
                    draw.rectangle((self.width - margin - rating_height, color_y, self.width - margin, color_y + rating_height), outline='black', width=line_width)
                    poster.paste(rating_img, box=(self.width - margin - rating_height+line_width, color_y + line_width))
                else:
                    draw.rectangle((self.width - margin - rating_height, self.height - margin, self.width - margin, self.height - margin - rating_height), outline='black', width=line_width)
                    poster.paste(rating_img, box=(self.width - margin - rating_height + line_width, self.height - margin - rating_height + line_width))
            else:
                ratio = right_side_width / r_w
                rating_height = int(r_h * ratio)
                rating_img = rating_img.resize((int(r_w * ratio), rating_height))
                r_w, r_h = rating_img.size
                if rating_at_top:
                    print("TODOOTODODOODODO")
                    pass
                else:
                    poster.paste(rating_img, box=(right_side_x, self.height - margin - r_h))
    
        # normalize color amounts to a pixel_width
        color_bar_width = (right_side_width + margin - (color_bar_spacing*len(self.colors)-1))  / len(self.colors)
        color_bar_height = 120 * self.size // 1000
        max_pixels = max(self.colors, key=lambda x:x['amount'])['amount']
        for i, c in enumerate(self.colors):
            base_x = color_bar_spacing + self.width - margin - margin - right_side_width + (color_bar_width+color_bar_spacing)*i
            # end_y = base_y + color_bar_height
            draw.rectangle((base_x, color_y, base_x + color_bar_width, color_y + color_bar_height), fill='#'+c['color'])
            
        '''
        color_margin = 20 * self.size // 1000
        color_width = ((self.size - margin) / 2 - (color_margin * (len(self.colors) - 1))) // len(self.colors) # leave a margin space in center
        color_height = 25 * self.size // 1000
        for i, c in enumerate(self.colors):
            x_offset = i*(color_width+color_margin) + right_side_x
            draw.rectangle((x_offset, color_y, x_offset+color_width, color_y+color_height), fill='#'+c['color'])
        '''
        # director
        d_text = f'{self.director}'
        director_font = self.font_percent(d_text, left_side_width, 'fonts/Sequel/Sequel100Black-85.ttf')
        maximum_director_font = ImageFont.truetype('fonts/Sequel/Sequel100Black-85.ttf', 55 * self.size // 1000)
        director_font = min(maximum_director_font, director_font, key=lambda x:x.size)
        _, director_h = draw.textsize(d_text, director_font)
        draw.text((margin, color_y), d_text, anchor='lt',fill='black',font=director_font)

        # writers

        if len(self.writers) == 1:
            w_text = self.writers[0]
        else:
            out = ", ".join(self.writers[:-1])
            # Add the last element, separated by "and" and a final "."
            w_text = "{} and {}".format(out, self.writers[-1])
        w_text = f'Written by {w_text}'
        if len(self.writers) == 1:
            writer_font = self.font_percent(w_text, (self.size - margin) // 3, 'fonts/Gidole-Regular.ttf')
        else:
            writer_font = self.font_percent(w_text, left_side_width, 'fonts/Gidole-Regular.ttf')
        writer_w, writer_h = draw.textsize(w_text, writer_font)
        draw.text((margin, color_y + director_h), w_text, anchor='lt',fill='black',font=writer_font)

        # bottom elements

        # runtime / seasons
        bottom_font_size = 22 * self.size // 1000
        bottom_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', bottom_font_size)
        draw.text((margin, self.height - margin), self.runtime,anchor='ls',fill='black',font=bottom_font)
        # released date
        draw.text((right_side_x - margin, self.height - margin), self.released,anchor='rs',fill='black',font=bottom_font)

        # genre
        genres = ', '.join(self.genres[:4])
        time_w, _ = draw.textsize(self.runtime, bottom_font)
        release_w, release_h = draw.textsize(self.released, bottom_font)
        available_space_genre = left_side_width - time_w - release_w
        genre_x = available_space_genre // 2 + time_w + margin
        draw.text((genre_x, self.height - margin), genres,anchor='ms',fill='black',font=bottom_font)

        # plot

        plot_font_size = 20 * self.size // 1000
        plot_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', plot_font_size)

        max_plot_y = color_y + director_h + writer_h
        available_space = self.height - max_plot_y - margin - release_h
        lines, plot_line_height = self.wrap_text(self.plot, left_side_width, plot_font)
        plot_height = len(lines) * plot_line_height

        center_of_available_space = (available_space - plot_height) // 2
        self.justified_text_box((margin, max_plot_y + center_of_available_space), self.plot, left_side_width, plot_font)


class ClassicultBarPoster(Poster):
    def margin_ratio(self):
        return .05 # .1/1.2
    def create_poster(self):
        def debug_line(y):
            draw.rectangle((0, y, self.width, y+5), fill='red')
        def x_debug_line(x):
            draw.rectangle((x, 0, x+5, self.height), fill='red')
        draw = self.draw
        poster = self.poster
        margin = int(self.margin_ratio() * self.size)
        # year init
        year_font_size = 40 * self.size // 1000
        year_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', year_font_size)
        year_font_w, _ = draw.textsize(self.year, year_font)

        # title
        font_size = 80 * self.size // 1000

        while True:
            font = ImageFont.truetype('fonts/Sequel/Sequel100Black-85.ttf', font_size)

            title_wrap, title_h = self.wrap_text(self.title.upper(), self.size - margin - year_font_w, font)
            if len(title_wrap) <= 2:
                break
            font_size -= 1
        total_title_height = title_h*len(title_wrap)
        additional_title_height = title_h*(len(title_wrap) - 1)
        title_y = margin * 1.5
        adjusted_title_y = int(title_y - additional_title_height)
        for i, line in enumerate(title_wrap):
            draw.text((margin, title_y + i * title_h), line, fill='black', anchor='lt', font=font)
        
        # img
        img_y = int(margin * 0.5 + title_y + total_title_height)
        poster.paste(self.img, box=(margin, img_y))

        # title
        # line
        bar_height = 4 * self.size // 1000
        draw.rectangle((margin, margin, margin+self.size, margin+bar_height), fill='black')

        # year con't

        draw.text((margin+self.size, title_y), self.year, anchor='rt',fill='black',font=year_font)

        right_side_width = int(self.size * .36)
        right_side_x = self.size - right_side_width + margin
        left_side_width = self.size - right_side_width - margin
        # colors
        color_y = int(img_y + margin + self.size)
        color_bar_spacing = 12 * self.size // 1000

        # rating
        rating_height = 0
        rating_at_top = False
        color_largest_at_top = True
        if self.rated != '':
            rating_img = Image.open(pathlib.Path().absolute() / 'ratings' / f'{self.rated}.png')
            r_w, r_h = rating_img.size
            if 'tv' in self.rated:
                rating_height = int((self.height - color_y - margin - color_bar_spacing * (len(self.colors))) / (len(self.colors)+1))
                line_width = 3 * self.size // 1000
                rating_img_with_border = rating_height - line_width*2
                rating_img = rating_img.resize((rating_img_with_border, rating_img_with_border))
                if rating_at_top:
                    draw.rectangle((self.width - margin - rating_height, color_y, self.width - margin, color_y + rating_height), outline='black', width=line_width)
                    poster.paste(rating_img, box=(self.width - margin - rating_height+line_width, color_y + line_width))
                else:
                    draw.rectangle((self.width - margin - rating_height, self.height - margin, self.width - margin, self.height - margin - rating_height), outline='black', width=line_width)
                    poster.paste(rating_img, box=(self.width - margin - rating_height+line_width, self.height - margin - rating_height+line_width))
            else:
                ratio = right_side_width / r_w
                rating_height = int(r_h * ratio)
                rating_img = rating_img.resize((int(r_w * ratio), rating_height))
                r_w, r_h = rating_img.size
                if rating_at_top:
                    print("TODOOTODODOODODO")
                    pass
                else:
                    poster.paste(rating_img, box=(right_side_x, self.height - margin - r_h))
    
        # normalize color amounts to a pixel_width
        if self.rated != '':
            color_bar_height = (self.height - color_y - rating_height - margin - color_bar_spacing * len(self.colors)) / len(self.colors)
        else:
            color_bar_height = (self.height - color_y - margin - color_bar_spacing * (len(self.colors) - 1) ) / len(self.colors)
        maximum_color_width = right_side_width
        max_pixels = max(self.colors, key=lambda x:x['amount'])['amount']
        min_color_bar_width = color_bar_height
        for i, c in enumerate(self.colors):
            pixel_width = int(c['amount'] / max_pixels * (maximum_color_width - min_color_bar_width)) + min_color_bar_width
            if color_largest_at_top:
                base_y = color_y+(color_bar_height+color_bar_spacing)*i
            else:
                base_y = color_y+(color_bar_height+color_bar_spacing)*(len(self.colors) - i - 1)
                if rating_at_top:
                    base_y += rating_height + color_bar_spacing
            end_y = base_y + color_bar_height
            draw.rectangle((self.width - margin, base_y, self.width - margin - pixel_width, end_y), fill='#'+c['color'])
            
        '''
        color_margin = 20 * self.size // 1000
        color_width = ((self.size - margin) / 2 - (color_margin * (len(self.colors) - 1))) // len(self.colors) # leave a margin space in center
        color_height = 25 * self.size // 1000
        for i, c in enumerate(self.colors):
            x_offset = i*(color_width+color_margin) + right_side_x
            draw.rectangle((x_offset, color_y, x_offset+color_width, color_y+color_height), fill='#'+c['color'])
        '''
        # director
        d_text = f'{self.director}'
        director_font = self.font_percent(d_text, left_side_width, 'fonts/Sequel/Sequel100Black-85.ttf')
        maximum_director_font = ImageFont.truetype('fonts/Sequel/Sequel100Black-85.ttf', 55 * self.size // 1000)
        director_font = min(maximum_director_font, director_font, key=lambda x:x.size)
        _, director_h = draw.textsize(d_text, director_font)
        draw.text((margin, color_y), d_text, anchor='lt',fill='black',font=director_font)

        # writers

        if len(self.writers) == 1:
            w_text = self.writers[0]
        else:
            out = ", ".join(self.writers[:-1])
            # Add the last element, separated by "and" and a final "."
            w_text = "{} and {}".format(out, self.writers[-1])
        w_text = f'Written by {w_text}'
        if len(self.writers) == 1:
            writer_font = self.font_percent(w_text, (self.size - margin) // 3, 'fonts/Gidole-Regular.ttf')
        else:
            writer_font = self.font_percent(w_text, left_side_width, 'fonts/Gidole-Regular.ttf')
        writer_w, writer_h = draw.textsize(w_text, writer_font)
        draw.text((margin, color_y + director_h), w_text, anchor='lt',fill='black',font=writer_font)

        # bottom elements

        # runtime / seasons
        bottom_font_size = 22 * self.size // 1000
        bottom_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', bottom_font_size)
        draw.text((margin, self.height - margin), self.runtime,anchor='ls',fill='black',font=bottom_font)
        # released date
        draw.text((right_side_x - margin, self.height - margin), self.released,anchor='rs',fill='black',font=bottom_font)

        # genre
        genres = ', '.join(self.genres[:4])
        time_w, _ = draw.textsize(self.runtime, bottom_font)
        release_w, release_h = draw.textsize(self.released, bottom_font)
        available_space_genre = left_side_width - time_w - release_w
        genre_x = available_space_genre // 2 + time_w + margin
        draw.text((genre_x, self.height - margin), genres,anchor='ms',fill='black',font=bottom_font)

        # plot

        plot_font_size = 20 * self.size // 1000
        plot_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', plot_font_size)

        max_plot_y = color_y + director_h + writer_h
        available_space = self.height - max_plot_y - margin - release_h
        lines, plot_line_height = self.wrap_text(self.plot, left_side_width, plot_font)
        plot_height = len(lines) * plot_line_height

        center_of_available_space = (available_space - plot_height) // 2
        self.justified_text_box((margin, max_plot_y + center_of_available_space), self.plot, left_side_width, plot_font)

