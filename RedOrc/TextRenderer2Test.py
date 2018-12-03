import numpy as np
from time import clock
from TextRenderer2 import *
from TextGenerator import GetRandomText

def Test():
    tr1 = TextRenderer2()
    tr2 = TextRenderer2()
    
    imageProps1 = ImageProperties(512, 512, 96, WicGuid.WicPixelFormat96bppRGBFloat())
    tr1.SetImageProperties(imageProps1)

    imageProps2 = ImageProperties(1024, 1024, 32, WicGuid.WicPixelFormat32bppRGBA())
    tr2.SetImageProperties(imageProps2)
    
    textProps1= TextProperties("Gabriola", FontWeight.Normal, FontStretch.Normal, FontStyle.Normal, 0, 56)
    fontExists1 = tr1.SetTextProperties(textProps1)

    textProps2= TextProperties("Edwardian Script ITC", FontWeight.Bold, FontStretch.Normal, FontStyle.Normal, 0, 72)
    fontExists2 = tr2.SetTextProperties(textProps2)
    
    textBounds1 = D2D1_RECT_F(20, 20, imageProps1.imageHeight - 20, imageProps1.imageWidth - 20)
    abc = "abcdefghijklmnopqrstuvwxyz"
    textInfo1 = tr1.GetRenderedTextInformation(abc + abc.upper(), textBounds1)
    textInfo1.maxGlyphsPerLine = int(textInfo1.maxGlyphsPerLine * 1.5)

    textBounds2 = D2D1_RECT_F(20, 20, imageProps2.imageHeight - 20, imageProps2.imageWidth - 20)
    abc = "abcdefghijklmnopqrstuvwxyz"
    textInfo2 = tr2.GetRenderedTextInformation(abc + abc.upper(), textBounds2)
    textInfo2.maxGlyphsPerLine = int(textInfo2.maxGlyphsPerLine * 1.5)
    
    imageBuffer1 = np.zeros(shape=(imageProps1.imageHeight, imageProps1.imageWidth, 3), dtype=np.float32)
    imageBuffer2 = np.zeros(shape=(imageProps2.imageHeight, imageProps2.imageWidth, 3), dtype=np.float32)
    
    iterCount = 1
    startTime = clock()
    for i in range(iterCount):
        textToDraw = GetRandomText(textInfo1, abc * 6 + abc.upper() + " " * 26 + "\n" * 1);
        boundingBoxes = tr1.RenderString(textToDraw, textBounds1, True, True, imageBuffer1.ctypes.data_as(ctypes.c_void_p))
        tr1.RenderRectangles(boundingBoxes, imageBuffer1.ctypes.data_as(ctypes.c_void_p))
        
        textToDraw = GetRandomText(textInfo2, abc * 6 + abc.upper() + " " * 26 + "\n" * 1);
        boundingBoxes = tr2.RenderString(textToDraw, textBounds2, True, True, imageBuffer2.ctypes.data_as(ctypes.c_void_p))
        tr2.RenderRectangles(boundingBoxes, imageBuffer2.ctypes.data_as(ctypes.c_void_p))
    endTime = clock()
    
    #tr1.SaveImageAsPng("TestRender1.png", imageBuffer1.ctypes.data_as(ctypes.c_void_p))
    #tr2.SaveImageAsPng("TestRender2.png", imageBuffer2.ctypes.data_as(ctypes.c_void_p))

    tr1.Destroy()
    tr2.Destroy()
    
    #print("Average time:", (endTime - startTime) / iterCount * 1000, "[ms]")

for i in range(100000):
    Test()
    print("Iter:", i, end="    \r")