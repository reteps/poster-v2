from poster_sources.poster_base import Poster
from PIL import Image, ImageFont, ImageDraw
import logging
import pathlib
import datetime
import textwrap

class PeliculaPrint(Poster):
    @property
    def margin_ratio(self):
        return .065
    def create_poster(self):
        draw = self.draw
        poster = self.poster
        margin = self.margin
        dgray = '#202221'
        big_margin = int(margin * 1.6)
        # line
        bar_height = 4 * self.size // 1000
        draw.rectangle(((margin, big_margin), (margin+self.size, big_margin+bar_height)), fill='black')
        # year
        year_font_size = 40 * self.size // 1000
        year_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', year_font_size)
        year_font_w, year_font_h = draw.textsize(self.year, year_font)
        draw.rectangle(((self.width - margin - int(year_font_w*1.1), big_margin+bar_height), (self.width - margin, big_margin + bar_height  + int(year_font_h*1.1))), fill='black')
        draw.text((self.width - margin, big_margin + bar_height), self.year, fill='white', anchor='rt', font=year_font)
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
        title_y = margin + big_margin + bar_height
        adjusted_title_y = int(title_y - additional_title_height)
        for i, line in enumerate(title_wrap):
            draw.text((margin, title_y + i * title_h), line, fill=dgray, anchor='lt', font=font)
        
        # img
        img_y = int(title_y + (2.5 - len(title_wrap)) * title_h)
        poster.paste(self.img, box=(margin, img_y))

        # color bar

        left_side = int(self.size * .6)
        left_side_x = margin + left_side
        right_side = self.size - left_side
        color_bar_y = img_y + self.size + margin
        color_bar_height = 45 * self.size // 1000
        draw.rectangle(((margin, color_bar_y), (margin+left_side, color_bar_y+color_bar_height)), fill=dgray)

        color_bar_width = (self.size - left_side) // len(self.colors)
        for i, c in enumerate(self.colors):
            base_x = left_side_x + color_bar_width*i
            print(c['color'])
            draw.rectangle(((base_x, color_bar_y), (base_x + color_bar_width, color_bar_y + color_bar_height)), fill='#'+c['color'])

        # Director
        director_font_size = 35 * self.size // 1000
        director_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', director_font_size)
        draw.text((margin, color_bar_y + color_bar_height // 2), 'Directed by ' + self.director,anchor='lm',fill='white',font=director_font)
        # Runtime
        bottom_font_size = 22 * self.size // 1000
        bottom_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', bottom_font_size)
        draw.text((margin, self.height - big_margin), self.runtime,anchor='ls',fill='black',font=bottom_font)

        # released date
        draw.text((left_side_x - margin, self.height - big_margin), self.released,anchor='rs',fill='black',font=bottom_font)

        # genre
        genres = ', '.join(self.genres[:4])
        time_w, _ = draw.textsize(self.runtime, bottom_font)
        release_w, release_h = draw.textsize(self.released, bottom_font)
        available_space_genre = left_side - time_w - release_w - margin
        genre_x = available_space_genre // 2 + time_w + margin
        draw.text((genre_x, self.height - big_margin), genres,anchor='ms',fill='black',font=bottom_font)

        # rating
        rating_height = 0
        if self.rated != '':
            rating_img = Image.open(pathlib.Path().absolute() / 'ratings' / f'{self.rated}.png')
            r_w, r_h = rating_img.size
            if 'tv' in self.rated:
                rating_height = 60 * self.size // 1000
                line_width = 3 * self.size // 1000
                rating_img_with_border = rating_height - line_width*2
                rating_img = rating_img.resize((rating_img_with_border, rating_img_with_border))
                draw.rectangle((self.width - margin - rating_height, self.height - margin, self.width - margin, self.height - margin - rating_height), outline='black', width=line_width)
                poster.paste(rating_img, box=(self.width - margin - rating_height + line_width, self.height - margin - rating_height + line_width))
            else:
                ratio = right_side / r_w
                rating_height = int(r_h * ratio)
                rating_img = rating_img.resize((int(r_w * ratio), rating_height))
                r_w, r_h = rating_img.size
                poster.paste(rating_img, box=(margin + left_side, self.height - big_margin - r_h))

        # Writers
        if len(self.writers) == 1:
            w_text = self.writers[0]
        else:
            out = ", ".join(self.writers[:-1])
            w_text = f"{out} and {self.writers[-1]}"
        w_text = f'Written by {w_text}'
        writer_font_size = 25 * self.size // 1000
        writer_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', writer_font_size)
        writer_w, writer_h = draw.textsize(w_text, writer_font)
        draw.text((margin, color_bar_y + color_bar_height * 1.9), w_text, anchor='lb',fill='black',font=writer_font)

        # Plot
        plot_font_size = 20 * self.size // 1000
        plot_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', plot_font_size)
        self.justified_text_box((margin, color_bar_y + color_bar_height * 2), self.plot, left_side - margin, plot_font)
class Classicult(Poster):
    ''' Not going to be exact due to paper sizes '''
    @property
    def margin_ratio(self):
        return .1
    def create_poster(self):
        draw = self.draw
        poster = self.poster
        margin = self.margin
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
        title_y = margin * 2
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

        right_side_width = int(self.size * .475)
        right_side_x = self.size - right_side_width + margin
        left_side_width = right_side_width
        # colors
        color_y = int(img_y + margin + self.size)
        color_bar_spacing = 20 * self.size // 1000

        # rating
        rating_height = 0
        if self.rated != '':
            rating_img = Image.open(pathlib.Path().absolute() / 'ratings' / f'{self.rated}.png')
            r_w, r_h = rating_img.size
            if 'tv' in self.rated:
                rating_height = int((self.height - color_y - margin - color_bar_spacing * (len(self.colors))) / (len(self.colors)+1))
                line_width = 3 * self.size // 1000
                rating_img_with_border = rating_height - line_width*2
                rating_img = rating_img.resize((rating_img_with_border, rating_img_with_border))
                draw.rectangle((self.width - margin - rating_height, self.height - margin, self.width - margin, self.height - margin - rating_height), outline='black', width=line_width)
                poster.paste(rating_img, box=(self.width - margin - rating_height + line_width, self.height - margin - rating_height + line_width))
            else:
                ratio = left_side_width / r_w
                rating_height = int(r_h * ratio)
                rating_img = rating_img.resize((int(r_w * ratio), rating_height))
                r_w, r_h = rating_img.size
                poster.paste(rating_img, box=(margin, self.height - margin - r_h))
    
        # normalize color amounts to a pixel_width
        color_bar_width = (left_side_width- (color_bar_spacing*len(self.colors)-1))  / len(self.colors)
        color_bar_height = 20 * self.size // 1000
        max_pixels = max(self.colors, key=lambda x:x['amount'])['amount']
        for i, c in enumerate(self.colors):
            base_x = margin + (color_bar_width+color_bar_spacing)*i
            # end_y = base_y + color_bar_height
            draw.rectangle((base_x, color_y, base_x + color_bar_width, color_y + color_bar_height), fill='#'+c['color'])
        # director
        d_text = f'{self.director}'
        director_font = self.font_fill_area(d_text, right_side_width, 'fonts/Sequel/Sequel100Black-85.ttf')
        maximum_director_font = ImageFont.truetype('fonts/Sequel/Sequel100Black-85.ttf', 55 * self.size // 1000)
        director_font = min(maximum_director_font, director_font, key=lambda x:x.size)
        _, director_h = draw.textsize(d_text, director_font)
        draw.text((right_side_x, color_y), d_text, anchor='lt',fill='black',font=director_font)

        # writers

        if len(self.writers) == 1:
            w_text = self.writers[0]
        else:
            out = ", ".join(self.writers[:-1])
            # Add the last element, separated by "and" and a final "."
            w_text = "{} and {}".format(out, self.writers[-1])
        w_text = f'Written by {w_text}'
        if len(self.writers) == 1:
            writer_font = self.font_fill_area(w_text, (self.size - right_side_width) // 3, 'fonts/Gidole-Regular.ttf')
        else:
            writer_font = self.font_fill_area(w_text, right_side_width, 'fonts/Gidole-Regular.ttf')
        writer_w, writer_h = draw.textsize(w_text, writer_font)
        draw.text((right_side_x, color_y + director_h), w_text, anchor='lt',fill='black',font=writer_font)

        # bottom elements

        # runtime / seasons
        bottom_font_size = 22 * self.size // 1000
        bottom_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', bottom_font_size)
        draw.text((right_side_x, self.height - margin), self.runtime,anchor='ls',fill='black',font=bottom_font)
        # released date
        draw.text((self.width - margin, self.height - margin), self.released,anchor='rs',fill='black',font=bottom_font)

        # genre
        genres = ', '.join(self.genres[:4])
        time_w, _ = draw.textsize(self.runtime, bottom_font)
        release_w, release_h = draw.textsize(self.released, bottom_font)
        available_space_genre = right_side_width - time_w - release_w
        genre_x = available_space_genre // 2 + time_w + right_side_x
        draw.text((genre_x, self.height - margin), genres,anchor='ms',fill='black',font=bottom_font)

        # plot

        plot_font_size = 20 * self.size // 1000
        plot_font = ImageFont.truetype('fonts/Gidole-Regular.ttf', plot_font_size)

        max_plot_y = color_y + director_h + writer_h
        available_space = self.height - max_plot_y - margin - release_h
        lines, plot_line_height = self.wrap_text(self.plot, right_side_width, plot_font)
        plot_height = len(lines) * plot_line_height

        center_of_available_space = (available_space - plot_height) // 2
        self.justified_text_box((right_side_x, max_plot_y + center_of_available_space), self.plot, right_side_width, plot_font)

class ModifiedClassicult(Poster):
    @property
    def margin_ratio(self):
        return .05 # .1/1.2
    def create_poster(self):
        draw = self.draw
        poster = self.poster
        margin = self.margin
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
        director_font = self.font_fill_area(d_text, left_side_width, 'fonts/Sequel/Sequel100Black-85.ttf')
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
            writer_font = self.font_fill_area(w_text, (self.size - margin) // 3, 'fonts/Gidole-Regular.ttf')
        else:
            writer_font = self.font_fill_area(w_text, left_side_width, 'fonts/Gidole-Regular.ttf')
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


class TheFilmPlanet(Poster):
    @property
    def margin_ratio(self):
        return .05 # .1/1.2
    def create_poster(self):
        draw = self.draw
        poster = self.poster
        margin = self.margin
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
        director_font = self.font_fill_area(d_text, left_side_width, 'fonts/Sequel/Sequel100Black-85.ttf')
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
            writer_font = self.font_fill_area(w_text, (self.size - margin) // 3, 'fonts/Gidole-Regular.ttf')
        else:
            writer_font = self.font_fill_area(w_text, left_side_width, 'fonts/Gidole-Regular.ttf')
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

