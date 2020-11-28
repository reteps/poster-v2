import subprocess, os
from PIL import ImageShow, Image
import pathlib
def custom_show_file(filename, **options):
    if '/mnt/' in filename:
        to_wsl = filename.replace('/mnt/c','c:').replace('/','\\')
    else:
        to_wsl = r'\\\wsl$\Ubuntu' + filename.replace('/', '\\')
    command = f'/mnt/c/windows/System32/cmd.exe /c start "" "{to_wsl}"'
    null = open(os.devnull, "w")
    subprocess.Popen(
        command,
        shell=True,
        stdout=null,
        stderr=null
    )
    return 1
def show_file(filename):
    path = pathlib.Path().absolute() / filename
    custom_show_file(str(path))
def hide_file():
    null = open(os.devnull, "w")
    subprocess.Popen(
        'cmd.exe /c taskkill /f /im "Microsoft.Photos.exe"',
        shell=True,
        stderr=null,
        stdout=null,
    )
def image_open(*args, **kwargs):
    p_img = Image.open(*args, **kwargs)
    return CustomImage(p_img)


class PreviewViewer(ImageShow.UnixViewer):
    format = 'PNG'
    options = {"compress_level": 1}
    
    def show_file(self, filename, **options):
        return custom_show_file(filename, **options)

class CustomImage():
    def __init__(self, img):
        self._img = img
    def __getattr__(self, key):
        if key == '_img':
            raise AttributeError()
        return getattr(self._img, key)
    def hide(self):
        hide_file()

ImageShow.register(PreviewViewer, order=-1)