import sys, ctypes
import PIL
import platform, subprocess, os
if sys.platform == 'win32':
    import ctypes

    if _PILLOW_INSTALLED:
        from PIL import ImageGrab

    # Makes this process aware of monitor scaling so the screenshots are correctly sized:
    try:
       ctypes.windll.user32.SetProcessDPIAware()
    except AttributeError:
        pass # Windows XP doesn't support this, so just do nothing.

    dc = ctypes.windll.user32.GetDC(0)

    class POINT(ctypes.Structure):
        _fields_ = [('x', ctypes.c_long),
                    ('y', ctypes.c_long)]

    def _winPosition():
        cursor = POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(cursor))
        return (cursor.x, cursor.y)
    position = _winPosition


    def _winScreenshot(filename=None):
        # TODO - Use the winapi to get a screenshot, and compare performance with ImageGrab.grab()
        # https://stackoverflow.com/a/3586280/1893164
        try:
            im = ImageGrab.grab()
            if filename is not None:
                im.save(filename)
        except NameError:
            raise ImportError('Pillow module must be installed to use screenshot functions on Windows.')
        return im
    screenshot = _winScreenshot

    def _winSize():
        return (ctypes.windll.user32.GetSystemMetrics(0), ctypes.windll.user32.GetSystemMetrics(1))
    size = _winSize

    def _winGetPixel(x, y):
        colorRef = ctypes.windll.gdi32.GetPixel(dc, x, y)  # A COLORREF value as 0x00bbggrr. See https://docs.microsoft.com/en-us/windows/win32/gdi/colorref
        red = colorRef % 256
        colorRef //= 256
        green = colorRef % 256
        colorRef //= 256
        blue = colorRef

        return (red, green, blue)
    getPixel = _winGetPixel


elif platform.system() == 'Linux':
    from Xlib.display import Display
    import errno

    scrotExists = False
    try:
            whichProc = subprocess.Popen(
                ['which', 'scrot'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            scrotExists = whichProc.wait() == 0
    except OSError as ex:
        if ex.errno == errno.ENOENT:
            # if there is no "which" program to find scrot, then assume there
            # is no scrot.
            pass
        else:
            raise

    _display = Display(os.environ['DISPLAY'])

    def _linuxPosition():
        coord = _display.screen().root.query_pointer()._data
        return coord["root_x"], coord["root_y"]
    position = _linuxPosition

    def _linuxScreenshot(filename=None):
        if not scrotExists:
            raise NotImplementedError('"scrot" must be installed to use screenshot functions in Linux. Run: sudo apt-get install scrot')

        if filename is not None:
            tmpFilename = filename
        else:
            tmpFilename = '.screenshot%s.png' % (datetime.datetime.now().strftime('%Y-%m%d_%H-%M-%S-%f'))

        if scrotExists:
            subprocess.call(['scrot', '-z', tmpFilename])
            im = Image.open(tmpFilename)

            # force loading before unlinking, Image.open() is lazy
            im.load()

            if filename is None:
                os.unlink(tmpFilename)
            return im
        else:
            raise Exception('The scrot program must be installed to take a screenshot with PyScreeze on Linux. Run: sudo apt-get install scrot')
    screenshot = _linuxScreenshot

    def _linuxSize():
        return _display.screen().width_in_pixels, _display.screen().height_in_pixels
    size = _linuxSize

    def _linuxGetPixel(x, y):
        rgbValue = screenshot().getpixel((x, y))
        return rgbValue[0], rgbValue[1], rgbValue[2]
    getPixel = _linuxGetPixel