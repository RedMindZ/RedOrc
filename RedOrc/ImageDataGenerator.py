import numpy as np
from TextRenderer import *
from TextGenerator import *

# Assumes that TextRenderer is already initialized
class ImageDataGenerator:

    _image_props = ImageProperties(128, 128, 96, WicGuid.WicPixelFormat96bppRGBFloat())
    _text_props = TextProperties("Arial", FontWeight.Normal, FontStretch.Normal, FontStyle.Normal, 0, 24)
    _text_bounds = D2D1_RECT_F(20, 20, 108, 108)
    _text_pool = "abcdefghijklmopqrstuvwxyz" + "ABCDEFGHIJKLMOPQRSTUVWXYZ"

    _image_shape = None
    _label_shape = None
    _loss_weights = None

    @staticmethod
    def Initialize():
        TextRenderer.Initialize()

    @staticmethod
    def SetImageProperties(imageProps):
        ImageDataGenerator._image_props = imageProps
        TextRenderer.SetImageProperties(ImageDataGenerator._image_props)
        
        ImageDataGenerator._image_shape = (ImageDataGenerator._image_props.imageHeight, ImageDataGenerator._image_props.imageWidth, 3)
        ImageDataGenerator._label_shape = (ImageDataGenerator._image_props.imageHeight, ImageDataGenerator._image_props.imageWidth, 3)

        ImageDataGenerator._loss_weights = np.ndarray(shape=ImageDataGenerator._label_shape)
        ImageDataGenerator._loss_weights[:, :, 0] = 100
        ImageDataGenerator._loss_weights[:, :, 1:] = 1

    @staticmethod
    def SetTextProperties(textProps):
        ImageDataGenerator._text_props = textProps
        TextRenderer.SetTextProperties(ImageDataGenerator._text_props)

    @staticmethod
    def SetTextBounds(textBounds):
        ImageDataGenerator._text_bounds = textBounds

    @staticmethod
    def SetTextPool(textPool):
        ImageDataGenerator._text_pool = textPool

    @staticmethod
    def SetFontFace(fontName):
        ImageDataGenerator._text_props.fontName = fontName
        TextRenderer.SetTextProperties(ImageDataGenerator._text_props)

    @staticmethod
    def SetFontWeight(weight):
        ImageDataGenerator._text_props.fontWeight = weight
        TextRenderer.SetTextProperties(ImageDataGenerator._text_props)

    @staticmethod
    def SetFontStretch(stretch):
        ImageDataGenerator._text_props.fontStretch = stretch
        TextRenderer.SetTextProperties(ImageDataGenerator._text_props)

    @staticmethod
    def SetFontStyle(style):
        ImageDataGenerator._text_props.fontStyle = style
        TextRenderer.SetTextProperties(ImageDataGenerator._text_props)

    @staticmethod
    def SetFontEmSize(emSize):
        ImageDataGenerator._text_props.fontEmSize = emSize
        TextRenderer.SetTextProperties(ImageDataGenerator._text_props)

    def __iter__(self):
        return self

    def __next__(self):
        textInfo = TextRenderer.GetRenderedTextInformation(ImageDataGenerator._text_pool, ImageDataGenerator._text_bounds)
        text = GetRandomText(textInfo, ImageDataGenerator._text_pool)
        imageBuffer = np.zeros(shape=ImageDataGenerator._image_shape, dtype=np.float32)
        boundingBoxes = TextRenderer.RenderString(text, ImageDataGenerator._text_bounds, True, False, imageBuffer.ctypes.data_as(ctypes.c_void_p))

        label = np.zeros(shape=ImageDataGenerator._label_shape, dtype=np.float)
        for rect in boundingBoxes:
            i, j = round(rect.top), round(rect.left)
            label[i, j, 0] = 1                             # Confidence
            label[i, j, 1] = abs(rect.bottom - rect.top)   # Height
            label[i, j, 2] = abs(rect.right - rect.left)   # Width

        return (imageBuffer, label, ImageDataGenerator._loss_weights)

    def Uninitialize(self):
        TextRenderer.Uninitialize()
