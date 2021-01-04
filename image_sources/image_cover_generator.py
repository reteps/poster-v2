from io import BytesIO
from image_sources.windows_image import image_open, CustomImage, show_file, hide_file
from PIL import ImageShow, ImageFile, ImageFont, ImageDraw, Image
import subprocess
import time
import os
import math
import progressbar
from abc import ABC, abstractmethod
from tempfile import NamedTemporaryFile

class ImageCoverGenerator(ABC): # abstract class
    def __init__(
        self,
        min_width=1000,
        min_height=1000,
        temp_img_name='temp_image.png' # tmp is bad
    ):
        self.min_height = min_height
        self.min_width = min_width
        self.temp_img_name = temp_img_name
    @staticmethod
    def _merge_and_markup_images(image_list):
        def _chunk(l, n):
            for i in range(0, len(l), n):  # Step over in chunks
                yield l[i : i + n]

        images_per_row = math.ceil(
            math.sqrt(len(list(filter(lambda x: x["img"] != None, image_list))))
        )
        if images_per_row == 0:
            raise ValueError('No valid images')
        font = ImageFont.truetype("/mnt/c/Windows/Fonts/micross.ttf", 100)
        font2 = ImageFont.truetype("/mnt/c/Windows/Fonts/micross.ttf", 50)
        rows = list(_chunk(image_list, images_per_row))
        total_height = 0
        longest_row = 0
        for row in rows:
            widths, heights = zip(*(i["current_size"] for i in row))
            total_width = sum(widths)
            max_height = max(heights)
            if total_width > longest_row:
                longest_row = total_width
            total_height += max_height
        new_img = Image.new("RGB", (longest_row, total_height))
        draw = ImageDraw.Draw(new_img)
        y_offset = 0
        for i, row in enumerate(rows):
            widths, heights = zip(*(i["current_size"] for i in row))
            total_width = sum(widths)
            max_height = max(heights)
            x_offset = 0
            for j, img in enumerate(row):
                if img["img"] == None:
                    continue
                try:
                    new_img.paste(img["img"], (x_offset, y_offset))
                    index = str(i * images_per_row + j + 1)
                    w, h = font.getsize(index)

                    size = f'{img["original_size"]}'
                    w2, h2 = font2.getsize(size)
                    draw.rectangle(
                        (x_offset, y_offset, x_offset + w, y_offset + h), fill="white"
                    )
                    draw.text((x_offset, y_offset), f"{index}", (0, 0, 0), font=font)

                    y_offset_2 = y_offset + img["current_size"][1] - 50
                    draw.rectangle(
                        (x_offset, y_offset_2, x_offset + w2, y_offset_2 + h2),
                        fill="white",
                    )
                    draw.text(
                        (x_offset, y_offset_2),
                        f'{img["original_size"]}',
                        (0, 0, 0),
                        font=font2,
                    )
                    x_offset += img["current_size"][0]
                except OSError:
                    print("Could not paste image", i + 1)
                    pass
            y_offset += max_height
        new_img.thumbnail((4000, 4000), Image.ANTIALIAS)
        return CustomImage(new_img)


    @abstractmethod
    def _search(self, keyword):
        pass
    def _processed_image(self, img):

        b = BytesIO()
        b.seek(0)  # go to adddress 0
        img.copy_to(b)
        b.seek(0)
        try:
            temp_img = image_open(b)
        except Exception as e:
            return None
        if temp_img.size[0] < self.min_height or temp_img.size[1] < self.min_width:
            return None
        return temp_img

    def _processed_image_wrapper(self, img, resize=True):
        temp_img = self._processed_image(img)
        if temp_img == None:
            return {"img": None, "original_size": [0, 0], "current_size": [0, 0]}
        if not resize:
            temp_img.thumbnail((4000, 4000), Image.ANTIALIAS)
        original_size = temp_img.size
        if resize:
            temp_img.thumbnail((10000, self.min_height), Image.ANTIALIAS)
        return {
            "img": temp_img,
            "original_size": original_size,
            "current_size": temp_img.size,
        }
    @abstractmethod
    def display_data(i, obj):
        pass
    def get_cover(self, keyword, pause=True, data=True,num=None):
        results = self._search(keyword)
        valid_images = []
        search_objs = []
        for i in progressbar.progressbar(range(len(results)), redirect_stdout=data):
            if num != None and num != i-1:
                continue
            if data:
                if num == None:
                    self.display_data(i, results[i])
                search_objs.append(results[i])  
            valid_images.append(self._processed_image_wrapper(results[i]))

                
        if num != None:
            results = [results[num-1]]
        num = 0
        if len(valid_images) != 1:
            merged_image = self._merge_and_markup_images(valid_images)
            merged_image.show()
            while True:
                num = int(input("Select Image Number > ")) - 1
                if num >= len(results) or num < 0:
                    print('[INVALID IMAGE NUMBER]')
                    continue
                break
            merged_image.hide()
        selected_image = self._processed_image_wrapper(results[num], resize=False)[
            "img"
        ]
        if pause:
            selected_image.save(self.temp_img_name)
            show_file(self.temp_img_name)
            input("[ENTER]")
            selected_image = CustomImage(Image.open(self.temp_img_name))
            hide_file()
        if data:
            return selected_image, search_objs[num]
        return selected_image

    def get_covers(self, keyword, pause=True, data=True,nums =None):
        results = self._search(keyword)
        valid_images = []
        search_objs = []
        for i in progressbar.progressbar(range(len(results)), redirect_stdout=data):
            if nums != None and i-1 not in nums:
                continue
            if data:
                if nums == None:
                    self.display_data(i, results[i])
                search_objs.append(results[i])  
            valid_images.append(self._processed_image_wrapper(results[i]))

                
        
        if nums != None:
            results = [results[n - 1] for n in nums]
            nums = [i for i in range(len(nums))]
        else:
            nums = []
            merged_image = self._merge_and_markup_images(valid_images)
            merged_image.show()
            while True:
                num =input("Select Image Number > ")
                if num.isdigit():
                    num = int(num) - 1
                else:
                    break
                if num >= len(results) or num < 0:
                    print('[INVALID IMAGE NUMBER]')
                    continue
                nums.append(num)
            merged_image.hide()
        selected_images = [self._processed_image_wrapper(results[num], resize=False)[
            "img"
        ] for num in nums ]
        print(len(selected_images))
        for i in range(len(selected_images)):
            temporary_file = NamedTemporaryFile(mode='w+b', suffix='.png')
            print(temporary_file.name)
            if pause:
                selected_images[i].save(temporary_file)
                show_file(temporary_file.name)
                input("[ENTER]")
                selected_images[i] = CustomImage(Image.open(temporary_file.name))
                hide_file()
        if data:
            return selected_images, [search_objs[num] for num in nums]
        return selected_images