import ctypes

class WicGuid(ctypes.Structure):
    _fields_ = \
    [
        ("data1", ctypes.c_ulong),
        ("data2", ctypes.c_ushort),
        ("data3", ctypes.c_ushort),
        ("data4", ctypes.c_char * 8)
    ]
    
    def __init__(self, d1, d2, d3, d41, d42, d43, d44, d45, d46, d47, d48):
        self.data1 = d1
        self.data2 = d2
        self.data3 = d3
        self.data4 = bytes([d41, d42, d43, d44, d45, d46, d47, d48])

    @staticmethod
    def WicPixelFormat32bppRGBA():
        return WicGuid(0xf5c7ad2d, 0x6a8d, 0x43dd, 0xa7, 0xa8, 0xa2, 0x99, 0x35, 0x26, 0x1a, 0xe9)

    @staticmethod
    def WicPixelFormat32bppRGB():
        return WicGuid(0xd98c6b95, 0x3efe, 0x47d6, 0xbb, 0x25, 0xeb, 0x17, 0x48, 0xab, 0x0c, 0xf1)

    @staticmethod
    def WicPixelFormat8bppGray():
        return WicGuid(0x6fddc324, 0x4e03, 0x4bfe, 0xb1, 0x85, 0x3d, 0x77, 0x76, 0x8d, 0xc9, 0x08)

    @staticmethod
    def WicPixelFormat96bppRGBFloat():
        return WicGuid(0xe3fed78f, 0xe8db, 0x4acf, 0x84, 0xc1, 0xe9, 0x7f, 0x61, 0x36, 0xb3, 0x27)

class ImageProperties(ctypes.Structure):
    _fields_ = \
    [
        ("imageHeight", ctypes.c_int),
        ("imageWidth", ctypes.c_int),
        ("bitsPerPixel", ctypes.c_int),
        ("wicPixelFormat", WicGuid)
    ]

    def __init__(self, imageHeight, imageWidth, bitsPerPixel, wicPixelFormat):
        self.imageHeight = imageHeight
        self.imageWidth = imageWidth
        self.bitsPerPixel = bitsPerPixel
        self.wicPixelFormat = wicPixelFormat

class FontWeight:
    Thin = 100,
    ExtraLight = 200,
    UltraLight = 200,
    Light = 300,
    SemiLight = 350,
    Normal = 400,
    Regular = 400,
    Medium = 500,
    DemiBold = 600,
    SemiBold = 600,
    Bold = 700,
    ExtraBold = 800,
    UltraBold = 800,
    Black = 900,
    Heavy = 900,
    ExtraBlack = 950,
    UltraBlack = 950

class FontStretch:
    Undefined = 0
    UltraCondensed = 1
    ExtraCondensed = 2
    Condensed = 3
    SemiCondensed = 4
    Normal = 5
    Medium = 5
    SemiExpanded = 6
    Expanded = 7
    ExtraExpanded = 8
    UltraExpanded = 9

class FontStyle:
    Normal = 0
    Oblique = 1
    Italic = 2

class TextProperties(ctypes.Structure):
    _fields_ = \
    [
        ("fontName", ctypes.c_wchar_p),
        ("fontWeight", ctypes.c_int),
        ("fontStretch", ctypes.c_int),
        ("fontStyle", ctypes.c_int),
        ("fontBidiLevel", ctypes.c_int),
        ("fontEmSize", ctypes.c_float)
    ]

    def __init__(self, fontName, fontWeight, fontStretch, fontStyle, fontBidiLevel, fontEmSize):
        self.fontName = fontName
        self.fontWeight, = fontWeight
        self.fontStretch = fontStretch
        self.fontStyle = fontStyle
        self.fontBidiLevel = fontBidiLevel
        self.fontEmSize = fontEmSize

class D2D1_RECT_F(ctypes.Structure):
    _fields_ = \
    [
        ("left", ctypes.c_float),
        ("top", ctypes.c_float),
        ("right", ctypes.c_float),
        ("bottom", ctypes.c_float)
    ]

    def __init__(self, left, top, right, bottom):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def __repr__(self):
        return "{ " + str(self.left) + ", " + str(self.top) + ", " + str(self.right) + ", " + str(self.bottom) + " }"

    def __str__(self):
        return self.__repr__()

class RenderedTextInformation(ctypes.Structure):
    _fields_ = \
    [
        ("maxGlyphsPerLine", ctypes.c_int),
        ("maxLines", ctypes.c_int),
    ]
    
    def __init__(self):
        self.maxGlyphsPerLine = 0
        self.maxLines = 0

class TextRenderer(object):
    _lib = ctypes.cdll.LoadLibrary("TextRenderer.dll")
    
    _initialize = _lib.Initialize
    _initialize.argtypes = []
    _initialize.restype = ctypes.c_int
    
    _set_image_properties = _lib.SetImageProperties
    _set_image_properties.argtypes = [ctypes.POINTER(ImageProperties)]
    _set_image_properties.restype = ctypes.c_int
    
    _set_text_properties = _lib.SetTextProperties
    _set_text_properties.argtypes = [ctypes.POINTER(TextProperties), ctypes.POINTER(ctypes.c_bool)]
    _set_text_properties.restype = ctypes.c_int

    _get_rendered_text_information = _lib.GetRenderedTextInformation
    _get_rendered_text_information.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(D2D1_RECT_F), ctypes.POINTER(RenderedTextInformation)]
    _get_rendered_text_information.restype = ctypes.c_int
    
    _render_string = _lib.RenderString
    _render_string.argtypes = [ctypes.c_wchar_p, ctypes.c_int, ctypes.POINTER(D2D1_RECT_F), ctypes.c_bool, ctypes.c_bool, ctypes.c_void_p, ctypes.POINTER(ctypes.POINTER(D2D1_RECT_F)), ctypes.POINTER(ctypes.c_int)]
    _render_string.restype = ctypes.c_int

    _render_rectangles = _lib.RenderRectangles
    _render_rectangles.argtypes = [ctypes.POINTER(D2D1_RECT_F), ctypes.c_int, ctypes.c_void_p]
    _render_rectangles.restype = ctypes.c_int
    
    _save_image_as_png = _lib.SaveImageAsPng
    _save_image_as_png.argtypes = [ctypes.c_wchar_p, ctypes.c_void_p]
    _save_image_as_png.restype = ctypes.c_int

    _delete_array = _lib.DeleteArray
    _delete_array.argtypes = [ctypes.c_void_p]
    _delete_array.restype = None
    
    _uninitialize = _lib.Uninitialize
    _uninitialize.argtypes = None
    _uninitialize.restype = None

    @staticmethod
    def Initialize():
        hr = TextRenderer._initialize()
        if hr < 0:
            raise RuntimeError("Initialize failed with code: " + str(hr))
    
    @staticmethod
    def SetImageProperties(imageProps):
        hr = TextRenderer._set_image_properties(ctypes.byref(imageProps))
        if hr < 0:
            raise RuntimeError("SetImageProperties failed with code: " + str(hr))
    
    @staticmethod
    def SetTextProperties(textProps):
        outFontExists = ctypes.c_bool(False)
        hr = TextRenderer._set_text_properties(ctypes.byref(textProps), ctypes.byref(outFontExists))
        if hr < 0:
            raise RuntimeError("SetTextProperties failed with code: " + str(hr))
        
        return outFontExists

    @staticmethod
    def GetRenderedTextInformation(charSet, textBounds):
        outTextInfo = RenderedTextInformation()
        hr = TextRenderer._get_rendered_text_information(charSet, ctypes.byref(textBounds), ctypes.byref(outTextInfo))
        if hr < 0:
            raise RuntimeError("GetRenderedTextInformation failed with code: " + str(hr))
        
        return outTextInfo

    @staticmethod
    def RenderString(string, textBounds, clearBackground, drawBoundingBoxes, imageBuffer):
        boundingBoxesPtr = ctypes.POINTER(D2D1_RECT_F)()
        boundingBoxesCount = ctypes.c_int()
        
        hr = TextRenderer._render_string(string, len(string), ctypes.byref(textBounds), clearBackground, drawBoundingBoxes, imageBuffer, ctypes.byref(boundingBoxesPtr), ctypes.byref(boundingBoxesCount))
        if hr < 0:
            raise RuntimeError("RenderString failed with code: " + str(hr))

        boundingBoxes = []
        for i in range(boundingBoxesCount.value):
            rect = boundingBoxesPtr[i]
            boundingBoxes.append(D2D1_RECT_F(rect.left, rect.top, rect.right, rect.bottom))

        TextRenderer._delete_array(boundingBoxesPtr)

        return boundingBoxes

    @staticmethod
    def RenderRectangles(rectangles, imageBuffer):
        rects = (D2D1_RECT_F * len(rectangles))(*rectangles)
        hr = TextRenderer._render_rectangles(ctypes.cast(rects, ctypes.POINTER(D2D1_RECT_F)), len(rectangles), imageBuffer)
        if hr < 0:
            raise RuntimeError("RenderRectangles failed with code: " + str(hr))

    @staticmethod
    def SaveImageAsPng(imageName, imageBuffer):
        hr = TextRenderer._save_image_as_png(imageName, imageBuffer)
        if hr < 0:
            raise RuntimeError("SaveImageAsPng failed with code: " + str(hr))

    @staticmethod
    def Uninitialize():
        TextRenderer._uninitialize()
