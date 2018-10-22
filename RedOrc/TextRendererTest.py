from PIL import Image
import numpy as np
from TextRenderer import *
from time import clock

renderer = TextRenderer()

imageProps = ImageProperties(500, 500, 32, WicGuid.WicPixelFormat32bppRGBA())
renderer.SetImageProperties(imageProps)

textProps = TextProperties("Gabriola", FontWeight.Normal, FontStretch.Normal, FontStyle.Normal, 0, 32)
fontExists = renderer.SetTextProperties(textProps)

textBounds = D2D1_RECT_F(20, 20, imageProps.imageHeight - 20, imageProps.imageWidth - 20)
imageBuffer = np.ndarray(shape=(imageProps.imageHeight * imageProps.imageWidth,), dtype=np.int32)

iterCount = 1
startTime = clock()
for i in range(iterCount):
    boundingBoxes = renderer.RenderString("This is a longer paragraph. It is written here to test the performance of string rendering. By adding more glyphs, the rendering and analasis becomes more complex, leading to maximum stress.", textBounds, True, False, imageBuffer.ctypes.data_as(ctypes.c_void_p))
endTime = clock()

print("Average time:", (endTime - startTime) / iterCount * 1000, "[ms]")

renderer.Uninitialize()

pilImage = Image.frombuffer("RGBA", (imageProps.imageWidth, imageProps.imageHeight), imageBuffer.tobytes(), "raw", "RGBA", 0, 1)
pilImage.save("TestRender.png")