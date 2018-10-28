from PIL import Image
import numpy as np
from time import clock
from TextRenderer import *
from TextGenerator import GetRandomText

TextRenderer.Initialize()

imageProps = ImageProperties(500, 500, 96, WicGuid.WicPixelFormat96bppRGBFloat())
TextRenderer.SetImageProperties(imageProps)

textProps = TextProperties("Gabriola", FontWeight.Normal, FontStretch.Normal, FontStyle.Normal, 0, 56)
fontExists = TextRenderer.SetTextProperties(textProps)

textBounds = D2D1_RECT_F(20, 20, imageProps.imageHeight - 20, imageProps.imageWidth - 20)
abc = "abcdefghijklmnopqrstuvwxyz"
textInfo = TextRenderer.GetRenderedTextInformation(abc + abc.upper(), textBounds)
textInfo.maxGlyphsPerLine = int(textInfo.maxGlyphsPerLine * 1.5)
textToDraw = GetRandomText(textInfo, abc * 6 + abc.upper() + " " * 26 + "\n" * 1);

imageBuffer = np.zeros(shape=(imageProps.imageHeight, imageProps.imageWidth, 3), dtype=np.float32)

iterCount = 1
startTime = clock()
for i in range(iterCount):
    boundingBoxes = TextRenderer.RenderString(textToDraw, textBounds, True, False, imageBuffer.ctypes.data_as(ctypes.c_void_p))
    TextRenderer.RenderRectangles(boundingBoxes, imageBuffer.ctypes.data_as(ctypes.c_void_p))
TextRenderer.SaveImageAsPng("TestRender.png", imageBuffer.ctypes.data_as(ctypes.c_void_p))
endTime = clock()

print("Average time:", (endTime - startTime) / iterCount * 1000, "[ms]")

TextRenderer.Uninitialize()