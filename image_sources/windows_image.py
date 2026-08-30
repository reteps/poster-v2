import subprocess, os, sys, platform
from PIL import ImageShow, Image, ImageDraw, ImageFont
import pathlib

# Pillow >= 10 removed ImageDraw.textsize()/ImageFont.getsize(); patch
# compatible shims back in since this project's poster renderers still use
# the old APIs extensively.
if not hasattr(ImageDraw.ImageDraw, "textsize"):
    def _textsize(self, text, font=None, *args, **kwargs):
        font = font or self.getfont()
        left, top, right, bottom = self.textbbox((0, 0), text, font=font)
        return right - left, bottom - top
    ImageDraw.ImageDraw.textsize = _textsize

if not hasattr(ImageFont.FreeTypeFont, "getsize"):
    def _getsize(self, text, *args, **kwargs):
        left, top, right, bottom = self.getbbox(text)
        return right - left, bottom - top
    ImageFont.FreeTypeFont.getsize = _getsize

IS_MACOS = platform.system() == "Darwin"
IS_WSL = "microsoft" in platform.uname().release.lower() if hasattr(platform.uname(), "release") else False

def custom_show_file(filename, **options):
    null = open(os.devnull, "w")
    if IS_MACOS:
        subprocess.Popen(["open", filename], stdout=null, stderr=null)
        return 1
    if '/mnt/' in filename:
        to_wsl = filename.replace('/mnt/c','c:').replace('/','\\')
    else:
        to_wsl = r'\\\wsl$\Ubuntu' + filename.replace('/', '\\')
    command = f'/mnt/c/windows/System32/cmd.exe /c start "" "{to_wsl}"'
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
    if IS_MACOS:
        return
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

    def get_command_ex(self, file, **options):
        # Newer Pillow versions require this abstract method; the actual
        # display is handled entirely by show_file/custom_show_file above.
        return ("", "")

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